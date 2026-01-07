from typing import List
from datetime import datetime

import matplotlib

matplotlib.use("Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QHeaderView,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.match_service import MatchService
from app.services.prediction_service import PredictionService


class HomePage(QWidget):
    def __init__(self, match_service: MatchService, prediction_service: PredictionService):
        super().__init__()
        self.match_service = match_service
        self.prediction_service = prediction_service
        self.rows: List[dict] = []

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["League", "Home", "Away", "Kickoff", "Status", "Score"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self._on_row_selected)

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

        table_card = QFrame()
        table_card.setObjectName("panel")
        table_layout = QVBoxLayout()
        table_title = QLabel("Fixture grid")
        table_title.setStyleSheet("font-size: 16px; font-weight: 700;")
        table_subtitle = QLabel("Sortable, modern list of the matches we hydrated from ESPN/BBC.")
        table_subtitle.setObjectName("muted")
        table_layout.addWidget(table_title)
        table_layout.addWidget(table_subtitle)
        table_layout.addWidget(self.table)
        table_card.setLayout(table_layout)

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

        self.detail_card = QFrame()
        self.detail_card.setObjectName("panel")
        detail_layout = QVBoxLayout()
        self.detail_heading = QLabel("Match details")
        self.detail_heading.setStyleSheet("font-size: 16px; font-weight: 700;")
        self.detail_sub = QLabel("Click a game to view the live card, similar to FotMob.")
        self.detail_sub.setObjectName("muted")

        self.teams_label = QLabel("No match selected")
        self.teams_label.setStyleSheet("font-size: 18px; font-weight: 800;")
        self.league_label = QLabel("")
        self.league_label.setObjectName("muted")

        self.status_chip = QFrame()
        self.status_chip.setObjectName("pill")
        chip_layout = QHBoxLayout()
        chip_layout.setContentsMargins(10, 6, 10, 6)
        chip_layout.addWidget(QLabel("Status"))
        self.status_value = QLabel("-")
        chip_layout.addWidget(self.status_value)
        chip_layout.addStretch()
        self.status_chip.setLayout(chip_layout)

        self.score_label = QLabel("")
        self.score_label.setStyleSheet("font-size: 28px; font-weight: 800;")
        self.kickoff_label = QLabel("")
        self.kickoff_label.setObjectName("muted")

        quick_row = QHBoxLayout()
        quick_row.setSpacing(10)
        quick_row.addWidget(self.status_chip)
        quick_row.addStretch()

        detail_layout.addWidget(self.detail_heading)
        detail_layout.addWidget(self.detail_sub)
        detail_layout.addLayout(quick_row)
        detail_layout.addWidget(self.teams_label)
        detail_layout.addWidget(self.score_label)
        detail_layout.addWidget(self.league_label)
        detail_layout.addWidget(self.kickoff_label)
        detail_layout.addStretch()

        self.detail_card.setLayout(detail_layout)

        grid = QGridLayout()
        grid.setSpacing(14)
        grid.addWidget(table_card, 0, 0, 1, 2)
        grid.addWidget(self.detail_card, 0, 2, 1, 1)
        grid.addWidget(chart_card, 1, 0, 1, 3)
        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 0)
        grid.setColumnStretch(2, 2)

        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.addWidget(hero_card)
        layout.addLayout(grid)
        self.setLayout(layout)

    def load_matches(self, rows: List[dict], target_date) -> None:
        self.rows = rows
        self.table.setRowCount(len(rows))
        for i, match in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(match.get("league", "")))
            self.table.setItem(i, 1, QTableWidgetItem(match.get("home", "")))
            self.table.setItem(i, 2, QTableWidgetItem(match.get("away", "")))
            kickoff_raw = match.get("kickoff")
            kickoff_display = kickoff_raw or "-"
            if isinstance(kickoff_raw, str):
                kickoff_display = kickoff_raw.replace("T", " ").replace("Z", "")
            self.table.setItem(i, 3, QTableWidgetItem(kickoff_display))
            self.table.setItem(i, 4, QTableWidgetItem(match.get("status", "").title()))
            score = "-"
            if match.get("home_score") is not None and match.get("away_score") is not None:
                score = f"{match['home_score']} - {match['away_score']}"
            self.table.setItem(i, 5, QTableWidgetItem(score))
        self.status_label.setText(f"Loaded {len(rows)} fixtures")
        self.sub_status.setText(f"Viewing fixtures for {target_date.strftime('%b %d, %Y')}")
        status_counts = self._count_statuses(rows)
        self._render_chart(status_counts)
        self._update_metrics(status_counts)
        if rows:
            self._set_detail(rows[0])

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

    def _on_row_selected(self, row: int, _col: int) -> None:
        if 0 <= row < len(self.rows):
            self._set_detail(self.rows[row])

    def _set_detail(self, match: dict) -> None:
        home = match.get("home", "")
        away = match.get("away", "")
        self.teams_label.setText(f"{home} vs {away}")
        status = match.get("status", "upcoming").title()
        self.status_value.setText(status)
        score = "-"
        if match.get("home_score") is not None and match.get("away_score") is not None:
            score = f"{match['home_score']} - {match['away_score']}"
        self.score_label.setText(score if score != "-" else "Awaiting kickoff")
        league = match.get("league", "")
        self.league_label.setText(f"Competition · {league}")
        kickoff_display = self._format_kickoff_time(match.get("kickoff"))
        self.kickoff_label.setText(f"Kickoff · {kickoff_display}")

    def _format_kickoff_time(self, kickoff_raw) -> str:
        if not kickoff_raw:
            return "TBD"
        if isinstance(kickoff_raw, str):
            try:
                parsed = datetime.fromisoformat(kickoff_raw.replace("Z", "+00:00"))
                return parsed.strftime("%b %d, %H:%M")
            except ValueError:
                return kickoff_raw.replace("T", " ").replace("Z", "")
        return str(kickoff_raw)
