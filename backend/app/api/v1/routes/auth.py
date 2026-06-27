"""Authentication routes (stub) — reserved for future auth.

Planned endpoints:
    POST /auth/register   create a user
    POST /auth/login      exchange credentials for a token

An empty router is declared as a home; not aggregated until auth is built.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])
