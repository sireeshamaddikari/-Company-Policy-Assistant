"""Document ORM model.

Stores metadata for an uploaded document and tracks its progress through the
ingestion pipeline. The raw file lives on disk (``stored_filename`` under the
upload dir); the embeddings live in FAISS. This row is the source of truth for
what exists and its status.
"""

import uuid
from enum import Enum

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class DocumentStatus(str, Enum):
    """Lifecycle of a document through the ingestion pipeline."""

    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


def _new_id() -> str:
    """Generate a unique, URL-safe document id."""
    return uuid.uuid4().hex


class Document(Base, TimestampMixin):
    """A single uploaded document and its ingestion metadata."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_new_id)

    # Original name as uploaded by the user (for display).
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    # Name on disk (``<id>.<ext>``) to avoid collisions / path issues.
    stored_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    # Normalized type: "pdf" | "docx".
    content_type: Mapped[str] = mapped_column(String(16), nullable=False)

    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    # SHA-256 of the file contents (enables future dedup).
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)

    # Populated after successful extraction/indexing.
    pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default=DocumentStatus.PROCESSING.value
    )
    # Error detail when status == failed.
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
