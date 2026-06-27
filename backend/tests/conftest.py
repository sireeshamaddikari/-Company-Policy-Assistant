"""Shared pytest fixtures.

Storage is redirected to a throwaway temp directory **before** the app is
imported, so tests never touch the project's ./data (the DB engine and settings
are created at import time and read these env vars).
"""

import atexit
import os
import shutil
import tempfile
from pathlib import Path

import pytest

# --- isolate storage (must happen before any `app` import) -----------------
_TMP = Path(tempfile.mkdtemp(prefix="rag_test_"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_TMP / 'test.db').as_posix()}"
os.environ["UPLOAD_DIR"] = str(_TMP / "uploads")
os.environ["VECTORSTORE_PATH"] = str(_TMP / "vectorstore")
os.environ["DEBUG"] = "false"
atexit.register(lambda: shutil.rmtree(_TMP, ignore_errors=True))


@pytest.fixture(scope="session")
def tmp_storage() -> Path:
    """The temp directory backing the test DB / uploads / vectorstore."""
    return _TMP


@pytest.fixture(scope="session")
def client():
    """A TestClient whose lifespan runs (creating tables on startup).

    ``create_app`` is imported lazily so unit tests that don't need the full
    app (and its heavy ML imports) stay light.
    """
    from fastapi.testclient import TestClient

    from app.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client
