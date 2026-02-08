"""Configuration loading for ThreadNote."""

from dataclasses import dataclass
from pathlib import Path
import sys

from .constants import DEFAULT_LOCALE
from .utils.resources import get_locales_path, get_data_dir


def get_project_root() -> Path:
    """Return the project root directory."""
    # Check if running as PyInstaller bundle
    if getattr(sys, "frozen", False):
        # Running as compiled executable - use exe directory
        return Path(sys.executable).parent
    else:
        # Running in development
        # src/threadnote/config.py -> src/threadnote -> src -> root
        return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class AppConfig:
    """Application configuration values."""

    project_root: Path
    locales_path: Path
    default_locale: str
    preferences_file: Path


def load_config() -> AppConfig:
    """Build the runtime configuration."""
    project_root = get_project_root()
    locales_path = get_locales_path()
    data_dir = get_data_dir()
    preferences_file = data_dir / "preferences.json"
    return AppConfig(
        project_root=project_root,
        locales_path=locales_path,
        default_locale=DEFAULT_LOCALE,
        preferences_file=preferences_file,
    )
