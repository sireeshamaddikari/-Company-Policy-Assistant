"""Conversation model (stub).

Represents a chat session that groups an ordered list of messages.

Planned columns:
    id          : primary key
    title       : short auto-generated label
    user_id     : FK -> users.id (future, multi-user scoping)
    created_at / updated_at (via TimestampMixin)

Relationships: one Conversation -> many Message.
"""
