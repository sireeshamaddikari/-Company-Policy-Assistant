"""ORM models package.

Import concrete models here as they are defined so a single
``import app.models`` registers all tables on ``Base.metadata`` (used by
``db.init_db`` and, later, Alembic autogenerate).

Planned models (defined in later steps):
    document.py      -> Document
    conversation.py  -> Conversation
    message.py       -> Message
    citation.py      -> Citation
    user.py          -> User (future: multi-user / auth)
"""

from app.models.base import Base  # noqa: F401
from app.models.document import Document, DocumentStatus  # noqa: F401
