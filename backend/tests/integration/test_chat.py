"""End-to-end tests for the chat (RAG) endpoint.

Uses the REAL retrieval pipeline (embeddings + FAISS) but a FAKE LLM client
(via dependency override) so the test is deterministic and needs no network or
API key. Verifies the retrieved context is actually injected into the prompt.
"""

import io

from app.api.deps import get_llm_client

VACATION_TEXT = (
    "Acme Corporation Leave Policy. "
    "Full-time employees are entitled to twenty paid vacation days per year. "
    "Vacation requests must be approved by a manager in advance. "
) * 20


class FakeLLM:
    """Records prompts and returns a canned answer."""

    def __init__(self, answer: str) -> None:
        self.answer = answer
        self.calls: list[tuple[str, str]] = []

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.calls.append((system_prompt, user_prompt))
        return self.answer


def _docx_bytes(text: str) -> bytes:
    import docx

    buf = io.BytesIO()
    d = docx.Document()
    for para in text.split(". "):
        if para.strip():
            d.add_paragraph(para)
    d.save(buf)
    return buf.getvalue()


def _upload(client, name, data):
    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return client.post("/api/v1/documents", files={"file": (name, data, mime)})


def test_chat_pipeline(client):
    fake = FakeLLM("Full-time employees get twenty paid vacation days per year.")
    client.app.dependency_overrides[get_llm_client] = lambda: fake
    try:
        # --- 0) Conversational intents short-circuit before retrieval / LLM ---
        intent_cases = [
            ("hi", "Company Policy Assistant"),
            ("good morning", "Company Policy Assistant"),
            ("bye", "Goodbye"),
            ("thanks a lot", "You're welcome"),
            ("who are you", "I answer questions using the uploaded"),
            ("how are you?", "I'm doing well"),
        ]
        for message, expected in intent_cases:
            fake.calls.clear()
            res = client.post("/api/v1/chat", json={"question": message})
            assert res.status_code == 200, res.text
            body = res.json()
            assert expected in body["answer"], (message, body["answer"])
            assert body["citations"] == []
            assert body["retrieved_chunks"] == []
            assert body["confidence"] is None
            assert not fake.calls, f"LLM must not be called for: {message}"

        # --- 1) No documents indexed yet -> out-of-scope fallback ---
        res = client.post("/api/v1/chat", json={"question": "How many vacation days?"})
        assert res.status_code == 200, res.text
        body = res.json()
        assert "couldn't find information about that" in body["answer"]
        assert body["citations"] == []
        assert body["retrieved_chunks"] == []
        assert body["confidence"] is None
        assert not fake.calls, "LLM must not be called when there is no context"

        # --- 2) Upload a relevant document ---
        up = _upload(client, "leave_policy.docx", _docx_bytes(VACATION_TEXT))
        assert up.status_code == 201, up.text
        doc_id = up.json()["id"]

        # --- 3) Ask a grounded question ---
        res = client.post(
            "/api/v1/chat",
            json={"question": "How many vacation days do employees get?", "top_k": 3},
        )
        assert res.status_code == 200, res.text
        body = res.json()

        # answer comes from the (fake) LLM
        assert body["answer"] == fake.answer

        # citations + retrieved chunks reference the uploaded document
        assert len(body["citations"]) >= 1
        assert len(body["retrieved_chunks"]) >= 1
        cit = body["citations"][0]
        assert cit["document_id"] == doc_id
        assert cit["filename"] == "leave_policy.docx"  # original filename resolved
        assert cit["snippet"]
        assert {"document_id", "chunk_index", "text", "score"} <= set(
            body["retrieved_chunks"][0]
        )

        # confidence is a similarity in [0, 1]
        assert 0.0 <= body["confidence"] <= 1.0

        # the retrieved context was actually injected into the user prompt
        assert fake.calls, "LLM should have been called"
        _system, user_prompt = fake.calls[-1]
        assert "vacation" in user_prompt.lower()
        assert "Question: How many vacation days" in user_prompt

        # --- 3b) Out-of-scope question (below threshold) -> fallback, no LLM ---
        fake.calls.clear()
        res = client.post(
            "/api/v1/chat",
            json={"question": "What is the capital of France?"},
        )
        assert res.status_code == 200, res.text
        body = res.json()
        assert "couldn't find information about that" in body["answer"]
        assert body["citations"] == []
        assert body["retrieved_chunks"] == []
        assert body["confidence"] is None
        assert not fake.calls, "LLM must not be called for out-of-scope questions"

        # --- 4) Validation: empty question -> 422 ---
        res = client.post("/api/v1/chat", json={"question": ""})
        assert res.status_code == 422

        # cleanup the uploaded doc so other tests start clean
        client.delete(f"/api/v1/documents/{doc_id}")
    finally:
        client.app.dependency_overrides.pop(get_llm_client, None)
