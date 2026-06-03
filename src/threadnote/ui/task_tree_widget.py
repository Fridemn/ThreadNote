"""Task tree view widget."""

from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..core.task import Task


class TaskTreeWidget(QWidget):
    """
    Displays tasks in a hierarchical tree.
    Sorted by Priority -> Created Date.
    """

    MINIMUM_WIDTH = 320
    PREFERRED_WIDTH = 340
    PRIORITY_COLUMN_WIDTH = 58
    STATUS_COLUMN_WIDTH = 74

    priority_change_requested = pyqtSignal(str)  # Emits task ID for priority change
    status_change_requested = pyqtSignal(str, str)  # Emits (task_id, new_status)
    delete_requested = pyqtSignal(str)  # Emits task ID for deletion

    def __init__(self, translator=None, parent=None):
        super().__init__(parent)
        self._ = translator if translator else lambda x: x
        self.setMinimumWidth(self.MINIMUM_WIDTH)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._tree = QTreeWidget()
        self._tree.setHeaderLabels([self._("Task"), self._("Prio"), self._("Status")])
        self._tree.setMinimumWidth(self.MINIMUM_WIDTH)
        self._configure_header()
        self._tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._show_context_menu)

        self._layout.addWidget(self._tree)

    def _configure_header(self) -> None:
        """Keep all metadata columns visible while giving titles the spare width."""
        header = self._tree.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self._tree.setColumnWidth(1, self.PRIORITY_COLUMN_WIDTH)
        self._tree.setColumnWidth(2, self.STATUS_COLUMN_WIDTH)

    def refresh(self, tasks: List[Task]):
        """Rebuild the tree from list of tasks."""
        # Save current expanded state before clearing
        expanded_state = self._save_expanded_state()

        self._tree.clear()

        # Build map for hierarchy
        task_map = {t.id: t for t in tasks}
        children_map = {t.id: [] for t in tasks}
        roots = []

        for t in tasks:
            if t.parent_id and t.parent_id in task_map:
                children_map[t.parent_id].append(t)
            else:
                roots.append(t)

        # Sort helper
        def sort_key(t: Task):
            # Same sort as PriorityQueue: Prio (asc), Created (asc)
            return (t.priority, t.created_at.timestamp())

        # Render function
        def add_items(parent_widget, task_list):
            sorted_tasks = sorted(task_list, key=sort_key)
            for t in sorted_tasks:
                item = QTreeWidgetItem(parent_widget)
                item.setText(0, t.title)
                item.setText(1, f"P{t.priority}")
                item.setText(2, t.status.value.capitalize())
                item.setData(0, Qt.ItemDataRole.UserRole, t.id)

                # Style by status
                if t.status.value == "done":
                    # Gray out and strikethrough
                    font = item.font(0)
                    font.setStrikeOut(True)
                    for col in range(3):
                        item.setFont(col, font)
                        item.setForeground(col, QColor(128, 128, 128))
                elif t.status.value == "doing":
                    # Bold for active tasks

                    font = item.font(0)
                    font.setBold(True)
                    item.setFont(0, font)
                elif t.status.value == "timeout":
                    # Red text for timeout
                    item.setForeground(0, QColor(200, 0, 0))

                # Recursion
                if t.id in children_map:
                    add_items(item, children_map[t.id])

                # Determine if should be expanded
                should_expand = False
                if expanded_state is not None and t.id in expanded_state:
                    # Restore previous expanded state
                    should_expand = expanded_state[t.id]
                elif t.priority <= 2:
                    # Expand by default if high priority (only for initial load)
                    should_expand = True

                if should_expand:
                    item.setExpanded(True)

        add_items(self._tree, roots)

    def _save_expanded_state(self) -> Optional[dict]:
        """Save the current expanded state of all items by task ID."""
        expanded_state = {}

        def traverse_item(item: QTreeWidgetItem):
            task_id = item.data(0, Qt.ItemDataRole.UserRole)
            if task_id:
                expanded_state[task_id] = item.isExpanded()

            # Traverse children
            for i in range(item.childCount()):
                traverse_item(item.child(i))

        # Traverse all root items
        root = self._tree.invisibleRootItem()
        for i in range(root.childCount()):
            traverse_item(root.child(i))

        return expanded_state if expanded_state else None

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double click on task items."""
        task_id = item.data(0, Qt.ItemDataRole.UserRole)
        if not task_id:
            return

        # Column 1: Priority
        if column == 1:
            self.priority_change_requested.emit(task_id)

        # Column 2: Status
        elif column == 2:
            self._show_status_dialog(task_id)

    def _show_context_menu(self, position):
        """Show actions for the task name column."""
        item = self._tree.itemAt(position)
        if not item or self._tree.columnAt(position.x()) != 0:
            return

        task_id = item.data(0, Qt.ItemDataRole.UserRole)
        if not task_id:
            return

        menu = QMenu(self._tree)
        delete_action = menu.addAction(self._("Delete"))
        selected_action = menu.exec(self._tree.viewport().mapToGlobal(position))
        if selected_action == delete_action:
            self.delete_requested.emit(task_id)

    def _show_status_dialog(self, task_id: str):
        """Show status selection dialog."""
        dialog = QDialog(self._tree)
        dialog.setWindowTitle(self._("Set Status"))
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 20, 24, 20)

        # Title label
        title_label = QLabel(self._("Set Status"))
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        layout.addSpacing(12)

        # Create button for each status
        statuses = [
            ("todo", self._("Todo")),
            ("doing", self._("Doing")),
            ("done", self._("Done")),
            ("timeout", self._("Timeout")),
        ]

        for status_value, status_label in statuses:
            btn = QPushButton(status_label)
            btn.setMinimumHeight(45)
            btn.setMinimumWidth(320)
            btn_font = QFont()
            btn_font.setPointSize(11)
            btn.setFont(btn_font)
            btn.clicked.connect(
                lambda checked, s=status_value: self._on_status_selected(
                    task_id, s, dialog
                )
            )
            layout.addWidget(btn)

        layout.addSpacing(12)

        # Cancel button with internationalization
        cancel_layout = QHBoxLayout()
        cancel_layout.addStretch()
        cancel_btn = QPushButton(self._("Cancel"))
        cancel_btn.setMinimumWidth(120)
        cancel_btn.setMinimumHeight(36)
        cancel_btn.clicked.connect(dialog.reject)
        cancel_layout.addWidget(cancel_btn)
        cancel_layout.addStretch()
        layout.addLayout(cancel_layout)

        dialog.setMinimumWidth(400)
        dialog.exec()

    def _on_status_selected(self, task_id: str, status: str, dialog):
        """Handle status selection."""
        self.status_change_requested.emit(task_id, status)
        dialog.accept()
