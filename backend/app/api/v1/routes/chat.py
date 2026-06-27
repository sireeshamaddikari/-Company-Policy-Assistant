"""Chat routes.

Endpoints:
    POST /chat   ask a question; returns a grounded answer, citations,
                 retrieved chunks and a confidence score.
"""

from fastapi import APIRouter, Depends

from app.api.deps import get_chat_service
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "",
    response_model=ChatResponse,
    summary="Ask a question (RAG)",
)
def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """Run the retrieval-augmented generation pipeline for a question.

    Returns the answer, the source citations, the retrieved chunks, and a
    retrieval-based confidence score.
    """
    return service.answer_question(request.question, top_k=request.top_k)
