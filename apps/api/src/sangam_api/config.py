"""
Application configuration using pydantic-settings.
Environment variables are loaded from .env files automatically.
"""

from typing import List
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "SANGAM API"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://sangam:sangam@localhost:5432/sangam"
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Security
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30  # Short-lived access tokens
    refresh_token_expire_days: int = 7  # Longer-lived refresh tokens
    
    # Development seed users (only used in development environment)
    dev_seed_users: str = ""  # JSON array of seed users, e.g., [{"email":"...","password":"...","roles":["admin"]}]

    # ML Service
    ml_service_url: str = "http://localhost:8001"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance (singleton pattern)."""
    return Settings()
