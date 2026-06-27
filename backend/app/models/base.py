"""Declarative base and shared model mixins.

Every ORM model inherits from ``Base`` so it is registered on a single
``MetaData``. ``TimestampMixin`` provides the created/updated columns that most
tables need, avoiding repetition.
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


class TimestampMixin:
    """Adds ``created_at`` / ``updated_at`` columns managed by the database."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
