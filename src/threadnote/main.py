"""ThreadNote application entry point."""
from PyQt6.QtWidgets import QApplication

from .core.app_controller import AppController
from .utils.i18n import gettext_factory


def main() -> int:
    """Start the ThreadNote application."""
    app = QApplication([])
    translator = gettext_factory()
    controller = AppController(translator)
    controller.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
