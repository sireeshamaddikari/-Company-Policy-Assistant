"""Security primitives — password hashing and JWT helpers.

Reserved home for future authentication. Deliberately empty for now: when auth
is introduced, password hashing (e.g. passlib/bcrypt) and token creation/
verification live here, keeping crypto concerns out of services and routes.
"""

# Intentionally no implementation yet. See app/api/v1/routes/auth.py and
# app/api/deps.py (get_current_user) for where these will be consumed.
