"""Database initialization.

While the schema is still settling we create tables directly with SQLAlchemy's
``create_all`` (Alembic migrations are deferred until the user/auth tables land).
Importing ``app.models`` ensures every ORM model is registered on the metadata
before the tables are created.
"""

from app.db.session import engine
from app.models.base import Base


def init_db() -> None:
    """Create all tables that do not yet exist.

    No-op today because no models are defined yet. Call this on application
    startup (or from a CLI) once models exist. Replace with Alembic migrations
    before introducing destructive schema changes.
    """
    # Import side-effect: registers models on Base.metadata.
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
