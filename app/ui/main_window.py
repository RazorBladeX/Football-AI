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
from app.ui.pages.settings import SettingsPage


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
        self.sidebar.addItems(["🏠  Home", "✨  Predictions", "⚙️  Settings"])
        self.sidebar.setMaximumWidth(210)
        self.sidebar.currentRowChanged.connect(self._on_nav_change)

        self.stack = QStackedWidget()
        self.home_page = HomePage(match_service, prediction_service)
        self.predictions_page = PredictionsPage(prediction_service, match_service)
        self.settings_page = SettingsPage()
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.predictions_page)
        self.stack.addWidget(self.settings_page)

        refresh_button = QPushButton("Refresh data")
        refresh_button.clicked.connect(self._safe_refresh)

        header = QFrame()
        header.setObjectName("hero")
        header_layout = QHBoxLayout()
        header_layout.setSpacing(18)

        title = QLabel("Football AI · Command Center")
        title.setStyleSheet("font-size: 24px; font-weight: 800;")
        subtitle = QLabel("Live fixtures, AI-driven scorelines, and ambient monitoring with a Discord-like sheen.")
        subtitle.setWordWrap(True)
        subtitle.setObjectName("muted")

        badge_row = QHBoxLayout()
        badge_row.setSpacing(10)
        live_badge = QFrame()
        live_badge.setObjectName("chip")
        live_badge_layout = QHBoxLayout()
        live_badge_layout.setContentsMargins(10, 6, 10, 6)
        live_badge_layout.setSpacing(6)
        live_badge_layout.addWidget(QLabel("🟢 Live sync"))
        live_badge_layout.addWidget(QLabel("Edge · Local DB"))
        live_badge.setLayout(live_badge_layout)

        trend_badge = QFrame()
        trend_badge.setObjectName("chip")
        trend_badge_layout = QHBoxLayout()
        trend_badge_layout.setContentsMargins(10, 6, 10, 6)
        trend_badge_layout.setSpacing(6)
        trend_badge_layout.addWidget(QLabel("⚡ Rapid refresh"))
        trend_badge_layout.addWidget(QLabel("Anti-boring UI"))
        trend_badge.setLayout(trend_badge_layout)
        badge_row.addWidget(live_badge)
        badge_row.addWidget(trend_badge)
        badge_row.addStretch()

        brand = QVBoxLayout()
        brand.setSpacing(8)
        brand.addWidget(title)
        brand.addWidget(subtitle)
        brand.addLayout(badge_row)

        controls = QVBoxLayout()
        controls.setSpacing(8)
        controls_row = QHBoxLayout()
        controls_row.setSpacing(10)
        controls_row.addWidget(QLabel("Target date"))
        controls_row.addWidget(self.date_picker)
        controls_row.addWidget(self.last_updated)
        controls_row.addItem(QSpacerItem(12, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        controls.addLayout(controls_row)
        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)
        today_button = QPushButton("Jump to today")
        today_button.setObjectName("ghost")
        today_button.clicked.connect(lambda: self.date_picker.setDate(QDate.currentDate()))
        actions_row.addWidget(today_button)
        predictions_button = QPushButton("Open predictions")
        predictions_button.setObjectName("ghost")
        predictions_button.clicked.connect(lambda: self.sidebar.setCurrentRow(1))
        actions_row.addWidget(predictions_button)
        settings_button = QPushButton("Settings")
        settings_button.setObjectName("ghost")
        settings_button.clicked.connect(lambda: self.sidebar.setCurrentRow(2))
        actions_row.addWidget(settings_button)
        actions_row.addWidget(refresh_button)
        controls.addLayout(actions_row)

        header_layout.addLayout(brand, stretch=2)
        header_layout.addLayout(controls, stretch=1)
        header.setLayout(header_layout)

        sidebar_layout = QVBoxLayout()
        brand_label = QLabel("Football AI")
        brand_label.setStyleSheet("font-size: 20px; font-weight: 800; padding: 4px;")
        sub_label = QLabel("Command palette")
        sub_label.setObjectName("muted")
        sidebar_layout.addWidget(brand_label)
        sidebar_layout.addWidget(sub_label)
        sidebar_layout.addSpacing(10)
        sidebar_layout.addWidget(self.sidebar, 1)
        sidebar_layout.addStretch()

        sidebar_container = QFrame()
        sidebar_container.setObjectName("sidebar")
        sidebar_container.setLayout(sidebar_layout)

        root = QWidget()
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(20)
        body_layout.addWidget(sidebar_container)
        body_layout.addWidget(self.stack, stretch=1)

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(16)
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
