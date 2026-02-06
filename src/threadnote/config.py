"""Configuration loading for ThreadNote."""
from dataclasses import dataclass
from pathlib import Path

from .constants import DEFAULT_LOCALE, LOCALES_DIR_NAME


def get_project_root() -> Path:
    """Return the project root directory."""
    # src/threadnote/config.py -> src/threadnote -> src -> root
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class AppConfig:
    """Application configuration values."""

    project_root: Path
    locales_path: Path
    default_locale: str


def load_config() -> AppConfig:
    """Build the runtime configuration."""
    project_root = get_project_root()
    locales_path = project_root / LOCALES_DIR_NAME
    return AppConfig(
        project_root=project_root,
        locales_path=locales_path,
        default_locale=DEFAULT_LOCALE,
    )
