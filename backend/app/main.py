"""FastAPI application entrypoint (application factory).

``create_app`` wires the application together from its parts:
  * logging
  * CORS for the frontend
  * domain exception handlers (consistent error envelope)
  * the unversioned ``/health`` probe
  * the versioned API under ``/api/v1``

Feature routers are mounted but currently expose no endpoints — business logic
is added in later steps.

Run locally (from the ``backend/`` directory):
    uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.api.v1.routes import health
from app.core.config import Settings, get_settings
from app.core.error_handlers import register_exception_handlers
from app.core.logging import setup_logging
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create database tables on startup (Alembic replaces this later)."""
    init_db()
    yield


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build and configure a FastAPI application instance."""
    settings = settings or get_settings()
    setup_logging()

    app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    # Liveness probe at the root for load balancers / uptime checks.
    app.include_router(health.router)
    # Versioned application API.
    app.include_router(api_router, prefix=f"{settings.api_v1_prefix}/v1")

    return app


app = create_app()
