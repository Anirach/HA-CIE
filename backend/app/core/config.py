"""Application configuration settings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "Hospital Accreditation Causal Insight Engine"
    app_debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production"

    # Storage
    storage_mode: str = "json"  # 'json' or 'postgres'
    data_dir: str = "../data"

    # Database
    database_url: Optional[str] = None

    # Neo4j
    neo4j_uri: Optional[str] = None
    neo4j_user: str = "neo4j"
    neo4j_password: Optional[str] = None

    # JWT
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


settings = Settings()
