"""Shared FastAPI dependencies (the dependency-injection layer).

Keeps construction/wiring out of routes and services. Heavy, stateful
collaborators (the embedding model, the FAISS index) are process-wide
singletons via ``lru_cache`` so they are created once; request-scoped
collaborators (DB session, repository, service) are built per request.
"""

from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.ingestion.splitter import TextSplitter
from app.rag.embeddings import SentenceTransformerEmbedder
from app.rag.interfaces import Embedder, LLMClient, VectorStore
from app.rag.llm import MistralClient
from app.rag.vector_store import FaissVectorStore
from app.repositories.document_repository import DocumentRepository
from app.services.chat_service import ChatService
from app.services.document_service import DocumentService
from app.services.ingestion_service import IngestionService
from app.services.intent import IntentDetector
from app.services.retrieval_service import RetrievalService

__all__ = [
    "get_db",
    "get_embedder",
    "get_vector_store",
    "get_llm_client",
    "get_document_repository",
    "get_ingestion_service",
    "get_document_service",
    "get_retrieval_service",
    "get_intent_detector",
    "get_chat_service",
]


@lru_cache
def get_embedder() -> Embedder:
    """Process-wide embedder singleton (loads the model once)."""
    settings = get_settings()
    return SentenceTransformerEmbedder(settings.embedding_model)


@lru_cache
def get_vector_store() -> VectorStore:
    """Process-wide FAISS vector store singleton (holds the in-memory index)."""
    settings = get_settings()
    return FaissVectorStore(settings.vectorstore_path)


@lru_cache
def get_llm_client() -> LLMClient:
    """Process-wide Mistral client singleton (reuses an httpx connection pool)."""
    return MistralClient(get_settings())


def get_document_repository(
    db: Session = Depends(get_db),
) -> DocumentRepository:
    """Per-request document repository bound to the request's DB session."""
    return DocumentRepository(db)


def get_ingestion_service(
    repository: DocumentRepository = Depends(get_document_repository),
    embedder: Embedder = Depends(get_embedder),
    vector_store: VectorStore = Depends(get_vector_store),
    settings: Settings = Depends(get_settings),
) -> IngestionService:
    """Assemble the ingestion service from its (injected) collaborators."""
    splitter = TextSplitter(settings.chunk_size, settings.chunk_overlap)
    return IngestionService(
        repository=repository,
        splitter=splitter,
        embedder=embedder,
        vector_store=vector_store,
        settings=settings,
    )


def get_document_service(
    repository: DocumentRepository = Depends(get_document_repository),
    vector_store: VectorStore = Depends(get_vector_store),
    settings: Settings = Depends(get_settings),
) -> DocumentService:
    """Assemble the document (read/delete) service from its collaborators."""
    return DocumentService(
        repository=repository,
        vector_store=vector_store,
        settings=settings,
    )


def get_retrieval_service(
    embedder: Embedder = Depends(get_embedder),
    vector_store: VectorStore = Depends(get_vector_store),
) -> RetrievalService:
    """Assemble the retrieval service (embedder + vector store)."""
    return RetrievalService(embedder=embedder, vector_store=vector_store)


@lru_cache
def get_intent_detector() -> IntentDetector:
    """Process-wide intent detector singleton (stateless)."""
    return IntentDetector()


def get_chat_service(
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    llm_client: LLMClient = Depends(get_llm_client),
    repository: DocumentRepository = Depends(get_document_repository),
    intent_detector: IntentDetector = Depends(get_intent_detector),
    settings: Settings = Depends(get_settings),
) -> ChatService:
    """Assemble the RAG chat service from its collaborators."""
    return ChatService(
        retrieval_service=retrieval_service,
        llm_client=llm_client,
        document_repository=repository,
        intent_detector=intent_detector,
        settings=settings,
    )


# Future (auth):
# def get_current_user(...): ...
