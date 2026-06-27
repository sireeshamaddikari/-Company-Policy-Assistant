"""Mistral LLM client.

Implements the ``LLMClient`` protocol by calling the Mistral chat-completions
REST API via httpx. All provider/transport concerns (auth, payload shape,
error mapping) live here; callers only see ``generate(system, user) -> str``.
"""

import logging

import httpx

from app.core.config import Settings
from app.core.exceptions import ConfigurationError, LLMError

logger = logging.getLogger(__name__)


class MistralClient:
    """Concrete ``LLMClient`` backed by the Mistral API."""

    def __init__(self, settings: Settings) -> None:
        self._model = settings.mistral_model
        self._temperature = settings.mistral_temperature
        self._max_tokens = settings.mistral_max_tokens
        self._api_key = settings.mistral_api_key
        self._endpoint = f"{settings.mistral_api_base.rstrip('/')}/chat/completions"
        # Reused across requests (connection pooling).
        self._client = httpx.Client(timeout=settings.mistral_timeout_seconds)

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Call Mistral and return the assistant's message content."""
        if not self._api_key:
            raise ConfigurationError(
                "MISTRAL_API_KEY is not set; cannot call the language model."
            )

        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = self._client.post(self._endpoint, json=payload, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Mistral API returned %s: %s",
                exc.response.status_code,
                exc.response.text[:500],
            )
            raise LLMError(
                f"Mistral API error (HTTP {exc.response.status_code})."
            ) from exc
        except httpx.RequestError as exc:
            logger.exception("Could not reach the Mistral API")
            raise LLMError("Could not reach the Mistral API.") from exc

        try:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError) as exc:
            logger.exception("Unexpected Mistral API response shape")
            raise LLMError("Malformed response from the Mistral API.") from exc

        if not content or not content.strip():
            raise LLMError("The Mistral API returned an empty answer.")
        return content.strip()
