import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

from app.services.live_score_service import LiveScoreService


class _DummyScraper:
    def __init__(self):
        self.calls: list[date] = []

    def get_fixtures(self, target_date: date):
        self.calls.append(target_date)
        return [
            {
                "league": "Test League",
                "home": "Alpha",
                "away": "Beta",
                "status": "upcoming",
                "home_score": None,
                "away_score": None,
            }
        ]


class _FailingScraper:
    def get_fixtures(self, target_date: date):
        raise RuntimeError(f"no fixtures for {target_date}")


class _DummyMatchService:
    def ensure_league(self, name: str, tier: int = 1, session=None):
        return SimpleNamespace(id=1, name=name)

    def ensure_team(self, name: str, league, session=None):
        return SimpleNamespace(id=hash(name) % 10_000, name=name)

    def upsert_match(
        self,
        league,
        home_team,
        away_team,
        kickoff,
        status,
        home_score,
        away_score,
        venue=None,
    ):
        return SimpleNamespace()


class LiveScoreServiceTests(unittest.TestCase):
    @patch("app.services.live_score_service.load_settings", return_value={"scrape_days_ahead": "1"})
    @patch("app.services.live_score_service.date")
    def test_refresh_window_respects_horizon(self, mock_date, _mock_settings):
        class _FakeDate(date):
            @classmethod
            def fromtimestamp(cls, _ts):
                return date(2000, 1, 1)

        mock_date.fromtimestamp.side_effect = _FakeDate.fromtimestamp
        scraper = _DummyScraper()
        service = LiveScoreService(scraper, _DummyMatchService())

        service.refresh_window()

        self.assertEqual(len(scraper.calls), 2)
        self.assertEqual(scraper.calls[0], date(2000, 1, 1))
        self.assertEqual(scraper.calls[1], date(2000, 1, 2))

    def test_refresh_window_skips_scraper_errors(self):
        service = LiveScoreService(_FailingScraper(), _DummyMatchService())
        try:
            service.refresh_window(days_ahead=0)
        except Exception as exc:
            self.fail(f"refresh_window should swallow scraper errors, got: {exc}")


if __name__ == "__main__":
    unittest.main()
