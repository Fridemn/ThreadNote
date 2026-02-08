"""Launcher script for PyInstaller packaging."""

import sys
from pathlib import Path
from threadnote.main import main

# Ensure src is in the path
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

# Import and run the main function

if __name__ == "__main__":
    raise SystemExit(main())
