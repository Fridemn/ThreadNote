"""Priority selection dialog with four quadrants visualization."""
from typing import Optional, Callable
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QRadioButton, QButtonGroup, QPushButton, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt


class PriorityDialog(QDialog):
    """Dialog for selecting task priority using four quadrants."""
    
    def __init__(self, current_priority: int = 4, translator: Callable[[str], str] = None, parent=None):
        super().__init__(parent)
        self._ = translator if translator else lambda x: x
        self.selected_priority = current_priority
        self.setWindowTitle(self._("Set Task Priority"))
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(self._("Eisenhower Matrix - Task Priority"))
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Four Quadrants Grid
        quadrant_group = QGroupBox(self._("Select Priority Quadrant"))
        grid_layout = QGridLayout()
        
        self.button_group = QButtonGroup(self)
        
        # Priority labels and descriptions
        priority_info = {
            1: (self._("P1: Urgent + Important"), self._("Do First - Critical tasks requiring immediate attention")),
            2: (self._("P2: Not Urgent + Important"), self._("Schedule - Important goals and planning")),
            3: (self._("P3: Urgent + Not Important"), self._("Delegate - Interruptions and distractions")),
            4: (self._("P4: Not Urgent + Not Important"), self._("Eliminate - Time wasters"))
        }
        
        # P1: Top-Left (Urgent + Important)
        p1_btn = QRadioButton(priority_info[1][0])
        p1_btn.setToolTip(priority_info[1][1])
        self.button_group.addButton(p1_btn, 1)
        grid_layout.addWidget(p1_btn, 0, 0)
        
        # P2: Top-Right (Not Urgent + Important)
        p2_btn = QRadioButton(priority_info[2][0])
        p2_btn.setToolTip(priority_info[2][1])
        self.button_group.addButton(p2_btn, 2)
        grid_layout.addWidget(p2_btn, 0, 1)
        
        # P3: Bottom-Left (Urgent + Not Important)
        p3_btn = QRadioButton(priority_info[3][0])
        p3_btn.setToolTip(priority_info[3][1])
        self.button_group.addButton(p3_btn, 3)
        grid_layout.addWidget(p3_btn, 1, 0)
        
        # P4: Bottom-Right (Not Urgent + Not Important)
        p4_btn = QRadioButton(priority_info[4][0])
        p4_btn.setToolTip(priority_info[4][1])
        self.button_group.addButton(p4_btn, 4)
        grid_layout.addWidget(p4_btn, 1, 1)
        
        # Store priority info for later use
        self._priority_info = priority_info
        
        # Set current selection
        self.button_group.button(self.selected_priority).setChecked(True)
        
        quadrant_group.setLayout(grid_layout)
        layout.addWidget(quadrant_group)
        
        # Description area
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("padding: 10px; background-color: #F0F0F0;")
        self._update_description()
        layout.addWidget(self.description_label)
        
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
        
        # Connect signal
        self.button_group.buttonClicked.connect(self._on_priority_changed)
        
        self.setMinimumWidth(400)

    def _on_priority_changed(self):
        self._update_description()

    def _update_description(self):
        priority = self.button_group.checkedId()
        if priority > 0 and priority in self._priority_info:
            label, desc = self._priority_info[priority]
            self.description_label.setText(f"<b>{label}</b><br>{desc}")

    def get_priority(self) -> Optional[int]:
        """Return selected priority if dialog was accepted."""
        if self.result() == QDialog.DialogCode.Accepted:
            return self.button_group.checkedId()
        return None
