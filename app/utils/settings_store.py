import json
import logging
from pathlib import Path
from typing import Dict

SETTINGS_DIR = Path.home() / ".config" / "football_ai"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

DEFAULT_SETTINGS: Dict[str, str] = {
    "ollama_mode": "cloud",  # cloud | local | remote
    "ollama_api_key": "",
    "ollama_host": "http://localhost",
    "ollama_port": "11434",
    "ollama_model": "llama3",
    "refresh_interval_minutes": "15",
}


def load_settings() -> Dict[str, str]:
    if not SETTINGS_FILE.exists():
        return DEFAULT_SETTINGS.copy()
    try:
        data = json.loads(SETTINGS_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return DEFAULT_SETTINGS.copy()
    merged = DEFAULT_SETTINGS.copy()
    merged.update(data)
    return merged


def save_settings(settings: Dict[str, str]) -> None:
    try:
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        SETTINGS_FILE.write_text(json.dumps(settings, indent=2))
    except (OSError, PermissionError):
        logging.getLogger(__name__).warning("Unable to persist settings to %s", SETTINGS_FILE)
