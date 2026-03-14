from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    app_name: str = "websentix"
    environment: str = "development"
    debug: bool = False

    model_name: str = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
    request_timeout: int = 12
    max_content_chars: int = 12000
    history_file: str = str(BASE_DIR / "data" / "analysis_history.json")
    user_agent: str = "Mozilla/5.0 (compatible; WebSentix/1.0; +https://localhost)"
    log_level: str = "INFO"
    host: str = "127.0.0.1"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
