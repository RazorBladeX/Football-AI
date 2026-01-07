from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.models.team import Team


class TeamDetailPage(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel("Select a team to view details")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def set_team(self, team: Team) -> None:
        self.label.setText(f"{team.name}\nLeague ID: {team.league_id}\nVenue: {team.venue or 'Unknown'}")
