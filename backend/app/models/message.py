"""Message model (stub).

A single turn within a conversation (user question or assistant answer).

Planned columns:
    id              : primary key
    conversation_id : FK -> conversations.id
    role            : user | assistant
    content         : message text
    created_at (via TimestampMixin)

Relationships: one Message -> many Citation (for assistant answers).
"""
