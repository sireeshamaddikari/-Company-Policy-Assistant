"""Abstract contracts for the RAG backends.

These ``Protocol`` definitions describe *what* the embedder, vector store, and
LLM client must do — not *how*. Services depend on these types; concrete
implementations (FAISS, sentence-transformers, Mistral) satisfy them
structurally. This is the seam that keeps the architecture swappable.

NOTE: These are interface definitions only — no behavior is implemented here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class SearchResult:
    """A single vector-store hit returned by a similarity search."""

    document_id: str
    chunk_index: int
    text: str
    score: float


@runtime_checkable
class Embedder(Protocol):
    """Turns text into dense vectors (e.g. all-MiniLM-L6-v2)."""

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts (used during ingestion)."""
        ...

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query string (used during retrieval)."""
        ...


@runtime_checkable
class VectorStore(Protocol):
    """Stores embeddings and answers nearest-neighbour queries (e.g. FAISS)."""

    def add(
        self,
        document_id: str,
        embeddings: list[list[float]],
        texts: list[str],
    ) -> None:
        """Index the chunk embeddings for a document."""
        ...

    def search(self, query_embedding: list[float], k: int) -> list[SearchResult]:
        """Return the top-k most similar chunks."""
        ...

    def delete(self, document_id: str) -> None:
        """Remove all vectors belonging to a document."""
        ...

    def persist(self) -> None:
        """Flush the index (and id-map) to disk."""
        ...


@runtime_checkable
class LLMClient(Protocol):
    """Generates an answer from a system + user prompt (e.g. Mistral API)."""

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Return the model's completion for the given prompts."""
        ...
