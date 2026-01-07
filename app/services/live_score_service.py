import logging
import threading
import time
from datetime import date, datetime

from app.config import settings
from app.services.match_service import MatchService
from app.services.scraper_service import ScraperService
from app.utils.datetime_utils import utc_now

logger = logging.getLogger(__name__)


class LiveScoreService:
    def __init__(self, scraper: ScraperService, matches: MatchService):
        self.scraper = scraper
        self.matches = matches
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _run_loop(self) -> None:
        while self._running:
            try:
                self.refresh_today()
            except Exception as exc:
                logger.error("Background refresh failed: %s", exc)
            time.sleep(settings.refresh_interval_seconds)

    def refresh_today(self) -> None:
        today = date.fromtimestamp(time.time())
        fixtures = self.scraper.get_fixtures(today)
        for item in fixtures:
            try:
                league = self.matches.ensure_league(item["league"], tier=1)
                home = self.matches.ensure_team(item["home"], league)
                away = self.matches.ensure_team(item["away"], league)
                kickoff = None
                if item.get("kickoff"):
                    kickoff = datetime.fromisoformat(item["kickoff"].replace("Z", "+00:00"))
                status = item.get("status", "upcoming").lower()
                if status in {"live", "in progress"}:
                    status = "live"
                self.matches.upsert_match(
                    league=league,
                    home_team=home,
                    away_team=away,
                    kickoff=kickoff,
                    status=status,
                    home_score=item.get("home_score"),
                    away_score=item.get("away_score"),
                )
            except Exception as exc:
                logger.warning("Skipping fixture due to error: %s", exc)
