from datetime import date
from PySide6.QtWidgets import (
    QHBoxLayout,
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

        refresh_button = QPushButton("Refresh Now")
        refresh_button.clicked.connect(lambda: self.refresh_matches(date.today()))

        layout = QVBoxLayout()
        layout.addWidget(self.sidebar)
        layout.addWidget(refresh_button)

        sidebar_container = QWidget()
        sidebar_container.setLayout(layout)

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
        for item in fixtures:
            league = self.match_service.ensure_league(item["league"], tier=1)
            home = self.match_service.ensure_team(item["home"], league)
            away = self.match_service.ensure_team(item["away"], league)
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
