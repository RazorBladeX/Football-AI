from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.models.match import Match
from app.utils.datetime_utils import format_match_time


class MatchDetailPage(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel("Select a match to see details")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def set_match(self, match: Match) -> None:
        text = f"{match.home_team.name} vs {match.away_team.name}\n"
        text += f"Kickoff: {format_match_time(match.kickoff_utc)}\n"
        text += f"Status: {match.status}\n"
        if match.home_score is not None and match.away_score is not None:
            text += f"Score: {match.home_score}-{match.away_score}\n"
        self.label.setText(text)
