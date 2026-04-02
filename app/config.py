"""Load configuration from environment and `.env` at the project root."""

from pathlib import Path
import logging
import sys

from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_PATH = _PROJECT_ROOT / ".env"

def _configure_logging() -> None:
    """Handlers on root/uvicorn often drop app.*; attach handler to the app logger tree."""
    log = logging.getLogger("app")
    if log.handlers:
        return
    log.setLevel(logging.DEBUG)
    h = logging.StreamHandler(sys.stderr)
    h.setLevel(logging.DEBUG)
    h.setFormatter(logging.Formatter("%(levelname)s [%(name)s] %(message)s"))
    log.addHandler(h)
    log.propagate = False


class Settings(BaseSettings):
    """Values match `env.example`: `POSTGRES_USER` → `postgres_user`, etc."""

    model_config = SettingsConfigDict(
        env_file=_ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # if not .env file, use default values
    postgres_user: str = "postgres"
    postgres_password: str = "password"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "postgres"

    secret_key: str = ""

    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen3:8b"

    anthropic_api_key: str | None = None

    seed_mock_on_start: bool = True

    @property
    def database_url(self) -> str:
        """Get the database URL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        """Синхронный URL для Alembic/сидов (psycopg)."""
        u = self.database_url
        return u.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)


_configure_logging()
settings = Settings()
