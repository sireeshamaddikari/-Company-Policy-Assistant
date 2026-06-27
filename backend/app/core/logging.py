"""Application logging configuration.

Centralizes log setup so the rest of the app just calls
``logging.getLogger(__name__)``. Kept intentionally simple (stdlib logging);
can be swapped for structured/JSON logging later without touching call sites.
"""

import logging

from app.core.config import get_settings


def setup_logging() -> None:
    """Configure the root logger once, based on the current environment."""
    settings = get_settings()
    level = logging.DEBUG if settings.debug else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
