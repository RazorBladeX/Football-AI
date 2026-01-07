from PySide6.QtWidgets import QLabel, QListWidget, QPushButton, QVBoxLayout, QWidget

from app.services.prediction_service import PredictionService


class PredictionsPage(QWidget):
    def __init__(self, prediction_service: PredictionService):
        super().__init__()
        self.prediction_service = prediction_service

        self.list_widget = QListWidget()
        self.refresh_button = QPushButton("Refresh Predictions")
        self.refresh_button.clicked.connect(self.refresh)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Saved Predictions"))
        layout.addWidget(self.list_widget)
        layout.addWidget(self.refresh_button)
        self.setLayout(layout)

        self.refresh()

    def refresh(self) -> None:
        self.list_widget.clear()
        for prediction in self.prediction_service.list_predictions():
            desc = (
                f"Match {prediction.match_id} | {prediction.final_score_home}-{prediction.final_score_away} "
                f"confidence {prediction.confidence}"
            )
            self.list_widget.addItem(desc)
