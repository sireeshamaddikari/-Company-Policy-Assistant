"""Embedder backed by sentence-transformers (all-MiniLM-L6-v2).

Implements the ``Embedder`` protocol. The model is loaded once per instance
(and the instance is a process-wide singleton via the DI layer), since loading
weights is expensive. Embeddings are L2-normalized so cosine similarity reduces
to an inner product in the vector store.
"""

import logging

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class SentenceTransformerEmbedder:
    """Concrete ``Embedder`` using a sentence-transformers model."""

    def __init__(self, model_name: str) -> None:
        logger.info("Loading embedding model '%s'...", model_name)
        self._model = SentenceTransformer(model_name)
        self._dimension = self._model.get_sentence_embedding_dimension()
        logger.info("Embedding model loaded (dim=%d)", self._dimension)

    @property
    def dimension(self) -> int:
        """Embedding vector dimensionality (384 for all-MiniLM-L6-v2)."""
        return self._dimension

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts (used during ingestion)."""
        if not texts:
            return []
        vectors = self._model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return vectors.tolist()

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query string (used during retrieval)."""
        vector = self._model.encode(
            [text],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return vector[0].tolist()
