import logging
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load environment configuration
load_dotenv()


@dataclass
class Settings:
    """Application configuration loaded from environment variables."""

    _default_db = Path(__file__).resolve().parents[1] / "football_ai.db"
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{_default_db}")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    scrape_primary: str = os.getenv("SCRAPE_PRIMARY", "bbc")
    scrape_fallback: str = os.getenv("SCRAPE_FALLBACK", "espn")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    refresh_interval_seconds: int = int(os.getenv("REFRESH_INTERVAL_SECONDS", "30"))


settings = Settings()


def configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
