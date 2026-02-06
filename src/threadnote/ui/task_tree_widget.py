"""Task tree view widget."""
from typing import List, Optional
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout, QMenu
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QAction

from ..core.task import Task, TaskStatus

class TaskTreeWidget(QWidget):
    """
    Displays tasks in a hierarchical tree.
    Sorted by Priority -> Due Date -> Created Date.
    """
    
    task_selected = pyqtSignal(str) # Emits task ID
    priority_change_requested = pyqtSignal(str) # Emits task ID for priority change
    status_change_requested = pyqtSignal(str, str) # Emits (task_id, new_status)
    duedate_change_requested = pyqtSignal(str) # Emits task ID for due date change

    def __init__(self, translator=None, parent=None):
        super().__init__(parent)
        self._ = translator if translator else lambda x: x
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels([self._("Task"), self._("Prio"), self._("Status")])
        self._tree.setColumnWidth(0, 200)
        self._tree.setColumnWidth(1, 50)
        self._tree.itemClicked.connect(self._on_item_clicked)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._show_context_menu)
        
        self._layout.addWidget(self._tree)

    def refresh(self, tasks: List[Task]):
        """Rebuild the tree from list of tasks."""
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
            # Same sort as PriorityQueue: Prio (asc), Due (asc/inf), Created (asc)
            due = t.due_date.timestamp() if t.due_date else float('inf')
            return (t.priority, due, t.created_at.timestamp())

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
                if t.status.value == 'done':
                    # Gray out and strikethrough
                    from PyQt6.QtGui import QFont, QColor
                    font = item.font(0)
                    font.setStrikeOut(True)
                    for col in range(3):
                        item.setFont(col, font)
                        item.setForeground(col, QColor(128, 128, 128))
                elif t.status.value == 'doing':
                    # Bold for active tasks
                    from PyQt6.QtGui import QFont
                    font = item.font(0)
                    font.setBold(True)
                    item.setFont(0, font)
                elif t.status.value == 'timeout':
                    # Red text for timeout
                    from PyQt6.QtGui import QColor
                    item.setForeground(0, QColor(200, 0, 0))
                
                # Recursion
                if t.id in children_map:
                    add_items(item, children_map[t.id])
                
                # Expand by default if high priority?
                if t.priority <= 2:
                    item.setExpanded(True)

        add_items(self._tree, roots)

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        task_id = item.data(0, Qt.ItemDataRole.UserRole)
        if task_id:
            self.task_selected.emit(task_id)
    
    def _show_context_menu(self, position):
        """Show context menu for task operations."""
        item = self._tree.itemAt(position)
        if not item:
            return
        
        task_id = item.data(0, Qt.ItemDataRole.UserRole)
        if not task_id:
            return
        
        menu = QMenu(self._tree)
        
        priority_action = QAction(self._("Set Priority..."), self._tree)
        priority_action.triggered.connect(lambda: self.priority_change_requested.emit(task_id))
        menu.addAction(priority_action)
        
        # Due date action
        duedate_action = QAction(self._("Set Due Date"), self._tree)
        duedate_action.triggered.connect(lambda: self.duedate_change_requested.emit(task_id))
        menu.addAction(duedate_action)
        
        menu.addSeparator()
        
        # Status submenu
        status_menu = menu.addMenu(self._("Set Status"))
        
        status_todo = QAction(self._("Todo"), self._tree)
        status_todo.triggered.connect(lambda: self.status_change_requested.emit(task_id, "todo"))
        status_menu.addAction(status_todo)
        
        status_doing = QAction(self._("Doing"), self._tree)
        status_doing.triggered.connect(lambda: self.status_change_requested.emit(task_id, "doing"))
        status_menu.addAction(status_doing)
        
        status_done = QAction(self._("Done"), self._tree)
        status_done.triggered.connect(lambda: self.status_change_requested.emit(task_id, "done"))
        status_menu.addAction(status_done)
        
        status_timeout = QAction(self._("Timeout"), self._tree)
        status_timeout.triggered.connect(lambda: self.status_change_requested.emit(task_id, "timeout"))
        status_menu.addAction(status_timeout)
        
        menu.exec(self._tree.viewport().mapToGlobal(position))
