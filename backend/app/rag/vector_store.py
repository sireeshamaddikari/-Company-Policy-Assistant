"""FAISS-backed vector store.

Implements the ``VectorStore`` protocol. Stores chunk embeddings in a FAISS
index and keeps a side-car id-map (FAISS int id -> {document_id, chunk_index,
text}) so search results can be traced back to their source document for
citations.

Design notes:
  * Embeddings are L2-normalized upstream, so an inner-product index
    (``IndexFlatIP``) yields cosine similarity.
  * The index is wrapped in ``IndexIDMap2`` so vectors carry explicit ids and
    a document's vectors can be removed later (used by deletion, future step).
  * The index dimension is discovered lazily from the first batch added, then
    persisted, so the store doesn't need a handle to the embedder.
  * A lock guards mutation/persistence because FastAPI serves sync endpoints
    from a threadpool and uploads may overlap.
"""

import json
import logging
import threading
from pathlib import Path

import faiss
import numpy as np

from app.rag.interfaces import SearchResult
from app.utils.files import ensure_dir

logger = logging.getLogger(__name__)


class FaissVectorStore:
    """Persistent FAISS vector store with a document-aware id-map."""

    def __init__(self, store_dir: str) -> None:
        self._dir = ensure_dir(store_dir)
        self._index_path = self._dir / "faiss.index"
        self._meta_path = self._dir / "store_meta.json"

        self._lock = threading.Lock()
        self._index: faiss.Index | None = None
        self._dim: int | None = None
        self._next_id: int = 0
        # FAISS int id -> chunk metadata.
        self._id_map: dict[int, dict] = {}

        self._load()

    # -- persistence ---------------------------------------------------------

    def _load(self) -> None:
        """Load an existing index + id-map from disk, if present."""
        if self._index_path.exists() and self._meta_path.exists():
            self._index = faiss.read_index(str(self._index_path))
            meta = json.loads(self._meta_path.read_text(encoding="utf-8"))
            self._dim = meta["dim"]
            self._next_id = meta["next_id"]
            self._id_map = {int(k): v for k, v in meta["id_map"].items()}
            logger.info(
                "Loaded FAISS index: dim=%s, vectors=%d",
                self._dim,
                len(self._id_map),
            )
        else:
            logger.info("No existing FAISS index found; starting empty.")

    def persist(self) -> None:
        """Flush the index and id-map to disk atomically-ish."""
        with self._lock:
            self._persist_unlocked()

    def _persist_unlocked(self) -> None:
        if self._index is None:
            return
        faiss.write_index(self._index, str(self._index_path))
        meta = {
            "dim": self._dim,
            "next_id": self._next_id,
            "id_map": {str(k): v for k, v in self._id_map.items()},
        }
        self._meta_path.write_text(json.dumps(meta), encoding="utf-8")
        logger.debug("Persisted FAISS index (%d vectors)", len(self._id_map))

    # -- mutation ------------------------------------------------------------

    def _ensure_index(self, dim: int) -> None:
        if self._index is None:
            self._dim = dim
            self._index = faiss.IndexIDMap2(faiss.IndexFlatIP(dim))
            logger.info("Initialized FAISS index (dim=%d)", dim)
        elif self._dim != dim:
            raise ValueError(
                f"Embedding dim {dim} does not match index dim {self._dim}"
            )

    def add(
        self,
        document_id: str,
        embeddings: list[list[float]],
        texts: list[str],
    ) -> None:
        """Index the chunk embeddings for a document."""
        if not embeddings:
            return
        if len(embeddings) != len(texts):
            raise ValueError("embeddings and texts must have equal length")

        vectors = np.asarray(embeddings, dtype="float32")
        with self._lock:
            self._ensure_index(vectors.shape[1])
            ids = np.arange(
                self._next_id, self._next_id + len(embeddings), dtype="int64"
            )
            self._index.add_with_ids(vectors, ids)
            for offset, faiss_id in enumerate(ids.tolist()):
                self._id_map[faiss_id] = {
                    "document_id": document_id,
                    "chunk_index": offset,
                    "text": texts[offset],
                }
            self._next_id += len(embeddings)
            logger.info(
                "Added %d vectors for document %s (total=%d)",
                len(embeddings),
                document_id,
                len(self._id_map),
            )

    def delete(self, document_id: str) -> None:
        """Remove all vectors belonging to a document."""
        with self._lock:
            if self._index is None:
                return
            target_ids = [
                fid
                for fid, meta in self._id_map.items()
                if meta["document_id"] == document_id
            ]
            if not target_ids:
                return
            self._index.remove_ids(np.asarray(target_ids, dtype="int64"))
            for fid in target_ids:
                del self._id_map[fid]
            logger.info(
                "Removed %d vectors for document %s", len(target_ids), document_id
            )

    # -- query ---------------------------------------------------------------

    def search(self, query_embedding: list[float], k: int) -> list[SearchResult]:
        """Return the top-k most similar chunks."""
        with self._lock:
            if self._index is None or self._index.ntotal == 0:
                return []
            query = np.asarray([query_embedding], dtype="float32")
            scores, ids = self._index.search(query, min(k, self._index.ntotal))

        results: list[SearchResult] = []
        for faiss_id, score in zip(ids[0].tolist(), scores[0].tolist()):
            if faiss_id == -1:
                continue
            meta = self._id_map.get(faiss_id)
            if meta is None:
                continue
            results.append(
                SearchResult(
                    document_id=meta["document_id"],
                    chunk_index=meta["chunk_index"],
                    text=meta["text"],
                    score=float(score),
                )
            )
        return results
