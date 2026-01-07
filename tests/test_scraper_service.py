import unittest
from datetime import date

from app.services.scraper_service import ScraperService


class _MockResponse:
    def __init__(self, text=None, json_data=None, status=200):
        self.text = text or ""
        self._json = json_data
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("HTTP error")

    def json(self):
        return self._json


BBC_HTML = """
<html><body>
<h3>Premier League</h3>
<article class="gs-o-list-ui__item--flush">
  <span class="sp-c-fixture__team--home"><span class="sp-c-fixture__team-name">Arsenal</span></span>
  <span class="sp-c-fixture__team--away"><span class="sp-c-fixture__team-name">Chelsea</span></span>
  <span class="sp-c-fixture__status">FT</span>
  <span class="sp-c-fixture__number--home">2</span>
  <span class="sp-c-fixture__number--away">1</span>
  <time datetime="2026-01-07T20:00:00Z"></time>
</article>
</body></html>
"""

ESPN_JSON = {
    "events": [
        {
            "date": "2026-01-07T20:00Z",
            "status": {"type": {"name": "in progress"}},
            "competitions": [
                {
                    "league": {"name": "ESPN League"},
                    "competitors": [
                        {"homeAway": "home", "team": {"displayName": "Leeds"}, "score": "0"},
                        {"homeAway": "away", "team": {"displayName": "Leicester"}, "score": "1"},
                    ],
                }
            ],
        }
    ]
}


class ScraperServiceTests(unittest.TestCase):
    def test_bbc_scrape_parses_fixture(self):
        service = ScraperService()

        def fake_get(url, timeout=15):
            return _MockResponse(text=BBC_HTML)

        original = service._scrape_bbc
        service._scrape_bbc = original.__get__(service)  # type: ignore
        # patch requests.get used inside scraper
        import app.services.scraper_service as scr_mod

        scr_mod.requests.get = fake_get  # type: ignore
        fixtures = service.get_fixtures(date(2026, 1, 7))
        self.assertEqual(len(fixtures), 1)
        self.assertEqual(fixtures[0]["home"], "Arsenal")
        self.assertEqual(fixtures[0]["home_score"], 2)

    def test_fallback_to_espn(self):
        service = ScraperService()

        def failing_bbc(_):
            raise ValueError("fail bbc")

        def fake_get(url, timeout=15):
            return _MockResponse(json_data=ESPN_JSON)

        service._scrape_bbc = failing_bbc  # type: ignore
        import app.services.scraper_service as scr_mod

        scr_mod.requests.get = fake_get  # type: ignore
        fixtures = service.get_fixtures(date(2026, 1, 8))
        self.assertEqual(fixtures[0]["home"], "Leeds")
        self.assertEqual(fixtures[0]["status"], "in progress")


if __name__ == "__main__":
    unittest.main()
