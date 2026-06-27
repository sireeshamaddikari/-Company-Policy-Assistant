"""Small file helpers used by the ingestion pipeline."""

import hashlib
from pathlib import Path


def sha256_hex(data: bytes) -> str:
    """Return the hex SHA-256 digest of the given bytes."""
    return hashlib.sha256(data).hexdigest()


def extension_of(filename: str) -> str:
    """Return the lower-cased file extension including the dot (e.g. ``.pdf``)."""
    return Path(filename).suffix.lower()


def build_stored_filename(document_id: str, original_filename: str) -> str:
    """Build a collision-free on-disk name: ``<document_id><ext>``.

    Using the document id (not the user-supplied name) avoids path traversal
    and duplicate-name issues.
    """
    return f"{document_id}{extension_of(original_filename)}"


def ensure_dir(path: str | Path) -> Path:
    """Create the directory (and parents) if needed and return it as a Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
