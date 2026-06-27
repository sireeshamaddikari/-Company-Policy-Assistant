"""Chat service — orchestrates the RAG pipeline for a single question.

Flow:
    retrieve chunks -> resolve source filenames -> build prompt -> call LLM ->
    assemble answer + citations + retrieved chunks + confidence.

Composes the focused collaborators (retrieval service, LLM client, document
repository) injected by the API layer; it owns no transport or storage details.
"""

import logging

from app.core.config import Settings
from app.core.exceptions import ValidationError
from app.rag.interfaces import LLMClient, SearchResult
from app.rag.prompts import SYSTEM_PROMPT, ContextItem, build_user_prompt
from app.repositories.document_repository import DocumentRepository
from app.schemas.chat import ChatResponse, Citation, RetrievedChunk
from app.services.intent import (
    INTENT_RESPONSES,
    OUT_OF_SCOPE_RESPONSE,
    Intent,
    IntentDetector,
)
from app.services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)

_SNIPPET_LEN = 300


class ChatService:
    """Answers a question using retrieval-augmented generation."""

    def __init__(
        self,
        retrieval_service: RetrievalService,
        llm_client: LLMClient,
        document_repository: DocumentRepository,
        intent_detector: IntentDetector,
        settings: Settings,
    ) -> None:
        self._retrieval = retrieval_service
        self._llm = llm_client
        self._documents = document_repository
        self._intents = intent_detector
        self._settings = settings

    def answer_question(self, question: str, top_k: int | None = None) -> ChatResponse:
        """Classify intent, then run RAG only for document queries."""
        question = (question or "").strip()
        if not question:
            raise ValidationError("Question must not be empty.")

        # Conversational intents short-circuit BEFORE any retrieval or LLM call.
        intent = self._intents.detect(question)
        if intent is not Intent.DOCUMENT_QUERY:
            logger.info("Intent '%s' detected; returning canned response.", intent.value)
            return self._simple_response(INTENT_RESPONSES[intent])

        k = top_k or self._settings.top_k_results
        chunks = self._retrieval.retrieve(question, k)

        # Keep only chunks at/above the relevance threshold. If none qualify the
        # question is out of scope: return the fallback WITHOUT calling the LLM.
        threshold = self._settings.similarity_threshold
        relevant = [c for c in chunks if c.score >= threshold]

        if not relevant:
            top = max((c.score for c in chunks), default=0.0)
            logger.info(
                "No relevant context (best score %.3f < threshold %.3f); "
                "returning out-of-scope response without calling the LLM.",
                top,
                threshold,
            )
            return self._simple_response(OUT_OF_SCOPE_RESPONSE)

        filenames = self._resolve_filenames(relevant)
        contexts = [
            ContextItem(
                source=f"{filenames[c.document_id]} (chunk {c.chunk_index})",
                text=c.text,
            )
            for c in relevant
        ]

        user_prompt = build_user_prompt(question, contexts)
        answer = self._llm.generate(SYSTEM_PROMPT, user_prompt)

        return ChatResponse(
            answer=answer,
            citations=self._build_citations(relevant, filenames),
            retrieved_chunks=[
                RetrievedChunk(
                    document_id=c.document_id,
                    chunk_index=c.chunk_index,
                    text=c.text,
                    score=c.score,
                )
                for c in relevant
            ],
            confidence=self._confidence(relevant),
        )

    @staticmethod
    def _simple_response(answer: str) -> ChatResponse:
        """A plain answer with no sources/chunks/confidence (greeting/fallback)."""
        return ChatResponse(
            answer=answer,
            citations=[],
            retrieved_chunks=[],
            confidence=None,
        )

    # -- helpers -------------------------------------------------------------

    def _resolve_filenames(self, chunks: list[SearchResult]) -> dict[str, str]:
        """Map each document_id to its original filename (one query per doc)."""
        names: dict[str, str] = {}
        for doc_id in {c.document_id for c in chunks}:
            document = self._documents.get(doc_id)
            names[doc_id] = document.filename if document else "unknown"
        return names

    def _build_citations(
        self, chunks: list[SearchResult], filenames: dict[str, str]
    ) -> list[Citation]:
        return [
            Citation(
                document_id=c.document_id,
                filename=filenames[c.document_id],
                chunk_index=c.chunk_index,
                snippet=c.text[:_SNIPPET_LEN],
                score=c.score,
            )
            for c in chunks
        ]

    @staticmethod
    def _confidence(chunks: list[SearchResult]) -> float:
        """Confidence proxy: top cosine similarity, clamped to [0, 1]."""
        top = max(c.score for c in chunks)
        return max(0.0, min(1.0, float(top)))
