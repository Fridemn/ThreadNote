"""Controller wiring for the application."""
from typing import Callable

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from ..ui.main_window import MainWindow
from ..config import load_config
from ..data.storage import DataStore
from ..ui.theme_manager import ThemeManager, Theme


class AppController:
    """Coordinate the application view lifecycle."""

    def __init__(self, translator: Callable[[str], str]) -> None:
        self._window = MainWindow(translator)
        self._config = load_config()
        self._data_store = DataStore(self._config.project_root / "data")
        self._current_theme = Theme.LIGHT
        
        self._setup_connections()
        self._load_initial_data()
        
        # Apply default theme
        self.toggle_theme() # Start with Dark? Or Light? Instructions say "Dynamically Switch".
        # Let's default to Light, toggle makes it dark if I call it once? No, let's be explicit.
        # But for 'Black & White' vibe, maybe Dark is cooler? 
        # Let's stick to Light default unless config says otherwise.
        ThemeManager.apply_theme(QApplication.instance(), self._current_theme)

    def _setup_connections(self):
        """Connect UI signals to controller logic."""
        self._window.editor_widget.content_changed.connect(self._on_editor_content_changed)
        self._window.theme_action.triggered.connect(self.toggle_theme)
        self._window.tree_widget.priority_change_requested.connect(self._on_priority_change_requested)

    def toggle_theme(self):
        """Switch between light and dark mode."""
        if self._current_theme == Theme.LIGHT:
            self._current_theme = Theme.DARK
        else:
            self._current_theme = Theme.LIGHT
        
        ThemeManager.apply_theme(QApplication.instance(), self._current_theme)

    def _load_initial_data(self):
        """Load data from disk and populate UI."""
        if self._data_store.todo_file.exists():
            content = self._data_store.todo_file.read_text(encoding="utf-8")
            self._window.editor_widget.set_content(content)
            tasks = self._data_store.reconcile_tasks(content)
            self._window.tree_widget.refresh(tasks)

    def _on_editor_content_changed(self, content: str):
        """Handle editor text changes."""
        # Debounce or immediate?
        # For now, let's do it immediately but maybe we can optimize later.
        # Actually, reconstructing tree on every keystroke might be heavy.
        # But for MVP, let's try.
        tasks = self._data_store.reconcile_tasks(content)
        self._window.tree_widget.refresh(tasks)
        
        # Auto-save
        self._data_store.save_raw_md(content)
        self._data_store.save_metadata(tasks)

    def _on_priority_change_requested(self, task_id: str):
        """Handle priority change request from tree widget."""
        from ..ui.priority_dialog import PriorityDialog
        
        # Get current content and tasks
        content = self._window.editor_widget.toPlainText()
        tasks = self._data_store.reconcile_tasks(content)
        
        # Find the task
        task = next((t for t in tasks if t.id == task_id), None)
        if not task:
            return
        
        # Show priority dialog with translator
        dialog = PriorityDialog(current_priority=task.priority, translator=self._window._, parent=self._window)
        if dialog.exec() == PriorityDialog.DialogCode.Accepted:
            new_priority = dialog.get_priority()
            if new_priority is not None and new_priority != task.priority:
                # Update task priority
                task.priority = new_priority
                task.touch()
                
                # Save metadata (no MD change needed, priority is only in metadata)
                self._data_store.save_metadata(tasks)
                
                # Refresh tree to show new priority
                self._window.tree_widget.refresh(tasks)

    def show(self) -> None:
        """Show the main window."""
        self._window.show()
