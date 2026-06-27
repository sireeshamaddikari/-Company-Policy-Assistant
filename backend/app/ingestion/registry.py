"""Loader registry — maps a file extension to the right loader.

Adding a new format is a one-line registration here. Keeping the mapping in one
place means validation ("is this supported?") and selection ("which loader?")
never drift apart.
"""

from app.core.exceptions import UnsupportedFileTypeError
from app.ingestion.loaders import DocumentLoader, DocxLoader, PDFLoader
from app.utils.files import extension_of

# Extension -> loader instance. Loaders are stateless and safe to share.
_LOADERS: dict[str, DocumentLoader] = {
    ".pdf": PDFLoader(),
    ".docx": DocxLoader(),
}

# Extension -> normalized content-type label stored on the Document row.
_CONTENT_TYPES: dict[str, str] = {
    ".pdf": "pdf",
    ".docx": "docx",
}

SUPPORTED_EXTENSIONS: frozenset[str] = frozenset(_LOADERS)


def is_supported(filename: str) -> bool:
    """Return True if a loader exists for the file's extension."""
    return extension_of(filename) in _LOADERS


def get_loader(filename: str) -> DocumentLoader:
    """Return the loader for ``filename`` or raise ``UnsupportedFileTypeError``."""
    ext = extension_of(filename)
    loader = _LOADERS.get(ext)
    if loader is None:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{ext or '(none)'}'. Supported: {supported}."
        )
    return loader


def content_type_of(filename: str) -> str:
    """Return the normalized content-type label for a supported file."""
    return _CONTENT_TYPES[extension_of(filename)]
