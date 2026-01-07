from datetime import date
import logging

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.services.live_score_service import LiveScoreService
from app.services.match_service import MatchService
from app.services.prediction_service import PredictionService
from app.services.scraper_service import ScraperService
from app.database.db import get_session
from app.ui.pages.home import HomePage
from app.ui.pages.predictions import PredictionsPage


class MainWindow(QMainWindow):
    def __init__(
        self,
        match_service: MatchService,
        prediction_service: PredictionService,
        scraper_service: ScraperService,
        live_service: LiveScoreService,
    ):
        super().__init__()
        self.setWindowTitle("Football AI Dashboard")
        self.resize(1200, 800)
        self.match_service = match_service
        self.prediction_service = prediction_service
        self.scraper_service = scraper_service
        self.live_service = live_service

        self.sidebar = QListWidget()
        self.sidebar.addItems(["Home", "Predictions", "Settings"])
        self.sidebar.setMaximumWidth(180)
        self.sidebar.currentRowChanged.connect(self._on_nav_change)

        self.stack = QStackedWidget()
        self.home_page = HomePage(match_service, prediction_service)
        self.predictions_page = PredictionsPage(prediction_service)
        self.settings_page = QWidget()
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.predictions_page)
        self.stack.addWidget(self.settings_page)

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self._safe_refresh)

        sidebar_layout = QVBoxLayout()
        brand = QLabel("Football AI")
        brand.setStyleSheet("font-size: 20px; font-weight: 700; padding: 12px 8px;")
        sidebar_layout.addWidget(brand)
        sidebar_layout.addWidget(self.sidebar, 1)
        sidebar_layout.addWidget(refresh_button)

        sidebar_container = QFrame()
        sidebar_container.setObjectName("card")
        sidebar_container.setLayout(sidebar_layout)

        root = QWidget()
        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(sidebar_container)
        root_layout.addWidget(self.stack, stretch=1)
        root.setLayout(root_layout)

        self.setCentralWidget(root)
        self.sidebar.setCurrentRow(0)

    def _on_nav_change(self, index: int) -> None:
        self.stack.setCurrentIndex(index)

    def refresh_matches(self, target_date: date) -> None:
        fixtures = self.scraper_service.get_fixtures(target_date)
        rows = []
        with get_session() as session:
            for item in fixtures:
                league = self.match_service.ensure_league(item["league"], tier=1, session=session)
                home = self.match_service.ensure_team(item["home"], league, session=session)
                away = self.match_service.ensure_team(item["away"], league, session=session)
                self.match_service.upsert_match(
                    league=league,
                    home_team=home,
                    away_team=away,
                    kickoff=None,
                    status=item.get("status", "upcoming"),
                    home_score=item.get("home_score"),
                    away_score=item.get("away_score"),
                )
                rows.append(item)
        self.home_page.load_matches(rows)

    def _safe_refresh(self):
        try:
            self.refresh_matches(date.today())
        except Exception as exc:
            logging.getLogger(__name__).error("Refresh failed: %s", exc)
