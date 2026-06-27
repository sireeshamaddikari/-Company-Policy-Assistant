"""Aggregates all v1 routers into a single router mounted under /api/v1.

Adding a new resource is a one-line ``include_router`` here. Feature routers
are currently empty (no endpoints) but are wired so the structure is real.
"""

from fastapi import APIRouter

from app.api.v1.routes import chat, conversations, documents

api_router = APIRouter()

api_router.include_router(documents.router)
api_router.include_router(chat.router)
api_router.include_router(conversations.router)

# Mounted once authentication is implemented:
# from app.api.v1.routes import auth
# api_router.include_router(auth.router)
