import logging
from typing import Dict, List

from sqlalchemy import select

from app.config import settings
from app.database.db import get_session
from app.models.match import Match
from app.models.prediction import Prediction

try:  # pragma: no cover - optional dependency runtime check
    import ollama
except ImportError:  # pragma: no cover
    ollama = None  # type: ignore

logger = logging.getLogger(__name__)


class PredictionService:
    def __init__(self) -> None:
        self.model = settings.ollama_model

    def generate_prediction(self, match: Match) -> Prediction:
        prompt = self._build_prompt(match)
        prediction_data = self._run_model(prompt)
        return self._persist_prediction(match, prediction_data)

    def list_predictions(self) -> List[Prediction]:
        with get_session() as session:
            return session.execute(select(Prediction).order_by(Prediction.created_at.desc())).scalars().all()

    def _persist_prediction(self, match: Match, data: Dict) -> Prediction:
        with get_session() as session:
            prediction = Prediction(
                match_id=match.id,
                model_used=self.model,
                confidence=data.get("confidence"),
                final_score_home=data.get("final_score_home"),
                final_score_away=data.get("final_score_away"),
                first_half_goals=data.get("first_half_goals"),
                second_half_goals=data.get("second_half_goals"),
                total_corners=data.get("total_corners"),
                total_cards=data.get("total_cards"),
                raw_response=data.get("raw_response"),
            )
            session.add(prediction)
            session.flush()
            return prediction

    def _build_prompt(self, match: Match) -> str:
        home_name = match.home_team.name
        away_name = match.away_team.name
        base = [
            f"Predict the match between {home_name} and {away_name}.",
            "Use only the historical scores provided below. Provide numerical outputs.",
        ]
        if match.home_score is not None and match.away_score is not None:
            base.append(f"Latest score: {home_name} {match.home_score} - {match.away_score} {away_name}.")
        return "\n".join(base)

    def _run_model(self, prompt: str) -> Dict:
        if ollama is None:
            logger.warning("Ollama not installed; using deterministic fallback prediction")
            return {
                "confidence": 0.35,
                "final_score_home": 1,
                "final_score_away": 1,
                "first_half_goals": 1,
                "second_half_goals": 1,
                "total_corners": 8,
                "total_cards": 3,
                "raw_response": "fallback-generated",
            }
        response = ollama.generate(model=self.model, prompt=prompt)
        raw_text = response.get("response", "")
        return {
            "confidence": 0.5,
            "final_score_home": 1,
            "final_score_away": 0,
            "first_half_goals": 1,
            "second_half_goals": 0,
            "total_corners": 7,
            "total_cards": 2,
            "raw_response": raw_text,
        }
