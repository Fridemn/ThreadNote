"""Resource path utilities for ThreadNote."""

from pathlib import Path
import sys


def get_resource_path(relative_path: str) -> Path:
    """
    Get the absolute path to a resource file.

    Works both in development and when packaged with PyInstaller.

    Args:
        relative_path: Relative path from the resources directory

    Returns:
        Absolute path to the resource file
    """
    # Check if running as PyInstaller bundle
    if getattr(sys, "frozen", False):
        # Running as compiled executable
        base_path = Path(sys._MEIPASS)  # type: ignore
    else:
        # Running in development
        base_path = Path(__file__).parent.parent

    return base_path / "resources" / relative_path


def get_locales_path() -> Path:
    """
    Get the absolute path to the locales directory.

    Works both in development and when packaged with PyInstaller.

    Returns:
        Absolute path to the locales directory
    """
    # Check if running as PyInstaller bundle
    if getattr(sys, "frozen", False):
        # Running as compiled executable - locales are in _MEIPASS/locales
        base_path = Path(sys._MEIPASS)  # type: ignore
        return base_path / "locales"
    else:
        # Running in development - locales are in project root
        # src/threadnote/utils/resources.py -> src/threadnote -> src -> root
        project_root = Path(__file__).resolve().parents[3]
        return project_root / "locales"


def get_data_dir() -> Path:
    """
    Get the absolute path to the data directory.

    Works both in development and when packaged with PyInstaller.

    Returns:
        Absolute path to the data directory
    """
    # Check if running as PyInstaller bundle
    if getattr(sys, "frozen", False):
        # Running as compiled executable - use directory where exe is located
        base_path = Path(sys.executable).parent
    else:
        # Running in development - data is in project root
        # src/threadnote/utils/resources.py -> src/threadnote -> src -> root
        project_root = Path(__file__).resolve().parents[3]
        base_path = project_root

    data_dir = base_path / "data"
    # Ensure data directory exists
    data_dir.mkdir(exist_ok=True)
    return data_dir
