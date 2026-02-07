"""Controller wiring for the application."""

import sys
import subprocess
from typing import Callable, List

from PyQt6.QtWidgets import QApplication

from ..ui.main_window import MainWindow
from ..config import load_config
from ..data.storage import DataStore
from ..data.archive import ArchiveManager
from ..ui.theme_manager import ThemeManager, Theme
from ..core.task import Task
from ..utils.preferences import UserPreferences


class AppController:
    """Coordinate the application view lifecycle."""

    def __init__(
        self, translator: Callable[[str], str], preferences: UserPreferences
    ) -> None:
        self._window = MainWindow(translator)
        self._config = load_config()
        self._prefs = preferences
        self._archive_manager = ArchiveManager(
            self._config.project_root / "data", translator
        )
        self._data_store = DataStore(self._config.project_root / "data")

        # Load saved theme or default to LIGHT
        saved_theme = self._prefs.get_theme()
        self._current_theme = Theme(saved_theme) if saved_theme else Theme.LIGHT

        self._setup_connections()
        self._load_initial_data()

        # Apply saved theme
        ThemeManager.apply_theme(QApplication.instance(), self._current_theme)

    def _setup_connections(self):
        """Connect UI signals to controller logic."""
        self._window.editor_widget.content_changed.connect(
            self._on_editor_content_changed
        )
        self._window.theme_action.triggered.connect(self.toggle_theme)
        self._window.tree_widget.priority_change_requested.connect(
            self._on_priority_change_requested
        )
        self._window.tree_widget.status_change_requested.connect(
            self._on_status_change_requested
        )
        self._window.archive_action.triggered.connect(self._on_archive_requested)
        self._window.language_action.triggered.connect(
            self._on_language_change_requested
        )

    def toggle_theme(self):
        """Switch between light and dark mode."""
        if self._current_theme == Theme.LIGHT:
            self._current_theme = Theme.DARK
        else:
            self._current_theme = Theme.LIGHT

        # Save theme preference
        self._prefs.set_theme(self._current_theme.value)
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
        dialog = PriorityDialog(
            current_priority=task.priority,
            translator=self._window._,
            parent=self._window,
        )
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

    def _on_status_change_requested(self, task_id: str, new_status: str):
        """Handle status change request from tree widget."""
        from ..core.task import TaskStatus

        # Get current content and tasks
        content = self._window.editor_widget.toPlainText()
        tasks = self._data_store.reconcile_tasks(content)

        # Find the task
        task = next((t for t in tasks if t.id == task_id), None)
        if not task:
            return

        # Update status
        try:
            task.status = TaskStatus(new_status)
            task.touch()

            # Save metadata
            self._data_store.save_metadata(tasks)

            # Auto-archive: Check if we should archive a complete task tree
            archived_count = self._check_and_archive_complete_trees(tasks)

            if archived_count > 0:
                # Tasks were archived, need to refresh everything
                # Refresh UI
                new_content = self._data_store.todo_file.read_text(encoding="utf-8")
                self._window.editor_widget.set_content(new_content)
                reloaded_tasks = self._data_store.reconcile_tasks(new_content)
                self._window.tree_widget.refresh(reloaded_tasks)

                # Show temporary message
                if archived_count == 1:
                    message = self._window._("1 task archived")
                else:
                    message = self._window._("{} tasks archived").format(archived_count)
                self._window.show_temporary_message(message)
            else:
                # Just refresh tree to show new status
                self._window.tree_widget.refresh(tasks)
        except ValueError:
            # Invalid status value
            pass

    def _on_archive_requested(self):
        """Open a read-only view of the archive document."""
        from ..ui.archive_view_dialog import ArchiveViewDialog

        dialog = ArchiveViewDialog(
            archive_file=self._data_store.archive_file,
            translator=self._window._,
            parent=self._window,
        )
        dialog.exec()

    def _regenerate_markdown(self, tasks: List[Task]):
        """Regenerate todo.md from task list."""
        # Build hierarchy
        children_map = {t.id: [] for t in tasks}
        task_map = {t.id: t for t in tasks}
        roots = []

        for t in tasks:
            if t.parent_id and t.parent_id in task_map:
                children_map[t.parent_id].append(t)
            else:
                roots.append(t)

        # Sort function
        def sort_key(t):
            return (t.priority, t.created_at.timestamp())

        # Generate markdown
        lines = []

        def render_task(task: Task):
            prefix = "#" * task.level
            lines.append(f"{prefix} {task.title}")
            if task.content:
                lines.append(task.content)
            lines.append("")

            # Render children (sorted)
            if task.id in children_map:
                sorted_children = sorted(children_map[task.id], key=sort_key)
                for child in sorted_children:
                    render_task(child)

        # Render roots (sorted)
        sorted_roots = sorted(roots, key=sort_key)
        for root in sorted_roots:
            render_task(root)

        content = "\n".join(lines)
        self._data_store.save_raw_md(content)

    def _check_and_archive_complete_trees(self, tasks: List[Task]) -> int:
        """
        Check for complete task trees (root + all descendants done) and archive them.
        Returns the number of tasks archived.
        """

        # Build task map for quick lookup
        task_map = {t.id: t for t in tasks}

        # Find root tasks (tasks without parent or parent not in task list)
        root_tasks = [
            t for t in tasks if not t.parent_id or t.parent_id not in task_map
        ]

        # Check each root task tree
        tasks_to_archive = []
        for root in root_tasks:
            if self._is_task_tree_complete(root, task_map):
                # Collect entire subtree
                subtree = self._collect_task_subtree(root, task_map)
                tasks_to_archive.extend(subtree)

        if tasks_to_archive:
            # Separate active and archived tasks
            task_ids_to_archive = {t.id for t in tasks_to_archive}
            active_tasks = [t for t in tasks if t.id not in task_ids_to_archive]

            # Archive the completed tasks using archive manager
            self._archive_manager._append_to_archive(tasks_to_archive)

            # Regenerate markdown from active tasks only
            self._regenerate_markdown(active_tasks)

            # Save metadata for active tasks
            self._data_store.save_metadata(active_tasks)

            return len(tasks_to_archive)

        return 0

    def _is_task_tree_complete(self, task: Task, task_map: dict) -> bool:
        """Check if a task and all its descendants are marked as DONE."""
        from ..core.task import TaskStatus

        if task.status != TaskStatus.DONE:
            return False

        # Check all children recursively
        for child_id in task.children:
            if child_id in task_map:
                child = task_map[child_id]
                if not self._is_task_tree_complete(child, task_map):
                    return False

        return True

    def _collect_task_subtree(self, task: Task, task_map: dict) -> List[Task]:
        """Collect a task and all its descendants."""
        subtree = [task]

        for child_id in task.children:
            if child_id in task_map:
                child = task_map[child_id]
                subtree.extend(self._collect_task_subtree(child, task_map))

        return subtree

    def _on_language_change_requested(self):
        """Show language selection dialog."""
        from ..ui.language_dialog import LanguageDialog
        import locale

        current_locale, _ = locale.getdefaultlocale()
        current_locale = current_locale or "en"

        dialog = LanguageDialog(
            current_locale=current_locale,
            translator=self._window._,
            parent=self._window,
        )
        if dialog.exec() == LanguageDialog.DialogCode.Accepted:
            new_locale = dialog.get_selected_locale()
            if new_locale:
                # Save locale to preferences
                self._prefs.set_locale(new_locale)

                # Restart application immediately
                subprocess.Popen([sys.executable, "-m", "threadnote"])
                QApplication.quit()

    def show(self) -> None:
        """Show the main window."""
        self._window.show()
