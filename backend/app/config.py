"""Clariq Backend Configuration."""
from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- Core ---
    APP_NAME: str = "clariq-backend"
    APP_VERSION: str = "0.1.0"
    LOG_LEVEL: str = "INFO"

    # --- Database ---
    DATABASE_URL: str = "sqlite+aiosqlite:///./clariq.db"

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:5173"

    # --- SerpApi ---
    SERPAPI_API_KEY: str = ""

    # --- LLM ---
    LLM_API_KEY: str = ""

    # --- HTTP Client ---
    MAX_RETRIES: int = 2
    REQUEST_TIMEOUT: int = 15

    # --- Search Cache ---
    CACHE_TTL: int = 3600          # seconds; 1 hour default
    MAX_QUERIES: int = 50          # max total SerpApi calls per analysis
    MAX_RESULTS_PER_QUERY: int = 10  # default results per engine call

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
