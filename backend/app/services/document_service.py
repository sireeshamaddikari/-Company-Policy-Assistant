"""Document service — lifecycle management for ingested documents.

Covers listing, single-document retrieval, and deletion. Deletion keeps the
three stores consistent (FAISS vectors, the file on disk, and the SQLite row).

Depends only on abstractions injected by the API layer (repository,
``VectorStore``, settings), so it is straightforward to unit-test with fakes.
"""

import logging
from dataclasses import dataclass
from pathlib import Path

from app.core.config import Settings
from app.core.exceptions import NotFoundError
from app.models.document import Document
from app.rag.interfaces import VectorStore
from app.repositories.document_repository import DocumentRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeletionResult:
    """Outcome of deleting a document."""

    document_id: str
    chunks_removed: int


class DocumentService:
    """Read and delete operations over the document store."""

    def __init__(
        self,
        repository: DocumentRepository,
        vector_store: VectorStore,
        settings: Settings,
    ) -> None:
        self._repository = repository
        self._vector_store = vector_store
        self._settings = settings

    def list_documents(self) -> list[Document]:
        """Return all documents, most recent first."""
        return self._repository.list()

    def get_document(self, document_id: str) -> Document:
        """Return a single document or raise ``NotFoundError`` (-> 404)."""
        document = self._repository.get(document_id)
        if document is None:
            raise NotFoundError(f"Document '{document_id}' was not found.")
        return document

    def delete_document(self, document_id: str) -> DeletionResult:
        """Delete a document's vectors, file and metadata, consistently.

        Order is chosen so we never leave orphaned vectors pointing at a missing
        document: remove vectors (and persist the index) first, then the file,
        then the DB row. The operation is idempotent on retry.
        """
        document = self.get_document(document_id)
        chunks = document.chunk_count

        # 1) Vectors first, then persist so the on-disk index stays consistent.
        self._vector_store.delete(document.id)
        self._vector_store.persist()

        # 2) Remove the stored file (tolerate an already-missing file).
        self._delete_file(document.stored_filename)

        # 3) Finally drop the metadata row.
        self._repository.delete(document)

        logger.info(
            "Deleted document %s (%s): removed %d vectors",
            document.id,
            document.filename,
            chunks,
        )
        return DeletionResult(document_id=document.id, chunks_removed=chunks)

    def _delete_file(self, stored_filename: str) -> None:
        path = Path(self._settings.upload_dir) / stored_filename
        try:
            path.unlink(missing_ok=True)
            logger.debug("Removed file %s", path)
        except OSError:
            # Don't fail the whole delete because the file couldn't be removed;
            # the metadata/vectors are the source of truth for the app.
            logger.exception("Could not remove file %s", path)
