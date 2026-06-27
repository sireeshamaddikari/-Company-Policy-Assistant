"""Health check route.

Lightweight liveness probe used to verify the API is running. Kept separate
from feature routes and (intentionally) unversioned-friendly.
"""

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return a simple OK payload for monitoring / load balancers."""
    return {"status": "ok", "app": settings.app_name}
