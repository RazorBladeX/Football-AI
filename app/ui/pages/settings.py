from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.utils.settings_store import DEFAULT_SETTINGS, load_settings, save_settings

FALLBACK_REFRESH_MINUTES = 15


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()

        header = QLabel("System & AI Settings")
        header.setStyleSheet("font-size: 20px; font-weight: 800;")
        sub = QLabel("Configure Ollama Cloud or local/remote nodes, plus refresh cadence.")
        sub.setObjectName("muted")
        sub.setWordWrap(True)

        hero = QFrame()
        hero.setObjectName("card")
        hero_layout = QVBoxLayout()
        hero_layout.setSpacing(6)
        hero_layout.addWidget(header)
        hero_layout.addWidget(sub)
        hero.setLayout(hero_layout)

        self.mode_select = QComboBox()
        self.mode_select.addItems(["cloud", "local", "remote"])
        self.mode_select.setCurrentText(self.settings.get("ollama_mode", "cloud"))
        self.mode_select.currentTextChanged.connect(self._on_mode_change)

        self.api_key = QLineEdit(self.settings.get("ollama_api_key", ""))
        self.api_key.setEchoMode(QLineEdit.Password)
        self.api_key.setPlaceholderText("sk-...")

        self.host = QLineEdit(self.settings.get("ollama_host", "http://localhost"))
        self.port = QLineEdit(self.settings.get("ollama_port", "11434"))
        self.model = QLineEdit(self.settings.get("ollama_model", "llama3"))

        self.refresh = QSpinBox()
        self.refresh.setRange(1, 120)
        try:
            default_refresh_str = DEFAULT_SETTINGS["refresh_interval_minutes"]
            raw_refresh = self.settings.get("refresh_interval_minutes", default_refresh_str)
            self.refresh.setValue(int(raw_refresh))
        except (TypeError, ValueError):
            self.refresh.setValue(FALLBACK_REFRESH_MINUTES)

        form = QFrame()
        form.setObjectName("panel")
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(12)
        form_layout.setHorizontalSpacing(10)
        form_layout.addWidget(QLabel("Mode"), 0, 0)
        form_layout.addWidget(self.mode_select, 0, 1)
        form_layout.addWidget(QLabel("API key (cloud)"), 1, 0)
        form_layout.addWidget(self.api_key, 1, 1)
        form_layout.addWidget(QLabel("Host"), 2, 0)
        form_layout.addWidget(self.host, 2, 1)
        form_layout.addWidget(QLabel("Port"), 3, 0)
        form_layout.addWidget(self.port, 3, 1)
        form_layout.addWidget(QLabel("Model"), 4, 0)
        form_layout.addWidget(self.model, 4, 1)
        form_layout.addWidget(QLabel("Refresh (min)"), 5, 0)
        form_layout.addWidget(self.refresh, 5, 1)
        form.setLayout(form_layout)

        self.status = QLabel("")
        self.status.setObjectName("muted")

        save_button = QPushButton("Save settings")
        save_button.clicked.connect(self._save_settings)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.addWidget(hero)
        layout.addWidget(form)
        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(save_button)
        layout.addLayout(button_row)
        layout.addWidget(self.status)
        layout.addStretch()
        self.setLayout(layout)

        self._on_mode_change(self.mode_select.currentText())

    def _on_mode_change(self, mode: str) -> None:
        cloud = mode == "cloud"
        self.api_key.setEnabled(cloud)
        self.host.setEnabled(not cloud)
        self.port.setEnabled(not cloud)

    def _save_settings(self) -> None:
        self.settings.update(
            {
                "ollama_mode": self.mode_select.currentText(),
                "ollama_api_key": self.api_key.text(),
                "ollama_host": self.host.text(),
                "ollama_port": self.port.text(),
                "ollama_model": self.model.text(),
                "refresh_interval_minutes": str(self.refresh.value()),
            }
        )
        save_settings(self.settings)
        self.status.setText("Settings saved.")
        self.status.setAlignment(Qt.AlignRight)
