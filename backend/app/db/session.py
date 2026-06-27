"""Database engine and session management.

Provides the SQLAlchemy engine, a session factory, and a ``get_db`` dependency
for FastAPI. This is the single place that knows how to open a DB connection;
repositories receive a ``Session`` and never create one themselves.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# ``check_same_thread=False`` is required for SQLite when used with the
# threadpool that serves FastAPI's sync endpoints.
_connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and guarantee it is closed afterwards.

    Used as a FastAPI dependency: ``db: Session = Depends(get_db)``.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
