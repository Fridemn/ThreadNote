"""Main window for ThreadNote."""
from typing import Callable

from PyQt6.QtWidgets import QMainWindow

from ..constants import APP_NAME, DEFAULT_WINDOW_SIZE


class MainWindow(QMainWindow):
    """Primary application window."""

    def __init__(self, translator: Callable[[str], str]) -> None:
        super().__init__()
        self._ = translator
        self._configure_window()

    def _configure_window(self) -> None:
        """Configure the window title and size."""
        self.setWindowTitle(self._(APP_NAME))
        width, height = DEFAULT_WINDOW_SIZE
        self.resize(width, height)
