"""Task tree view widget."""
from typing import List, Optional
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt

from ..core.task import Task, TaskStatus

class TaskTreeWidget(QWidget):
    """
    Displays tasks in a hierarchical tree.
    Sorted by Priority -> Due Date -> Created Date.
    """
    
    task_selected = pyqtSignal(str) # Emits task ID

    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["Task", "Prio", "Status"])
        self._tree.setColumnWidth(0, 200)
        self._tree.setColumnWidth(1, 50)
        self._tree.itemClicked.connect(self._on_item_clicked)
        
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
                item.setText(2, t.status.value)
                item.setData(0, Qt.ItemDataRole.UserRole, t.id)
                
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
