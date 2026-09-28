from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, overridable through environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    app_name: str = "AI Powered Banking Service"

    environment: str = "local"

    log_level: str = "INFO"

    # SQLite keeps local development dependency free.
    # docker-compose overrides this with a PostgreSQL URL.
    database_url: str = "sqlite:///./banking.db"

    sql_echo: bool = False

    jwt_secret_key: str = "local-development-secret-change-me"

    jwt_algorithm: str = "HS256"

    jwt_access_token_expire_minutes: int = 60

    # Redis is optional. When it is not configured, idempotency is disabled.
    redis_url: str | None = None

    idempotency_ttl_seconds: int = 86_400

    risk_prediction_enabled: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
