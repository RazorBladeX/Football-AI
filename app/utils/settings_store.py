import json
from pathlib import Path
from typing import Dict

SETTINGS_FILE = Path.home() / ".football_ai_settings.json"

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
        merged = DEFAULT_SETTINGS.copy()
        merged.update({k: str(v) for k, v in data.items()})
        return merged
    except Exception:
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: Dict[str, str]) -> None:
    try:
        SETTINGS_FILE.write_text(json.dumps(settings, indent=2))
    except (OSError, PermissionError):
        # Best-effort persistence; ignore write failures to avoid crashing the UI.
        return
