"""Ingestion service — orchestrates the document upload pipeline.

Flow:
    validate -> persist file -> create metadata row -> extract text ->
    split into chunks -> embed -> add to vector store -> persist index ->
    mark indexed.

The service depends on abstractions (repository, splitter, ``Embedder``,
``VectorStore``) injected by the API layer, so it has no knowledge of FastAPI,
SQLAlchemy internals, FAISS, or the concrete embedding model.
"""

import logging
from uuid import uuid4

from app.core.config import Settings
from app.core.exceptions import (
    AppError,
    IngestionError,
    PayloadTooLargeError,
    ValidationError,
)
from app.ingestion import registry
from app.ingestion.splitter import TextSplitter
from app.models.document import Document, DocumentStatus
from app.rag.interfaces import Embedder, VectorStore
from app.repositories.document_repository import DocumentRepository
from app.utils.files import build_stored_filename, ensure_dir, sha256_hex

logger = logging.getLogger(__name__)


class IngestionService:
    """Coordinates extraction, chunking, embedding and indexing of a document."""

    def __init__(
        self,
        repository: DocumentRepository,
        splitter: TextSplitter,
        embedder: Embedder,
        vector_store: VectorStore,
        settings: Settings,
    ) -> None:
        self._repository = repository
        self._splitter = splitter
        self._embedder = embedder
        self._vector_store = vector_store
        self._settings = settings

    def ingest(self, filename: str, data: bytes) -> Document:
        """Run the full pipeline for one uploaded file and return its record."""
        self._validate(filename, data)

        document_id = uuid4().hex
        stored_filename = build_stored_filename(document_id, filename)
        self._save_to_disk(stored_filename, data)

        document = Document(
            id=document_id,
            filename=filename,
            stored_filename=stored_filename,
            content_type=registry.content_type_of(filename),
            size_bytes=len(data),
            checksum=sha256_hex(data),
            status=DocumentStatus.PROCESSING.value,
        )
        document = self._repository.add(document)
        logger.info("Created document %s (%s)", document.id, filename)

        try:
            self._process(document)
        except AppError:
            raise
        except Exception as exc:  # noqa: BLE001 - convert to a handled error
            self._mark_failed(document, str(exc))
            logger.exception("Ingestion failed for document %s", document.id)
            raise IngestionError(f"Failed to process '{filename}'.") from exc

        return document

    # -- pipeline steps ------------------------------------------------------

    def _validate(self, filename: str, data: bytes) -> None:
        if not filename:
            raise ValidationError("A filename is required.")
        # Raises UnsupportedFileTypeError for unknown extensions.
        registry.get_loader(filename)
        if not data:
            raise ValidationError("The uploaded file is empty.")
        if len(data) > self._settings.max_upload_size_bytes:
            limit_mb = self._settings.max_upload_size_bytes / (1024 * 1024)
            raise PayloadTooLargeError(f"File exceeds the {limit_mb:.0f} MB limit.")

    def _save_to_disk(self, stored_filename: str, data: bytes) -> None:
        upload_dir = ensure_dir(self._settings.upload_dir)
        (upload_dir / stored_filename).write_bytes(data)
        logger.debug("Saved upload to %s", stored_filename)

    def _process(self, document: Document) -> None:
        """Extract -> chunk -> embed -> index for an already-persisted row."""
        path = str(ensure_dir(self._settings.upload_dir) / document.stored_filename)

        loader = registry.get_loader(document.filename)
        loaded = loader.load(path)
        if not loaded.text.strip():
            raise ValidationError("No extractable text was found in the document.")

        chunks = self._splitter.split(loaded.text)
        if not chunks:
            raise ValidationError("The document produced no text chunks.")

        embeddings = self._embedder.embed_texts(chunks)
        self._vector_store.add(document.id, embeddings, chunks)
        self._vector_store.persist()

        document.pages = loaded.page_count
        document.chunk_count = len(chunks)
        document.status = DocumentStatus.INDEXED.value
        document.error = None
        self._repository.update(document)
        logger.info(
            "Indexed document %s: pages=%s, chunks=%d",
            document.id,
            loaded.page_count,
            len(chunks),
        )

    def _mark_failed(self, document: Document, error: str) -> None:
        document.status = DocumentStatus.FAILED.value
        document.error = error[:1000]
        try:
            self._repository.update(document)
        except Exception:  # noqa: BLE001 - never mask the original error
            logger.exception("Could not record failure for document %s", document.id)
