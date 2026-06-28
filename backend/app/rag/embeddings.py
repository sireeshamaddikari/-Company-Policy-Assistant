"""Embedder backed by the Mistral embeddings API (``mistral-embed``).

Implements the ``Embedder`` protocol by calling Mistral's hosted ``/embeddings``
endpoint over HTTP (via httpx) instead of running a local model. This keeps the
deployment image small and memory use low (no PyTorch / model weights), which
matters on constrained hosts such as Render's free tier.

Design notes:
  * Vectors are L2-normalized here so cosine similarity reduces to an inner
    product in the FAISS store (which uses ``IndexFlatIP``).
  * ``mistral-embed`` returns 1024-dimensional vectors.
  * Batches are chunked to stay within the API's per-request limits.
"""

import logging

import httpx

from app.core.config import Settings
from app.core.exceptions import ConfigurationError, LLMError

logger = logging.getLogger(__name__)

# Conservative per-request batch size to stay within Mistral's input limits.
_MAX_BATCH = 64


def _l2_normalize(vector: list[float]) -> list[float]:
    """Return the L2-normalized copy of ``vector`` (no-op for the zero vector)."""
    norm = sum(component * component for component in vector) ** 0.5
    if norm == 0.0:
        return vector
    return [component / norm for component in vector]


class MistralEmbedder:
    """Concrete ``Embedder`` using the hosted Mistral embeddings API."""

    def __init__(self, settings: Settings) -> None:
        self._model = settings.embedding_model
        self._api_key = settings.mistral_api_key
        self._endpoint = f"{settings.mistral_api_base.rstrip('/')}/embeddings"
        self._client = httpx.Client(timeout=settings.mistral_timeout_seconds)
        logger.info("Using Mistral embeddings model '%s'", self._model)

    def _embed(self, texts: list[str]) -> list[list[float]]:
        """Call the Mistral embeddings API and return normalized vectors."""
        if not self._api_key:
            raise ConfigurationError(
                "MISTRAL_API_KEY is not set; cannot create embeddings."
            )

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        vectors: list[list[float]] = []
        for start in range(0, len(texts), _MAX_BATCH):
            batch = texts[start : start + _MAX_BATCH]
            payload = {"model": self._model, "input": batch}
            try:
                response = self._client.post(
                    self._endpoint, json=payload, headers=headers
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                logger.error(
                    "Mistral embeddings API returned %s: %s",
                    exc.response.status_code,
                    exc.response.text[:500],
                )
                raise LLMError(
                    f"Mistral embeddings API error (HTTP {exc.response.status_code})."
                ) from exc
            except httpx.RequestError as exc:
                logger.exception("Could not reach the Mistral embeddings API")
                raise LLMError("Could not reach the Mistral embeddings API.") from exc

            try:
                data = response.json()
                # Preserve input order (Mistral echoes an `index` per item).
                items = sorted(data["data"], key=lambda item: item["index"])
                vectors.extend(_l2_normalize(item["embedding"]) for item in items)
            except (ValueError, KeyError, IndexError, TypeError) as exc:
                logger.exception("Unexpected Mistral embeddings response shape")
                raise LLMError(
                    "Malformed response from the Mistral embeddings API."
                ) from exc

        return vectors

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts (used during ingestion)."""
        if not texts:
            return []
        return self._embed(texts)

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query string (used during retrieval)."""
        return self._embed([text])[0]
