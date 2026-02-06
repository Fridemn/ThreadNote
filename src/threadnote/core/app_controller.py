"""Controller wiring for the application."""
from typing import Callable

from ..ui.main_window import MainWindow


class AppController:
    """Coordinate the application view lifecycle."""

    def __init__(self, translator: Callable[[str], str]) -> None:
        self._window = MainWindow(translator)

    def show(self) -> None:
        """Show the main window."""
        self._window.show()
