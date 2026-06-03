"""ThreadNote application entry point."""

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from .config import load_config
from .core.app_controller import AppController
from .utils.i18n import gettext_factory
from .utils.preferences import UserPreferences
from .utils.resources import get_resource_path
from .utils.single_process import ActivationServer, SingleProcessLock


def main() -> int:
    config = load_config()
    process_lock = SingleProcessLock.for_data_dir(config.preferences_file.parent)
    if not process_lock.acquire():
        process_lock.request_activation()
        return 0

    app = QApplication([])
    activation_server = ActivationServer(process_lock.activation_path)

    # Set application icon
    icon_path = get_resource_path("logo.png")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Load user preferences
    prefs = UserPreferences(config.preferences_file)

    # Get locale (from preferences or system default)
    preferred_locale = prefs.get_locale()
    translator = gettext_factory(preferred_locale)

    controller = AppController(translator, prefs)
    activation_server.activation_requested.connect(controller.activate)
    activation_server.listen()
    controller.show()
    try:
        return app.exec()
    finally:
        activation_server.close()
        process_lock.release()


if __name__ == "__main__":
    raise SystemExit(main())
