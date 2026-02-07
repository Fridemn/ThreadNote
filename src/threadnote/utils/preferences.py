"""User preferences management."""

import json
from pathlib import Path
from typing import Optional


class UserPreferences:
    """Manages user preferences stored in JSON file."""

    def __init__(self, config_file: Path):
        self.config_file = config_file
        self._data = self._load()

    def _load(self) -> dict:
        """Load preferences from file."""
        if self.config_file.exists():
            try:
                return json.loads(self.config_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save(self):
        """Save preferences to file."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    def get_locale(self) -> Optional[str]:
        """Get saved locale preference."""
        return self._data.get("locale")

    def set_locale(self, locale: str):
        """Save locale preference."""
        self._data["locale"] = locale
        self._save()

    def get_theme(self) -> Optional[str]:
        """Get saved theme preference."""
        return self._data.get("theme")

    def set_theme(self, theme: str):
        """Save theme preference."""
        self._data["theme"] = theme
        self._save()
