"""Allow running threadnote as a module: python -m threadnote"""

from .main import main

if __name__ == "__main__":
    raise SystemExit(main())
