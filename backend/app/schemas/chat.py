"""Chat API schemas (Pydantic DTOs)."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """A user question for the RAG pipeline."""

    question: str = Field(min_length=1, description="The user's question.")
    top_k: int | None = Field(
        default=None,
        ge=1,
        le=20,
        description="Override the number of chunks to retrieve (optional).",
    )


class RetrievedChunk(BaseModel):
    """A raw chunk returned by the retriever (for transparency/debugging)."""

    document_id: str
    chunk_index: int
    text: str
    score: float


class Citation(BaseModel):
    """A source reference attached to the answer."""

    document_id: str
    filename: str
    chunk_index: int
    snippet: str
    score: float


class ChatResponse(BaseModel):
    """The RAG pipeline's answer plus its grounding."""

    answer: str
    citations: list[Citation]
    retrieved_chunks: list[RetrievedChunk]
    confidence: float | None = Field(
        default=None,
        description="Retrieval-similarity confidence in [0, 1] (None if no context).",
    )
