"""Markdown editor widget."""

from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import pyqtSignal


class EditorWidget(QTextEdit):
    """Markdown editor with auto-save triggers."""

    content_changed = pyqtSignal(str)

    def __init__(self, translator=None, parent=None):
        super().__init__(parent)
        self._ = translator if translator else lambda x: x
        self.setPlaceholderText(f"{self._('# New Task')}\n{self._('Details...')}")
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self):
        self.content_changed.emit(self.toPlainText())

    def set_content(self, content: str):
        """Update content without triggering signal loop if possible."""
        self.blockSignals(True)
        self.setPlainText(content)
        self.blockSignals(False)
