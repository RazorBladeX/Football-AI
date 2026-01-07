from typing import List, Optional
from datetime import datetime

import matplotlib

matplotlib.use("Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.services.match_service import MatchService
from app.services.prediction_service import PredictionService


class HomePage(QWidget):
    match_selected = Signal(dict)

    def __init__(self, match_service: MatchService, prediction_service: PredictionService):
        super().__init__()
        self.match_service = match_service
        self.prediction_service = prediction_service
        self.rows: List[dict] = []

        self.status_label = QLabel("Today's fixtures")
        self.status_label.setStyleSheet("font-size: 20px; font-weight: 800;")
        self.sub_status = QLabel("Live English football pulse, refreshed frequently.")
        self.sub_status.setObjectName("muted")

        self.figure = Figure(figsize=(4, 2), facecolor="#0f172a")
        self.canvas = FigureCanvasQTAgg(self.figure)

        self.metrics = self._build_metrics_row()

        hero_card = QFrame()
        hero_card.setObjectName("card")
        hero_layout = QVBoxLayout()
        hero_layout.setSpacing(10)
        hero_layout.addWidget(self.status_label)
        hero_layout.addWidget(self.sub_status)
        hero_layout.addLayout(self.metrics)
        hero_card.setLayout(hero_layout)

        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(12)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setColumnStretch(0, 1)
        self.cards_layout.setColumnStretch(1, 1)
        cards_body = QWidget()
        cards_body.setLayout(self.cards_layout)

        self.cards_area = QScrollArea()
        self.cards_area.setWidgetResizable(True)
        self.cards_area.setObjectName("plain-scroll")
        self.cards_area.setWidget(cards_body)

        cards_card = QFrame()
        cards_card.setObjectName("panel")
        cards_layout = QVBoxLayout()
        cards_header = QHBoxLayout()
        cards_title = QLabel("Fixture cards")
        cards_title.setStyleSheet("font-size: 16px; font-weight: 700;")
        cards_subtitle = QLabel("Tap a game for the dedicated overview page.")
        cards_subtitle.setObjectName("muted")
        cards_header.addWidget(cards_title)
        cards_header.addStretch()
        cards_layout.addLayout(cards_header)
        cards_layout.addWidget(cards_subtitle)
        cards_layout.addWidget(self.cards_area)
        cards_card.setLayout(cards_layout)

        chart_card = QFrame()
        chart_card.setObjectName("panel")
        chart_layout = QVBoxLayout()
        chart_title = QLabel("Status mix")
        chart_title.setStyleSheet("font-size: 16px; font-weight: 700;")
        chart_subtitle = QLabel("Quick glance of live vs finished vs upcoming fixtures.")
        chart_subtitle.setObjectName("muted")
        chart_layout.addWidget(chart_title)
        chart_layout.addWidget(chart_subtitle)
        chart_layout.addWidget(self.canvas)
        chart_card.setLayout(chart_layout)

        grid = QGridLayout()
        grid.setSpacing(14)
        grid.addWidget(cards_card, 0, 0, 2, 2)
        grid.addWidget(chart_card, 0, 2, 1, 1)
        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 3)
        grid.setColumnStretch(2, 2)

        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.addWidget(hero_card)
        layout.addLayout(grid)
        self.setLayout(layout)

    def load_matches(self, rows: List[dict], target_date) -> None:
        self.rows = rows
        self._clear_cards()
        if not rows:
            self._show_empty_message("No fixtures available for this date.")
        for idx, match in enumerate(rows):
            card = self._build_match_card(match)
            self.cards_layout.addWidget(card, idx // 2, idx % 2)
        self.status_label.setText(f"Loaded {len(rows)} fixtures")
        self.sub_status.setText(f"Viewing fixtures for {target_date.strftime('%b %d, %Y')}")
        status_counts = self._count_statuses(rows)
        self._render_chart(status_counts)
        self._update_metrics(status_counts)

    def _render_chart(self, status_counts: dict) -> None:
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        bars = list(status_counts.keys())
        values = list(status_counts.values())
        ax.bar(bars, values, color=["#22c55e", "#3b82f6", "#6b7280"], alpha=0.9)
        ax.set_facecolor("#111827")
        self.figure.patch.set_facecolor("#111827")
        ax.tick_params(colors="#e5e7eb")
        for spine in ax.spines.values():
            spine.set_color("#374151")
        ax.set_title("Match status mix", color="#e5e7eb")
        self.canvas.draw_idle()

    def _build_metrics_row(self) -> QGridLayout:
        layout = QGridLayout()
        layout.setHorizontalSpacing(18)
        layout.setVerticalSpacing(12)
        self.metric_labels = {}
        for idx, key in enumerate(["upcoming", "live", "finished"]):
            card = QFrame()
            card.setObjectName("pill")
            card_layout = QVBoxLayout()
            title = QLabel(key.capitalize())
            title.setObjectName("muted")
            value = QLabel("0")
            value.setStyleSheet("font-size: 22px; font-weight: 800;")
            card_layout.addWidget(title)
            card_layout.addWidget(value)
            card.setLayout(card_layout)
            layout.addWidget(card, 0, idx)
            self.metric_labels[key] = value
        return layout

    def _update_metrics(self, status_counts: dict) -> None:
        for key, label in self.metric_labels.items():
            label.setText(str(status_counts.get(key, 0)))

    def _count_statuses(self, rows: List[dict]) -> dict:
        status_counts = {"live": 0, "finished": 0, "upcoming": 0}
        for m in rows:
            status = m.get("status", "upcoming").lower()
            if status not in status_counts:
                status_counts["upcoming"] += 1
                continue
            status_counts[status] += 1
        return status_counts

    def _clear_cards(self) -> None:
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _show_empty_message(self, message: str) -> None:
        placeholder = QLabel(message)
        placeholder.setObjectName("muted")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder_card = QFrame()
        placeholder_card.setObjectName("panel")
        placeholder_layout = QVBoxLayout()
        placeholder_layout.addWidget(placeholder)
        placeholder_card.setLayout(placeholder_layout)
        self.cards_layout.addWidget(placeholder_card, 0, 0, 1, 2)

    def show_empty_state(self, target_date, reason: Optional[str] = None) -> None:
        self.rows = []
        self._clear_cards()
        detail = reason or "No data returned by providers."
        self._show_empty_message(detail)
        self.status_label.setText("No fixtures found")
        self.sub_status.setText(f"{target_date.strftime('%b %d, %Y')} · {detail}")
        self._render_chart({"live": 0, "finished": 0, "upcoming": 0})
        self._update_metrics({})

    def _build_match_card(self, match: dict) -> QFrame:
        card = QFrame()
        card.setObjectName("panel")
        layout = QVBoxLayout()
        layout.setSpacing(8)

        header = QHBoxLayout()
        league_label = QLabel(match.get("league", "Unknown"))
        league_label.setObjectName("muted")
        status_chip = QFrame()
        status_chip.setObjectName("pill")
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(10, 6, 10, 6)
        status_layout.setSpacing(6)
        status_label = QLabel(match.get("status", "upcoming").title())
        status_layout.addWidget(status_label)
        status_chip.setLayout(status_layout)
        header.addWidget(league_label)
        header.addStretch()
        header.addWidget(status_chip)

        teams_row = QHBoxLayout()
        teams_row.setSpacing(6)
        home = QLabel(match.get("home", "Home"))
        home.setStyleSheet("font-size: 16px; font-weight: 800;")
        away = QLabel(match.get("away", "Away"))
        away.setStyleSheet("font-size: 16px; font-weight: 800;")
        vs = QLabel("vs")
        vs.setObjectName("muted")
        score = QLabel(self._format_score(match))
        score.setStyleSheet("font-size: 22px; font-weight: 800;")
        teams_row.addWidget(home)
        teams_row.addWidget(vs)
        teams_row.addWidget(away)
        teams_row.addStretch()
        teams_row.addWidget(score)

        meta_row = QHBoxLayout()
        kickoff_label = QLabel(f"Kickoff · {self._format_kickoff_time(match.get('kickoff'))}")
        kickoff_label.setObjectName("muted")
        meta_row.addWidget(kickoff_label)
        meta_row.addStretch()
        open_button = QPushButton("Open match")
        open_button.setObjectName("ghost")
        open_button.clicked.connect(lambda _=None, m=match: self._emit_match_selection(m))
        meta_row.addWidget(open_button)

        layout.addLayout(header)
        layout.addLayout(teams_row)
        layout.addLayout(meta_row)
        card.setLayout(layout)
        return card

    def _emit_match_selection(self, match: dict) -> None:
        self.match_selected.emit(match)

    def _format_score(self, match: dict) -> str:
        if match.get("home_score") is None or match.get("away_score") is None:
            return "–"
        return f"{match['home_score']} - {match['away_score']}"

    def _format_kickoff_time(self, kickoff_raw: Optional[str]) -> str:
        if not kickoff_raw:
            return "TBD"
        if isinstance(kickoff_raw, str):
            candidates = [kickoff_raw]
            if kickoff_raw.endswith("Z"):
                candidates.append(kickoff_raw[:-1] + "+00:00")
            for candidate in candidates:
                try:
                    parsed = datetime.fromisoformat(candidate)
                    return parsed.strftime("%b %d, %H:%M")
                except ValueError:
                    continue
            return str(kickoff_raw)
        return str(kickoff_raw)
