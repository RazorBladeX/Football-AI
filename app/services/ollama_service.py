import logging
from typing import Dict

from app.config import settings

try:  # pragma: no cover - optional runtime dependency
    import ollama
except ImportError:  # pragma: no cover
    ollama = None  # type: ignore

logger = logging.getLogger(__name__)


class OllamaService:
    def __init__(self) -> None:
        self.model = settings.ollama_model

    def generate(self, prompt: str) -> Dict:
        if ollama is None:
            logger.warning("Ollama not installed; returning fallback response")
            return {"response": "ollama-not-installed"}
        return ollama.generate(model=self.model, prompt=prompt)
