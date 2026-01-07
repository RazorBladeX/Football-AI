from datetime import date
import logging

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QDateEdit,
    QSizePolicy,
    QSpacerItem,
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

        self.date_picker = QDateEdit(QDate.currentDate())
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDisplayFormat("MMM d, yyyy")
        self.date_picker.dateChanged.connect(self._on_date_change)

        self.last_updated = QLabel("Synced · not yet refreshed")
        self.last_updated.setObjectName("muted")

        self.sidebar = QListWidget()
        self.sidebar.addItems(["Home", "Predictions", "Settings"])
        self.sidebar.setMaximumWidth(180)
        self.sidebar.currentRowChanged.connect(self._on_nav_change)

        self.stack = QStackedWidget()
        self.home_page = HomePage(match_service, prediction_service)
        self.predictions_page = PredictionsPage(prediction_service, match_service)
        self.settings_page = self._build_settings_page()
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.predictions_page)
        self.stack.addWidget(self.settings_page)

        refresh_button = QPushButton("Refresh data")
        refresh_button.clicked.connect(self._safe_refresh)

        header = QFrame()
        header.setObjectName("toolbar")
        header_layout = QHBoxLayout()
        title = QLabel("Football AI Control Room")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        subtitle = QLabel("Live fixtures, on-device predictions, modern dark UI")
        subtitle.setObjectName("muted")
        brand = QVBoxLayout()
        brand.addWidget(title)
        brand.addWidget(subtitle)
        controls = QHBoxLayout()
        controls.setSpacing(12)
        controls.addWidget(QLabel("Target date"))
        controls.addWidget(self.date_picker)
        controls.addItem(QSpacerItem(24, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        controls.addWidget(self.last_updated)
        controls.addWidget(refresh_button)
        header_layout.addLayout(brand, stretch=1)
        header_layout.addLayout(controls, stretch=0)
        header.setLayout(header_layout)

        sidebar_layout = QVBoxLayout()
        brand_label = QLabel("Dashboard")
        brand_label.setStyleSheet("font-size: 18px; font-weight: 700; padding: 12px 8px;")
        sidebar_layout.addWidget(brand_label)
        sidebar_layout.addWidget(self.sidebar, 1)

        sidebar_container = QFrame()
        sidebar_container.setObjectName("card")
        sidebar_container.setLayout(sidebar_layout)

        root = QWidget()
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(16)
        body_layout.addWidget(sidebar_container)
        body_layout.addWidget(self.stack, stretch=1)

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)
        root_layout.addWidget(header)
        root_layout.addLayout(body_layout)
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
        self.home_page.load_matches(rows, target_date)
        self.predictions_page.reload_matches(target_date)
        self.last_updated.setText(f"Synced {len(rows)} fixtures · {target_date.strftime('%b %d')}")

    def _safe_refresh(self):
        qdate = self.date_picker.date()
        selected_date = qdate.toPython() if hasattr(qdate, "toPython") else qdate.toPyDate()
        try:
            self.refresh_matches(selected_date)
        except Exception as exc:
            logging.getLogger(__name__).error("Refresh failed: %s", exc)

    def _on_date_change(self, target: QDate) -> None:
        self._safe_refresh()

    def _build_settings_page(self) -> QWidget:
        container = QFrame()
        container.setObjectName("card")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Settings & System"))
        description = QLabel(
            "This lightweight desktop app runs entirely on your machine, using BBC/ESPN feeds and optional Ollama models "
            "to provide quick match insights. Adjust environment variables to change models or scrape sources."
        )
        description.setWordWrap(True)
        description.setObjectName("muted")
        layout.addWidget(description)
        container.setLayout(layout)
        shell = QWidget()
        shell_layout = QVBoxLayout()
        shell_layout.addWidget(container)
        shell.setLayout(shell_layout)
        return shell
