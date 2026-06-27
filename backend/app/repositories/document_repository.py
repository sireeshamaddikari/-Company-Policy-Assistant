"""Document repository — persistence for :class:`Document` rows.

The only place that issues DB queries for documents. Services call these methods
and never touch the ORM/session directly, which keeps persistence concerns
isolated (and gives future per-user scoping a single home).
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document


class DocumentRepository:
    """CRUD operations for documents, scoped to one DB session."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, document: Document) -> Document:
        """Persist a new document and return it (with generated fields)."""
        self._db.add(document)
        self._db.commit()
        self._db.refresh(document)
        return document

    def update(self, document: Document) -> Document:
        """Flush pending changes on an attached document to the DB."""
        self._db.commit()
        self._db.refresh(document)
        return document

    def get(self, document_id: str) -> Document | None:
        """Return a document by id, or ``None`` if it does not exist."""
        return self._db.get(Document, document_id)

    def list(self) -> list[Document]:
        """Return all documents, most recent first."""
        stmt = select(Document).order_by(Document.created_at.desc())
        return list(self._db.scalars(stmt).all())

    def get_by_checksum(self, checksum: str) -> Document | None:
        """Return an existing document with the same content, if any."""
        stmt = select(Document).where(Document.checksum == checksum)
        return self._db.scalars(stmt).first()

    def delete(self, document: Document) -> None:
        """Delete a document row."""
        self._db.delete(document)
        self._db.commit()
