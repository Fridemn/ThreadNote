"""Due date selection dialog."""

from typing import Optional, Callable
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QDateTimeEdit,
    QCheckBox,
)
from PyQt6.QtCore import Qt, QDateTime


class DueDateDialog(QDialog):
    """Dialog for setting task due date."""

    def __init__(
        self,
        current_due_date: Optional[datetime] = None,
        translator: Callable[[str], str] = None,
        parent=None,
    ):
        super().__init__(parent)
        self._ = translator if translator else lambda x: x
        self.current_due_date = current_due_date
        self.setWindowTitle(self._("Set Due Date"))
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel(self._("Set Due Date"))
        title.setStyleSheet("font-size: 12pt; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # No due date checkbox
        self.no_due_date_cb = QCheckBox(self._("No Due Date"))
        layout.addWidget(self.no_due_date_cb)

        # Date time picker
        self.date_time_edit = QDateTimeEdit()
        self.date_time_edit.setCalendarPopup(True)
        self.date_time_edit.setDisplayFormat("yyyy-MM-dd HH:mm")

        if self.current_due_date:
            qt_datetime = QDateTime.fromSecsSinceEpoch(
                int(self.current_due_date.timestamp())
            )
            self.date_time_edit.setDateTime(qt_datetime)
            self.no_due_date_cb.setChecked(False)
        else:
            # Default: tomorrow at current time
            tomorrow = datetime.now() + timedelta(days=1)
            qt_datetime = QDateTime.fromSecsSinceEpoch(int(tomorrow.timestamp()))
            self.date_time_edit.setDateTime(qt_datetime)
            self.no_due_date_cb.setChecked(True)
            self.date_time_edit.setEnabled(False)

        layout.addWidget(self.date_time_edit)

        # Connect checkbox
        self.no_due_date_cb.stateChanged.connect(self._on_no_due_date_changed)

        # Quick buttons
        quick_layout = QHBoxLayout()

        today_btn = QPushButton(self._("Today"))
        today_btn.clicked.connect(lambda: self._set_quick_date(0))
        quick_layout.addWidget(today_btn)

        tomorrow_btn = QPushButton(self._("Tomorrow"))
        tomorrow_btn.clicked.connect(lambda: self._set_quick_date(1))
        quick_layout.addWidget(tomorrow_btn)

        week_btn = QPushButton(self._("Next Week"))
        week_btn.clicked.connect(lambda: self._set_quick_date(7))
        quick_layout.addWidget(week_btn)

        layout.addLayout(quick_layout)

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

    def _on_no_due_date_changed(self, state):
        self.date_time_edit.setEnabled(state == 0)

    def _set_quick_date(self, days_offset: int):
        self.no_due_date_cb.setChecked(False)
        self.date_time_edit.setEnabled(True)
        target = datetime.now() + timedelta(days=days_offset)
        qt_datetime = QDateTime.fromSecsSinceEpoch(int(target.timestamp()))
        self.date_time_edit.setDateTime(qt_datetime)

    def get_due_date(self) -> Optional[datetime]:
        """Return selected due date if dialog was accepted."""
        if self.result() == QDialog.DialogCode.Accepted:
            if self.no_due_date_cb.isChecked():
                return None
            qt_datetime = self.date_time_edit.dateTime()
            return datetime.fromtimestamp(qt_datetime.toSecsSinceEpoch())
        return self.current_due_date
