from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

PRIMARY = "#0d1117"
SURFACE = "#111827"
ACCENT = "#10b981"
TEXT = "#e5e7eb"
SUBTEXT = "#9ca3af"
CARD = "#1f2937"
BORDER = "#2d3748"


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
        QFrame#card { background-color: %s; border: 1px solid %s; border-radius: 10px; padding: 12px; }
        QListWidget { background-color: %s; border: none; }
        QListWidget::item { padding: 10px 12px; }
        QListWidget::item:selected { background-color: %s; border-radius: 6px; }
        QPushButton { background-color: %s; color: %s; border: none; border-radius: 8px; padding: 10px 14px; font-weight: 600; }
        QPushButton:hover { background-color: #0ea371; }
        QTableWidget { background-color: %s; gridline-color: %s; }
        QHeaderView::section { background-color: %s; color: %s; padding: 8px; border: none; }
        """
        % (SURFACE, TEXT, CARD, BORDER, CARD, ACCENT, ACCENT, PRIMARY, CARD, BORDER, CARD, TEXT)
    )
