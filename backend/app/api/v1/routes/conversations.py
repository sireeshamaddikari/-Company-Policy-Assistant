"""Conversation (chat history) routes (stub).

Planned endpoints (added in a later step):
    GET    /conversations          list conversations
    GET    /conversations/{id}     fetch a conversation with its messages
    DELETE /conversations/{id}     delete a conversation

An empty router is declared so it can be aggregated now; no endpoints yet.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/conversations", tags=["conversations"])
