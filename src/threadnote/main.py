"""ThreadNote application entry point."""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from .core.app_controller import AppController
from .utils.i18n import gettext_factory
from .config import load_config
from .utils.preferences import UserPreferences
from .utils.resources import get_resource_path


def main() -> int:
    app = QApplication([])
    # Set application icon
    icon_path = get_resource_path("logo.png")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Load user preferences
    config = load_config()
    prefs = UserPreferences(config.preferences_file)

    # Get locale (from preferences or system default)
    preferred_locale = prefs.get_locale()
    translator = gettext_factory(preferred_locale)

    controller = AppController(translator, prefs)
    controller.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
