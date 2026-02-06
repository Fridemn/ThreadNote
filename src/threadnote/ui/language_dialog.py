"""Language selection dialog."""
from typing import Optional, Callable
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QRadioButton, 
    QButtonGroup, QPushButton, QHBoxLayout, QLabel
)
from PyQt6.QtCore import Qt


class LanguageDialog(QDialog):
    """Dialog for selecting application language."""
    
    LANGUAGES = {
        "en": "English",
        "zh_CN": "简体中文 (Chinese Simplified)"
    }
    
    def __init__(self, current_locale: str = "en", translator: Callable[[str], str] = None, parent=None):
        super().__init__(parent)
        self._ = translator if translator else lambda x: x
        self.selected_locale = current_locale
        self.setWindowTitle(self._("Switch Language"))
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(self._("Switch Language"))
        title.setStyleSheet("font-size: 12pt; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Language selection
        self.button_group = QButtonGroup(self)
        self.locale_buttons = {}  # Map radio buttons to locale codes
        
        for locale_code, locale_name in self.LANGUAGES.items():
            radio = QRadioButton(locale_name)
            self.button_group.addButton(radio)
            self.locale_buttons[radio] = locale_code
            radio.toggled.connect(lambda checked, loc=locale_code: self._on_locale_selected(loc, checked))
            layout.addWidget(radio)
            
            if locale_code == self.selected_locale:
                radio.setChecked(True)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton(self._("OK"))
        cancel_btn = QPushButton(self._("Cancel"))
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setMinimumWidth(300)
    
    def _on_locale_selected(self, locale_code: str, checked: bool):
        """Update selected locale when radio button is toggled."""
        if checked:
            self.selected_locale = locale_code
    
    def get_selected_locale(self) -> Optional[str]:
        """Return selected locale if dialog was accepted."""
        if self.result() == QDialog.DialogCode.Accepted:
            return self.selected_locale
        return None
