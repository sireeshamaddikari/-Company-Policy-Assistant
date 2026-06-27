"""Retrieval service — turns a question into ranked context chunks.

Embeds the query and runs a similarity search against the vector store. Pure
retrieval: no prompt building, no LLM, no DB. Returns the vector store's
``SearchResult`` objects (document_id, chunk_index, text, score).
"""

import logging

from app.rag.interfaces import Embedder, SearchResult, VectorStore

logger = logging.getLogger(__name__)


class RetrievalService:
    """Embeds a query and retrieves the top-k most similar chunks."""

    def __init__(self, embedder: Embedder, vector_store: VectorStore) -> None:
        self._embedder = embedder
        self._vector_store = vector_store

    def retrieve(self, query: str, k: int) -> list[SearchResult]:
        """Return up to ``k`` chunks most similar to ``query``."""
        query_embedding = self._embedder.embed_query(query)
        results = self._vector_store.search(query_embedding, k)
        logger.info("Retrieved %d chunks for query (k=%d)", len(results), k)
        return results
