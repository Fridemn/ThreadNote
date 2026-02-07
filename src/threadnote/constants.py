"""Application-wide constants."""
from typing import Tuple

APP_NAME: str = "ThreadNote"
DEFAULT_LOCALE: str = "en"
SUPPORTED_LOCALES: Tuple[str, str] = ("en", "zh_CN")
LOCALES_DIR_NAME: str = "locales"
DEFAULT_WINDOW_SIZE: Tuple[int, int] = (1200, 800)
ARCHIVE_VIEW_REFRESH_MS: int = 1000
