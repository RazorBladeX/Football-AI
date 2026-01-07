from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

PRIMARY = "#0b1220"
SURFACE = "#0f172a"
PANEL = "#111c35"
ACCENT = "#3b82f6"
ACCENT_GRADIENT = "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #2563eb, stop:1 #9333ea)"
TEXT = "#e5e7eb"
SUBTEXT = "#9ca3af"
CARD = "#0b162c"
BORDER = "#1f2937"
SOFT_HIGHLIGHT = "#1b2942"
SECONDARY_SURFACE = "#0f1b31"


def apply_dark_palette(app: QApplication) -> None:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(SURFACE))
    palette.setColor(QPalette.WindowText, QColor(TEXT))
    palette.setColor(QPalette.Base, QColor(PRIMARY))
    palette.setColor(QPalette.AlternateBase, QColor(SURFACE))
    palette.setColor(QPalette.ToolTipBase, QColor(TEXT))
    palette.setColor(QPalette.ToolTipText, QColor(TEXT))
    palette.setColor(QPalette.Text, QColor(TEXT))
    palette.setColor(QPalette.Button, QColor(CARD))
    palette.setColor(QPalette.ButtonText, QColor(TEXT))
    palette.setColor(QPalette.Highlight, QColor(ACCENT))
    palette.setColor(QPalette.HighlightedText, QColor(PRIMARY))
    app.setPalette(palette)
    app.setStyleSheet(
        """
        QWidget { background-color: %s; color: %s; font-family: 'Inter', 'Segoe UI', sans-serif; }
        QFrame#sidebar { background-color: %s; border: 1px solid %s; border-radius: 18px; padding: 16px; }
        QFrame#hero { background: %s; border: 1px solid %s; border-radius: 18px; padding: 20px; }
        QFrame#card { background-color: %s; border: 1px solid %s; border-radius: 16px; padding: 16px; }
        QFrame#panel { background-color: %s; border: 1px solid %s; border-radius: 16px; padding: 16px; }
        QFrame#pill, QFrame#chip { background-color: %s; border: 1px solid %s; border-radius: 12px; padding: 8px 12px; }
        QListWidget { background: transparent; border: none; }
        QListWidget::item { padding: 12px 14px; border-radius: 12px; color: %s; }
        QListWidget::item:selected { background-color: %s; color: #f8fafc; }
        QPushButton { background-color: %s; color: %s; border: 1px solid %s; border-radius: 12px; padding: 12px 16px; font-weight: 700; }
        QPushButton:hover { background-color: #2563eb; }
        QPushButton#ghost { background-color: transparent; border: 1px solid %s; color: %s; }
        QComboBox, QDateEdit, QLineEdit { background-color: %s; color: %s; border: 1px solid %s; border-radius: 10px; padding: 10px 12px; }
        QTableWidget { background-color: %s; gridline-color: %s; alternate-background-color: %s; border: 1px solid %s; border-radius: 14px; }
        QTableWidget::item { padding: 10px; }
        QHeaderView::section { background-color: %s; color: %s; padding: 10px; border: none; font-weight: 800; }
        QScrollArea { background-color: %s; border: 1px solid %s; border-radius: 14px; }
        QScrollArea#plain-scroll { background-color: transparent; border: none; }
        QLabel#muted { color: %s; }
        """
        % (
            SURFACE,
            TEXT,
            SECONDARY_SURFACE,
            BORDER,
            ACCENT_GRADIENT,
            BORDER,
            CARD,
            BORDER,
            PANEL,
            BORDER,
            SOFT_HIGHLIGHT,
            BORDER,
            TEXT,
            ACCENT,
            ACCENT,
            BORDER,
            BORDER,
            TEXT,
            PANEL,
            TEXT,
            BORDER,
            CARD,
            BORDER,
            SURFACE,
            BORDER,
            CARD,
            BORDER,
            TEXT,
            SURFACE,
            BORDER,
            SUBTEXT,
        )
    )
