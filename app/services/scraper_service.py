import logging
from datetime import date
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

from app.config import settings
from app.utils.caching import ttl_cache
from app.utils.rate_limit import RateLimiter


def safe_int(text: str | None) -> int | None:
    if text is None:
        return None
    try:
        return int(text)
    except (ValueError, TypeError):
        return None

logger = logging.getLogger(__name__)


class ScraperService:
    def __init__(self):
        self.rate_limiter = RateLimiter(1.0)
        self.primary = settings.scrape_primary.lower()
        self.fallback = settings.scrape_fallback.lower()

    @ttl_cache(ttl_seconds=120)
    def get_fixtures(self, target_date: date) -> List[Dict]:
        """Return fixtures and results for the given date, primary source BBC with ESPN fallback."""
        order = [self.primary, self.fallback]
        for source in order:
            try:
                if source == "bbc":
                    return self._scrape_bbc(target_date)
                if source == "espn":
                    return self._scrape_espn(target_date)
            except Exception as exc:
                logger.warning("%s scrape failed, trying next: %s", source.upper(), exc)
        raise ValueError("All scrapers failed")

    def _scrape_bbc(self, target_date: date) -> List[Dict]:
        url = f"https://www.bbc.co.uk/sport/football/scores-fixtures/{target_date.isoformat()}"
        with self.rate_limiter.wait():
            response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        fixtures: List[Dict] = []

        for fixture in soup.select("article.gs-o-list-ui__item--flush"):
            league = fixture.find_previous("h3")
            league_name = league.get_text(strip=True) if league else "Unknown"
            home = fixture.select_one("span.sp-c-fixture__team--home .sp-c-fixture__team-name")
            away = fixture.select_one("span.sp-c-fixture__team--away .sp-c-fixture__team-name")
            status_el = fixture.select_one("span.sp-c-fixture__status")
            score_home = fixture.select_one("span.sp-c-fixture__number--home")
            score_away = fixture.select_one("span.sp-c-fixture__number--away")
            kickoff = fixture.select_one("time")
            if not home or not away:
                continue
            fixtures.append(
                {
                    "league": league_name,
                    "home": home.get_text(strip=True),
                    "away": away.get_text(strip=True),
                    "status": status_el.get_text(strip=True) if status_el else "upcoming",
                    "home_score": safe_int(score_home.get_text(strip=True) if score_home else None),
                    "away_score": safe_int(score_away.get_text(strip=True) if score_away else None),
                    "kickoff": kickoff["datetime"] if kickoff and kickoff.has_attr("datetime") else None,
                }
            )
        if not fixtures:
            raise ValueError(f"BBC returned no fixtures for {target_date} ({url})")
        return fixtures

    def _scrape_espn(self, target_date: date) -> List[Dict]:
        url = f"https://site.api.espn.com/apis/v2/sports/soccer/eng.1/scoreboard?dates={target_date.strftime('%Y%m%d')}"
        with self.rate_limiter.wait():
            response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        fixtures: List[Dict] = []
        events = data.get("events", [])
        for event in events:
            competitions = event.get("competitions", [])
            if not competitions:
                continue
            comp = competitions[0]
            competitors = {c["homeAway"]: c for c in comp.get("competitors", [])}
            status = event.get("status", {}).get("type", {}).get("name", "upcoming").lower()
            if status == "in progress":
                status = "live"
            fixtures.append(
                {
                    "league": comp.get("league", {}).get("name", "ESPN England"),
                    "home": competitors.get("home", {}).get("team", {}).get("displayName"),
                    "away": competitors.get("away", {}).get("team", {}).get("displayName"),
                    "status": status,
                    "home_score": safe_int(competitors.get("home", {}).get("score")),
                    "away_score": safe_int(competitors.get("away", {}).get("score")),
                    "kickoff": event.get("date"),
                }
            )
        if not fixtures:
            logger.debug("ESPN response payload keys: %s", list(data.keys()))
            raise ValueError(f"ESPN returned no fixtures for {target_date} ({url}) - events: {len(events)}")
        return fixtures
