"""Application-level exception types.

Services and repositories raise these domain exceptions instead of leaking
framework- or storage-specific errors. The API layer (see ``error_handlers``)
translates them into consistent HTTP responses, so business code never has to
construct HTTP status codes directly.
"""


class AppError(Exception):
    """Base class for all expected, handled application errors."""

    status_code: int = 500
    message: str = "Internal server error"

    def __init__(self, message: str | None = None) -> None:
        if message is not None:
            self.message = message
        super().__init__(self.message)


class NotFoundError(AppError):
    """A requested resource does not exist."""

    status_code = 404
    message = "Resource not found"


class ValidationError(AppError):
    """Input failed a business validation rule."""

    status_code = 422
    message = "Invalid input"


class UnauthorizedError(AppError):
    """Authentication is required or has failed (reserved for future auth)."""

    status_code = 401
    message = "Authentication required"


class ConflictError(AppError):
    """The request conflicts with current state (e.g. duplicate document)."""

    status_code = 409
    message = "Conflict"


class UnsupportedFileTypeError(AppError):
    """The uploaded file is not a supported document type."""

    status_code = 415
    message = "Unsupported file type"


class PayloadTooLargeError(AppError):
    """The uploaded file exceeds the configured size limit."""

    status_code = 413
    message = "Uploaded file is too large"


class IngestionError(AppError):
    """The document could not be processed (extraction/embedding/indexing)."""

    status_code = 500
    message = "Failed to process document"


class ConfigurationError(AppError):
    """A required setting is missing or invalid (e.g. no LLM API key)."""

    status_code = 500
    message = "Service is misconfigured"


class LLMError(AppError):
    """The upstream language model request failed."""

    status_code = 502
    message = "The language model request failed"
