from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

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

        self.status_label = QLabel("Today's fixtures")

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.table)
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
