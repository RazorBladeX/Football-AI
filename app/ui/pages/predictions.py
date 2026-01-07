from datetime import date

from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.prediction_service import PredictionService
from app.services.match_service import MatchService


class PredictionsPage(QWidget):
    def __init__(self, prediction_service: PredictionService, match_service: MatchService):
        super().__init__()
        self.prediction_service = prediction_service
        self.match_service = match_service

        self.header = QLabel("AI Predictions")
        self.header.setStyleSheet("font-size: 20px; font-weight: 800;")
        self.description = QLabel(
            "Pick a match and spin up on-device predictions. Feels like a Discord command palette, stores locally."
        )
        self.description.setWordWrap(True)
        self.description.setObjectName("muted")

        self.match_select = QComboBox()
        self.generate_button = QPushButton("Generate with AI")
        self.generate_button.clicked.connect(self.generate_prediction)
        self.list_widget = QListWidget()
        self.status_label = QLabel("Pick a match to begin.")
        self.status_label.setObjectName("muted")

        hero_card = QFrame()
        hero_card.setObjectName("card")
        hero_layout = QVBoxLayout()
        hero_layout.setSpacing(8)
        hero_layout.addWidget(self.header)
        hero_layout.addWidget(self.description)
        hero_card.setLayout(hero_layout)

        form_card = QFrame()
        form_card.setObjectName("panel")
        form_layout = QVBoxLayout()
        form_layout.setSpacing(12)
        form_layout.addWidget(QLabel("Match"))
        form_layout.addWidget(self.match_select)
        form_layout.addWidget(self.generate_button)
        form_layout.addWidget(self.status_label)
        form_card.setLayout(form_layout)

        list_card = QFrame()
        list_card.setObjectName("panel")
        list_layout = QVBoxLayout()
        list_layout.addWidget(QLabel("Saved Predictions"))
        list_layout.addWidget(self.list_widget)
        list_card.setLayout(list_layout)

        row = QHBoxLayout()
        row.setSpacing(14)
        row.addWidget(form_card, 1)
        row.addWidget(list_card, 1)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.addWidget(hero_card)
        layout.addLayout(row)
        self.setLayout(layout)

        self.reload_matches(date.today())
        self.refresh_predictions()

    def reload_matches(self, target_date: date) -> None:
        matches = self.match_service.list_matches_for_date(target_date)
        self.match_select.clear()
        for match in matches:
            label = f"{match.home_team.name} vs {match.away_team.name}"
            self.match_select.addItem(label, match.id)
        if not matches:
            self.match_select.addItem("No matches loaded yet", None)
            self.generate_button.setEnabled(False)
            self.status_label.setText("Use the Home tab to refresh fixtures, then return here.")
        else:
            self.generate_button.setEnabled(True)
            self.status_label.setText(f"{len(matches)} matches available for predictions.")

    def refresh_predictions(self) -> None:
        self.list_widget.clear()
        for prediction in self.prediction_service.list_predictions():
            desc = (
                f"Match {prediction.match_id} | "
                f"{prediction.final_score_home}-{prediction.final_score_away} "
                f"confidence {prediction.confidence or 'N/A'}"
            )
            self.list_widget.addItem(desc)

    def generate_prediction(self) -> None:
        match_id = self.match_select.currentData()
        if not match_id:
            self.status_label.setText("No match selected yet.")
            return
        match = self.match_service.get_match(match_id)
        if not match:
            self.status_label.setText("Selected match is unavailable.")
            return
        prediction = self.prediction_service.generate_prediction(match)
        self.status_label.setText(
            f"Prediction saved: {prediction.final_score_home}-{prediction.final_score_away} "
            f"(confidence {prediction.confidence})"
        )
        self.refresh_predictions()
