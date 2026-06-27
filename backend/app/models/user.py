"""User model (stub) — reserved for future authentication / multi-user support.

Planned columns:
    id              : primary key
    email           : unique login identifier
    hashed_password : set via app/core/security.py
    is_active       : bool
    created_at / updated_at (via TimestampMixin)

Once introduced, documents and conversations gain a ``user_id`` FK and
repositories scope every query to the current user.
"""
