"""Unit tests for DocumentService using in-memory fakes (no DB, no FAISS).

Demonstrates the service is testable in isolation thanks to dependency
injection: collaborators are simple fakes.
"""

from types import SimpleNamespace

import pytest

from app.core.exceptions import NotFoundError
from app.models.document import Document, DocumentStatus
from app.services.document_service import DocumentService


class FakeRepository:
    def __init__(self, documents: list[Document]) -> None:
        self._docs = {d.id: d for d in documents}
        self.deleted: list[str] = []

    def list(self) -> list[Document]:
        return list(self._docs.values())

    def get(self, document_id: str) -> Document | None:
        return self._docs.get(document_id)

    def delete(self, document: Document) -> None:
        self.deleted.append(document.id)
        self._docs.pop(document.id, None)


class FakeVectorStore:
    def __init__(self) -> None:
        self.deleted: list[str] = []
        self.persist_calls = 0

    def delete(self, document_id: str) -> None:
        self.deleted.append(document_id)

    def persist(self) -> None:
        self.persist_calls += 1


def _doc(doc_id: str = "abc", chunks: int = 3) -> Document:
    return Document(
        id=doc_id,
        filename="handbook.pdf",
        stored_filename=f"{doc_id}.pdf",
        content_type="pdf",
        size_bytes=123,
        checksum="deadbeef",
        pages=2,
        chunk_count=chunks,
        status=DocumentStatus.INDEXED.value,
    )


def _service(repo, vs, tmp_path) -> DocumentService:
    settings = SimpleNamespace(upload_dir=str(tmp_path))
    return DocumentService(repository=repo, vector_store=vs, settings=settings)


def test_get_document_missing_raises_not_found(tmp_path):
    service = _service(FakeRepository([]), FakeVectorStore(), tmp_path)
    with pytest.raises(NotFoundError):
        service.get_document("nope")


def test_list_documents_returns_all(tmp_path):
    docs = [_doc("a"), _doc("b")]
    service = _service(FakeRepository(docs), FakeVectorStore(), tmp_path)
    assert {d.id for d in service.list_documents()} == {"a", "b"}


def test_delete_removes_vectors_then_metadata(tmp_path):
    doc = _doc("xyz", chunks=5)
    repo = FakeRepository([doc])
    vs = FakeVectorStore()
    service = _service(repo, vs, tmp_path)

    result = service.delete_document("xyz")

    assert result.document_id == "xyz"
    assert result.chunks_removed == 5
    assert vs.deleted == ["xyz"]        # vectors removed
    assert vs.persist_calls == 1        # index persisted for consistency
    assert repo.deleted == ["xyz"]      # metadata removed


def test_delete_missing_raises_not_found(tmp_path):
    service = _service(FakeRepository([]), FakeVectorStore(), tmp_path)
    with pytest.raises(NotFoundError):
        service.delete_document("missing")
