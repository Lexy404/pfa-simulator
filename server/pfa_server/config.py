"""Server settings, read from environment variables (prefix PFA_) or server/.env."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

SERVER_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PFA_",
        env_file=SERVER_DIR / ".env",
        extra="ignore",
    )

    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen3:4b-instruct-2507-q4_K_M"
    host: str = "0.0.0.0"
    port: int = 8000
    persona: str = "burning_building"
    personas_dir: Path = SERVER_DIR / "personas"


@lru_cache
def get_settings() -> Settings:
    return Settings()
