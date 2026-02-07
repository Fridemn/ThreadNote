"""Dialog for viewing archived tasks."""
from pathlib import Path
from typing import Callable, Optional

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer

from ..constants import ARCHIVE_VIEW_REFRESH_MS


class ArchiveViewDialog(QDialog):
    """Read-only dialog showing archived tasks content."""

    def __init__(self, archive_file: Path, translator: Callable[[str], str] = None, parent=None) -> None:
        super().__init__(parent)
        self._ = translator if translator else lambda x: x
        self._archive_file = archive_file
        self._last_mtime: Optional[float] = None
        self._timer = QTimer(self)
        self.setWindowTitle(self._("Archived Tasks"))
        self._init_ui()
        self._setup_refresh()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        self._text = QTextEdit()
        self._text.setReadOnly(True)
        layout.addWidget(self._text)

        button_layout = QHBoxLayout()
        close_btn = QPushButton(self._("Close"))
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

    def _setup_refresh(self) -> None:
        self._timer.setInterval(ARCHIVE_VIEW_REFRESH_MS)
        self._timer.timeout.connect(self._refresh_if_changed)
        self._refresh_if_changed(force=True)
        self._timer.start()

    def _refresh_if_changed(self, force: bool = False) -> None:
        current_mtime = self._get_archive_mtime()
        if force or current_mtime != self._last_mtime:
            self._last_mtime = current_mtime
            content = self._read_archive_content()
            if not content.strip():
                content = self._("Archive is empty.")
            self._render_markdown(content)

    def _get_archive_mtime(self) -> Optional[float]:
        try:
            return self._archive_file.stat().st_mtime
        except FileNotFoundError:
            return None

    def _read_archive_content(self) -> str:
        if self._archive_file.exists():
            return self._archive_file.read_text(encoding="utf-8")
        return ""

    def _render_markdown(self, content: str) -> None:
        if hasattr(self._text, "setMarkdown"):
            self._text.setMarkdown(content)
        else:
            self._text.setPlainText(content)

    def closeEvent(self, event) -> None:
        self._timer.stop()
        super().closeEvent(event)
