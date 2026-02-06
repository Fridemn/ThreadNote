"""Markdown editor widget."""
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import pyqtSignal

class EditorWidget(QTextEdit):
    """Markdown editor with auto-save triggers."""
    
    content_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("# New Task\nDetails...")
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self):
        self.content_changed.emit(self.toPlainText())
        
    def set_content(self, content: str):
        """Update content without triggering signal loop if possible."""
        self.blockSignals(True)
        self.setPlainText(content)
        self.blockSignals(False)
