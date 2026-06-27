"""End-to-end tests for the document management endpoints.

Exercises upload -> list -> get -> delete against the real app (TestClient),
including FAISS/SQLite consistency after deletion. Runs as a single ordered
flow because the app's vector store and DB are shared singletons.
"""

import io
import json
import os
from pathlib import Path

SAMPLE_TEXT = (
    "Acme Corporation Employee Handbook. "
    "This document describes company policies, benefits and procedures. "
) * 60


def _pdf_bytes(pages: int = 2) -> bytes:
    from reportlab.pdfgen import canvas

    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    for page in range(pages):
        t = c.beginText(40, 800)
        for line in SAMPLE_TEXT[:1400].split(". "):
            t.textLine(f"[p{page + 1}] {line}")
        c.drawText(t)
        c.showPage()
    c.save()
    return buf.getvalue()


def _docx_bytes() -> bytes:
    import docx

    buf = io.BytesIO()
    d = docx.Document()
    for para in SAMPLE_TEXT.split(". "):
        if para.strip():
            d.add_paragraph(para)
    d.save(buf)
    return buf.getvalue()


def _upload(client, name, data, mime):
    return client.post(
        "/api/v1/documents", files={"file": (name, data, mime)}
    )


def _vector_doc_ids() -> list[str]:
    """Read the persisted FAISS id-map and return the document_id per vector."""
    meta_path = Path(os.environ["VECTORSTORE_PATH"]) / "store_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    return [v["document_id"] for v in meta["id_map"].values()]


def test_document_management_flow(client):
    # --- upload a PDF and a DOCX ---
    pdf = _upload(client, "handbook.pdf", _pdf_bytes(2), "application/pdf")
    assert pdf.status_code == 201, pdf.text
    pdf_id = pdf.json()["id"]
    pdf_chunks = pdf.json()["chunks_created"]

    docx = _upload(
        client,
        "handbook.docx",
        _docx_bytes(),
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    assert docx.status_code == 201, docx.text
    docx_id = docx.json()["id"]
    docx_chunks = docx.json()["chunks_created"]

    # --- LIST: both present with the required fields ---
    res = client.get("/api/v1/documents")
    assert res.status_code == 200
    items = res.json()
    by_id = {d["id"]: d for d in items}
    assert {pdf_id, docx_id} <= set(by_id)
    expected_fields = {
        "id",
        "filename",
        "original_filename",
        "file_type",
        "pages",
        "chunk_count",
        "upload_date",
        "indexing_status",
    }
    assert expected_fields <= set(by_id[pdf_id])
    assert by_id[pdf_id]["original_filename"] == "handbook.pdf"
    assert by_id[pdf_id]["filename"].endswith(".pdf")  # stored name
    assert by_id[pdf_id]["file_type"] == "pdf"
    assert by_id[pdf_id]["indexing_status"] == "indexed"
    assert by_id[pdf_id]["pages"] == 2
    assert by_id[docx_id]["pages"] is None

    # --- GET one: full metadata ---
    res = client.get(f"/api/v1/documents/{pdf_id}")
    assert res.status_code == 200
    detail = res.json()
    assert detail["id"] == pdf_id
    assert detail["size_bytes"] > 0
    assert detail["checksum"]
    assert "updated_at" in detail

    # --- GET unknown: 404 with error envelope ---
    res = client.get("/api/v1/documents/does-not-exist")
    assert res.status_code == 404
    assert res.json()["error"]["type"] == "NotFoundError"

    # --- vector store has both docs' vectors ---
    ids_before = _vector_doc_ids()
    assert ids_before.count(pdf_id) == pdf_chunks
    assert ids_before.count(docx_id) == docx_chunks

    # --- DELETE the PDF ---
    res = client.delete(f"/api/v1/documents/{pdf_id}")
    assert res.status_code == 200
    body = res.json()
    assert body["deleted"] is True
    assert body["chunks_removed"] == pdf_chunks
    assert pdf_id in body["message"]

    # --- consistency: gone from DB, file, and FAISS ---
    assert client.get(f"/api/v1/documents/{pdf_id}").status_code == 404
    remaining = {d["id"] for d in client.get("/api/v1/documents").json()}
    assert pdf_id not in remaining and docx_id in remaining

    upload_dir = Path(os.environ["UPLOAD_DIR"])
    assert not (upload_dir / by_id[pdf_id]["filename"]).exists()

    ids_after = _vector_doc_ids()
    assert pdf_id not in ids_after
    assert ids_after.count(docx_id) == docx_chunks  # docx untouched

    # --- DELETE unknown: 404 ---
    assert client.delete("/api/v1/documents/does-not-exist").status_code == 404
