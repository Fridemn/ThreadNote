"""ThreadNote application entry point."""
from PyQt6.QtWidgets import QApplication

from .core.app_controller import AppController
from .utils.i18n import gettext_factory
from .config import load_config
from .utils.preferences import UserPreferences


def main() -> int:
    """Start the ThreadNote application."""
    app = QApplication([])
    
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
