"""Application configuration.

Settings are loaded from environment variables (and an optional `.env` file)
using pydantic-settings. This keeps configuration in one typed, validated place
and out of the business logic.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings, sourced from the environment / `.env`."""

    # --- App ---
    app_name: str = "Company RAG Chatbot"
    environment: str = "development"
    debug: bool = True

    # --- API ---
    api_v1_prefix: str = "/api"
    # Comma-separated list of allowed CORS origins (e.g. the Vite dev server).
    cors_origins: str = "http://localhost:5173"

    # --- LLM (Mistral) ---
    mistral_api_key: str = ""
    mistral_api_base: str = "https://api.mistral.ai/v1"
    mistral_model: str = "mistral-small-latest"
    mistral_timeout_seconds: float = 30.0
    mistral_temperature: float = 0.2
    mistral_max_tokens: int = 1024

    # --- Embeddings (Mistral hosted API; 1024-dim vectors) ---
    embedding_model: str = "mistral-embed"

    # --- Retrieval / chat ---
    # Number of chunks to retrieve from FAISS per question.
    top_k_results: int = 4
    # Minimum cosine similarity for a chunk to count as "relevant". If the best
    # retrieved chunk scores below this, the question is treated as out of scope
    # and a polite fallback is returned without calling the LLM.
    # NOTE: calibrated for `mistral-embed` against real document chunks, whose
    # cosine scores compress into a narrow band: ~0.58-0.64 for off-topic text,
    # ~0.71-0.78 for genuinely relevant questions. 0.70 sits in the gap. (Short,
    # misspelled queries can fall into the off-topic band and be rejected.)
    similarity_threshold: float = 0.70

    # --- Ingestion / chunking ---
    chunk_size: int = 1000
    chunk_overlap: int = 200
    # Hard cap on a single upload (25 MB by default).
    max_upload_size_bytes: int = 25 * 1024 * 1024

    # --- Storage paths ---
    database_url: str = "sqlite:///./data/app.db"
    vectorstore_path: str = "./data/vectorstore"
    upload_dir: str = "./data/uploads"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse the comma-separated CORS origins into a clean list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (read env once per process)."""
    return Settings()
