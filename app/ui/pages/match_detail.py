from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.models.match import Match
from app.utils.datetime_utils import format_match_time


class MatchDetailPage(QWidget):
    back_requested = Signal()

    def __init__(self):
        super().__init__()
        self.title = QLabel("Select a match to see details")
        self.title.setStyleSheet("font-size: 22px; font-weight: 800;")
        self.sub_title = QLabel("Choose a fixture from the homepage cards to view the rich overview.")
        self.sub_title.setObjectName("muted")
        self.sub_title.setWordWrap(True)

        self.score_label = QLabel("")
        self.score_label.setStyleSheet("font-size: 32px; font-weight: 900;")

        self.teams_label = QLabel("")
        self.teams_label.setStyleSheet("font-size: 18px; font-weight: 700;")

        self.league_label = QLabel("")
        self.league_label.setObjectName("muted")

        self.status_chip = self._build_chip("Status", "-")
        self.kickoff_chip = self._build_chip("Kickoff", "TBD")

        header_card = QFrame()
        header_card.setObjectName("card")
        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)

        nav_row = QHBoxLayout()
        back_btn = QPushButton("Back to fixtures")
        back_btn.setObjectName("ghost")
        back_btn.clicked.connect(self.back_requested.emit)
        nav_row.addWidget(back_btn)
        nav_row.addStretch()

        header_layout.addLayout(nav_row)
        header_layout.addWidget(self.title)
        header_layout.addWidget(self.sub_title)
        header_card.setLayout(header_layout)

        overview = QFrame()
        overview.setObjectName("panel")
        overview_layout = QVBoxLayout()
        overview_layout.setSpacing(12)

        score_row = QHBoxLayout()
        score_row.addWidget(self.teams_label)
        score_row.addStretch()
        score_row.addWidget(self.score_label)

        chips_row = QHBoxLayout()
        chips_row.setSpacing(10)
        chips_row.addWidget(self.status_chip)
        chips_row.addWidget(self.kickoff_chip)
        chips_row.addStretch()

        overview_layout.addLayout(score_row)
        overview_layout.addLayout(chips_row)
        overview_layout.addWidget(self.league_label)
        overview.setLayout(overview_layout)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        grid.addWidget(overview, 0, 0, 1, 2)

        root = QVBoxLayout()
        root.setSpacing(14)
        root.addWidget(header_card)
        root.addLayout(grid)
        root.addStretch()
        self.setLayout(root)

    def set_match_data(self, match: dict) -> None:
        home = match.get("home", "Home")
        away = match.get("away", "Away")
        self.title.setText(f"{home} vs {away}")
        self.teams_label.setText(f"{home} · {away}")
        self.score_label.setText(self._format_score(match))
        self.league_label.setText(f"Competition · {match.get('league', 'Unknown')}")
        kickoff_display = self._format_kickoff(match.get("kickoff"))
        self._set_chip_text(self.status_chip, match.get("status", "upcoming").title())
        self._set_chip_text(self.kickoff_chip, kickoff_display)

    def set_match(self, match: Match) -> None:
        payload = {
            "home": match.home_team.name,
            "away": match.away_team.name,
            "league": match.league.name,
            "status": match.status,
            "home_score": match.home_score,
            "away_score": match.away_score,
            "kickoff": match.kickoff_utc.isoformat() if match.kickoff_utc else None,
        }
        self.set_match_data(payload)

    def _format_score(self, match: dict) -> str:
        if match.get("home_score") is None or match.get("away_score") is None:
            return "Awaiting kickoff"
        return f"{match['home_score']} - {match['away_score']}"

    def _format_kickoff(self, kickoff_raw) -> str:
        if isinstance(kickoff_raw, datetime):
            return format_match_time(kickoff_raw)
        if isinstance(kickoff_raw, str):
            try:
                parsed = datetime.fromisoformat(kickoff_raw.replace("Z", "+00:00"))
                return format_match_time(parsed)
            except ValueError:
                return kickoff_raw.replace("T", " ").replace("Z", "")
        return "TBD"

    def _build_chip(self, label: str, value: str) -> QFrame:
        chip = QFrame()
        chip.setObjectName("pill")
        layout = QVBoxLayout()
        title = QLabel(label)
        title.setObjectName("muted")
        val = QLabel(value)
        val.setStyleSheet("font-weight: 800;")
        layout.addWidget(title)
        layout.addWidget(val)
        chip.setLayout(layout)
        return chip

    def _set_chip_text(self, chip: QFrame, value: str) -> None:
        if chip.layout() and chip.layout().count() > 1:
            label = chip.layout().itemAt(1).widget()
            if isinstance(label, QLabel):
                label.setText(value)
