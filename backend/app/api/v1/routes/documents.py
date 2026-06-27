"""Document routes.

Endpoints:
    POST   /documents          upload a PDF/DOCX, ingest it, return status.
    GET    /documents          list all documents.
    GET    /documents/{id}     full metadata for one document (404 if missing).
    DELETE /documents/{id}     delete file, metadata and vectors.
"""

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.deps import get_document_service, get_ingestion_service
from app.schemas.document import (
    DocumentDeleteResponse,
    DocumentDetail,
    DocumentSummary,
    DocumentUploadResponse,
)
from app.services.document_service import DocumentService
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and ingest a document",
)
def upload_document(
    file: UploadFile = File(...),
    service: IngestionService = Depends(get_ingestion_service),
) -> DocumentUploadResponse:
    """Accept a PDF/DOCX upload and run the full ingestion pipeline.

    Returns the new document's id, filename, page count (PDF only), number of
    chunks indexed, status and upload time.
    """
    data = file.file.read()
    document = service.ingest(file.filename, data)
    return DocumentUploadResponse.from_model(document)


@router.get(
    "",
    response_model=list[DocumentSummary],
    summary="List all documents",
)
def list_documents(
    service: DocumentService = Depends(get_document_service),
) -> list[DocumentSummary]:
    """Return metadata for every uploaded document, most recent first."""
    documents = service.list_documents()
    return [DocumentSummary.from_model(d) for d in documents]


@router.get(
    "/{document_id}",
    response_model=DocumentDetail,
    summary="Get one document's metadata",
)
def get_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service),
) -> DocumentDetail:
    """Return complete metadata for a single document (404 if not found)."""
    document = service.get_document(document_id)
    return DocumentDetail.from_model(document)


@router.delete(
    "/{document_id}",
    response_model=DocumentDeleteResponse,
    summary="Delete a document",
)
def delete_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service),
) -> DocumentDeleteResponse:
    """Delete a document's file, metadata and FAISS vectors (404 if missing)."""
    result = service.delete_document(document_id)
    return DocumentDeleteResponse(
        id=result.document_id,
        chunks_removed=result.chunks_removed,
        message=f"Document '{result.document_id}' deleted successfully.",
    )
