import sys
from datetime import date

from PySide6.QtWidgets import QApplication

from app.config import configure_logging
from app.database.db import init_db
from app.database.migrations import run_migrations
from app.services.live_score_service import LiveScoreService
from app.services.match_service import MatchService
from app.services.prediction_service import PredictionService
from app.services.scraper_service import ScraperService
from app.ui.main_window import MainWindow
from app.ui.theme import apply_dark_palette


def bootstrap():
    configure_logging()
    init_db()
    run_migrations()

    scraper = ScraperService()
    match_service = MatchService()
    prediction_service = PredictionService()

    # Prime database with today's fixtures
    live_service = LiveScoreService(scraper, match_service)
    live_service.refresh_today()
    live_service.start()

    app = QApplication(sys.argv)
    apply_dark_palette(app)
    window = MainWindow(
        match_service=match_service,
        prediction_service=prediction_service,
        scraper_service=scraper,
        live_service=live_service,
    )
    window.refresh_matches(date.today())
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    bootstrap()
