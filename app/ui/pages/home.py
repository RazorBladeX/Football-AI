from typing import List

import matplotlib

matplotlib.use("Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import QLabel, QFrame, QHeaderView, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from app.services.match_service import MatchService
from app.services.prediction_service import PredictionService


class HomePage(QWidget):
    def __init__(self, match_service: MatchService, prediction_service: PredictionService):
        super().__init__()
        self.match_service = match_service
        self.prediction_service = prediction_service

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["League", "Home", "Away", "Status", "Score"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)

        self.status_label = QLabel("Today's fixtures")
        self.status_label.setStyleSheet("font-size: 18px; font-weight: 600;")

        self.figure = Figure(figsize=(4, 2), facecolor="#111827")
        self.canvas = FigureCanvasQTAgg(self.figure)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout()
        card_layout.addWidget(self.status_label)
        card_layout.addWidget(self.table)
        card_layout.addWidget(self.canvas)
        card.setLayout(card_layout)

        layout = QVBoxLayout()
        layout.addWidget(card)
        self.setLayout(layout)

    def load_matches(self, rows: List[dict]) -> None:
        self.table.setRowCount(len(rows))
        for i, match in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(match.get("league", "")))
            self.table.setItem(i, 1, QTableWidgetItem(match.get("home", "")))
            self.table.setItem(i, 2, QTableWidgetItem(match.get("away", "")))
            self.table.setItem(i, 3, QTableWidgetItem(match.get("status", "")))
            score = "-"
            if match.get("home_score") is not None and match.get("away_score") is not None:
                score = f"{match['home_score']} - {match['away_score']}"
            self.table.setItem(i, 4, QTableWidgetItem(score))
        self.status_label.setText(f"Loaded {len(rows)} fixtures")
        self._render_chart(rows)

    def _render_chart(self, rows: List[dict]) -> None:
        status_counts = {"live": 0, "finished": 0, "upcoming": 0}
        for m in rows:
            status = m.get("status", "upcoming").lower()
            if status not in status_counts:
                status_counts["upcoming"] += 1
                continue
            status_counts[status] += 1
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        bars = list(status_counts.keys())
        values = list(status_counts.values())
        ax.bar(bars, values, color=["#10b981", "#3b82f6", "#6b7280"])
        ax.set_facecolor("#111827")
        self.figure.patch.set_facecolor("#111827")
        ax.tick_params(colors="#e5e7eb")
        for spine in ax.spines.values():
            spine.set_color("#374151")
        ax.set_title("Match status mix", color="#e5e7eb")
        self.canvas.draw_idle()
