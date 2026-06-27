"""Maps application exceptions to consistent JSON HTTP responses.

Registering these handlers on the app keeps error formatting in one place, so
every endpoint returns the same error envelope:

    {"error": {"type": "NotFoundError", "message": "..."}}
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError


def register_exception_handlers(app: FastAPI) -> None:
    """Attach domain exception handlers to the FastAPI application."""

    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"type": exc.__class__.__name__, "message": exc.message}},
        )
