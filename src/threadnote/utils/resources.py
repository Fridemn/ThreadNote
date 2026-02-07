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
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = Path(sys._MEIPASS)  # type: ignore
    else:
        # Running in development
        base_path = Path(__file__).parent.parent
    
    return base_path / 'resources' / relative_path
