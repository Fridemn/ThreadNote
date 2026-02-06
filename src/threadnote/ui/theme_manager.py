"""Theme management for Light/Dark modes."""
from enum import Enum
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor

class Theme(str, Enum):
    LIGHT = "light"
    DARK = "dark"

class ThemeManager:
    """Manages application-wide theme styles."""

    @staticmethod
    def apply_theme(app: QApplication, theme: Theme):
        """Apply the specified theme to the application."""
        if theme == Theme.DARK:
            ThemeManager._apply_dark_theme(app)
        else:
            ThemeManager._apply_light_theme(app)

    @staticmethod
    def _apply_dark_theme(app: QApplication):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(50, 50, 50))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        app.setPalette(palette)
        # Minimalist Black & White overrides for Widgets if needed (CSS)
        app.setStyleSheet("""
            QTreeWidget {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: none;
            }
            QTextEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #333333;
            }
            QSplitter::handle {
                background-color: #444444;
            }
        """)

    @staticmethod
    def _apply_light_theme(app: QApplication):
        palette = QPalette() # Default is usually light
        palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
        app.setPalette(palette)
        
        app.setStyleSheet("""
            QTreeWidget {
                background-color: #FFFFFF;
                color: #000000;
                border: none;
            }
            QTextEdit {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #E0E0E0;
            }
            QSplitter::handle {
                background-color: #E0E0E0;
            }
        """)
