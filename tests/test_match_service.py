import unittest
from datetime import datetime

from app.database.db import engine
from app.database.db import init_db
from app.models import league, team, match, prediction, match_stats  # noqa: F401
from app.models.base import Base
from app.services.match_service import MatchService


class MatchServiceTests(unittest.TestCase):
    def setUp(self):
        # Reset schema for deterministic tests
        Base.metadata.drop_all(bind=engine)
        init_db()
        self.service = MatchService()
        league = self.service.ensure_league("Test League", tier=1)
        home = self.service.ensure_team("Home FC", league)
        away = self.service.ensure_team("Away FC", league)
        match = self.service.upsert_match(
            league=league,
            home_team=home,
            away_team=away,
            kickoff=datetime(2026, 1, 7, 12, 0),
            status="upcoming",
            home_score=None,
            away_score=None,
        )
        self.match_id = match.id

    def test_get_match_eager_loads_teams(self):
        match = self.service.get_match(self.match_id)
        self.assertIsNotNone(match)
        self.assertEqual(match.home_team.name, "Home FC")
        self.assertEqual(match.away_team.name, "Away FC")

    def test_get_match_missing_returns_none(self):
        self.assertIsNone(self.service.get_match(9999))


if __name__ == "__main__":
    unittest.main()
