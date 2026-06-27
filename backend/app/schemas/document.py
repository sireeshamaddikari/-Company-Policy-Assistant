"""Document API schemas (Pydantic DTOs)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.document import Document


class DocumentUploadResponse(BaseModel):
    """Response returned after a successful upload + ingestion."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    content_type: str
    pages: int | None = Field(
        default=None, description="Number of pages (PDF only; null for DOCX)."
    )
    chunks_created: int = Field(description="Number of text chunks indexed.")
    status: str
    upload_time: datetime

    @classmethod
    def from_model(cls, document: Document) -> "DocumentUploadResponse":
        """Build the response from a persisted Document model."""
        return cls(
            id=document.id,
            filename=document.filename,
            content_type=document.content_type,
            pages=document.pages,
            chunks_created=document.chunk_count,
            status=document.status,
            upload_time=document.created_at,
        )


class DocumentSummary(BaseModel):
    """List-view metadata for a document.

    ``filename`` is the on-disk (stored) name; ``original_filename`` is the name
    the user uploaded.
    """

    id: str
    filename: str = Field(description="Stored (on-disk) filename.")
    original_filename: str = Field(description="Name as uploaded by the user.")
    file_type: str = Field(description="Normalized type: pdf | docx.")
    pages: int | None
    chunk_count: int
    upload_date: datetime
    indexing_status: str = Field(description="processing | indexed | failed.")

    @classmethod
    def from_model(cls, document: Document) -> "DocumentSummary":
        return cls(
            id=document.id,
            filename=document.stored_filename,
            original_filename=document.filename,
            file_type=document.content_type,
            pages=document.pages,
            chunk_count=document.chunk_count,
            upload_date=document.created_at,
            indexing_status=document.status,
        )


class DocumentDetail(DocumentSummary):
    """Complete metadata for a single document."""

    size_bytes: int
    checksum: str
    error: str | None = None
    updated_at: datetime

    @classmethod
    def from_model(cls, document: Document) -> "DocumentDetail":
        return cls(
            id=document.id,
            filename=document.stored_filename,
            original_filename=document.filename,
            file_type=document.content_type,
            pages=document.pages,
            chunk_count=document.chunk_count,
            upload_date=document.created_at,
            indexing_status=document.status,
            size_bytes=document.size_bytes,
            checksum=document.checksum,
            error=document.error,
            updated_at=document.updated_at,
        )


class DocumentDeleteResponse(BaseModel):
    """Confirmation returned after deleting a document."""

    id: str
    deleted: bool = True
    chunks_removed: int
    message: str
