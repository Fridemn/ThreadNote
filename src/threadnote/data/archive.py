"""Archive management for completed tasks."""

from pathlib import Path
from typing import List, Callable

from ..core.task import Task, TaskStatus
from .parser import MarkdownParser


class ArchiveManager:
    """Manages archiving of completed tasks."""

    def __init__(self, data_dir: Path, translator: Callable[[str], str] = None):
        self.data_dir = data_dir
        self.archive_file = data_dir / "archive.md"
        self.parser = MarkdownParser()
        self._ = translator if translator else lambda x: x

    def archive_completed_tasks(self, tasks: List[Task]) -> List[Task]:
        """
        Move completed tasks to archive.md and return remaining tasks.
        """
        active_tasks = []
        completed_tasks = []

        for task in tasks:
            if task.status == TaskStatus.DONE:
                completed_tasks.append(task)
            else:
                active_tasks.append(task)

        if completed_tasks:
            self._append_to_archive(completed_tasks)

        return active_tasks

    def _append_to_archive(self, tasks: List[Task]):
        """Append tasks to archive.md file."""
        # Load existing archive content
        existing_content = ""
        if self.archive_file.exists():
            existing_content = self.archive_file.read_text(encoding="utf-8")

        # Build hierarchy for completed tasks (Tree traversal)
        children_map = {t.id: [] for t in tasks}
        task_map = {t.id: t for t in tasks}
        roots = []

        for t in tasks:
            if t.parent_id and t.parent_id in task_map:
                children_map[t.parent_id].append(t)
            else:
                roots.append(t)

        # Generate markdown for completed tasks
        lines = []

        def render_task(task: Task, depth: int = 0):
            prefix = "#" * task.level
            lines.append(f"{prefix} {task.title}")
            if task.content:
                lines.append(task.content)
            lines.append("")

            # Render children
            if task.id in children_map:
                for child in children_map[task.id]:
                    render_task(child, depth + 1)

        # Add timestamp header
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"\n**{self._('Archived on')} {timestamp}**\n")

        for root in roots:
            render_task(root)

        new_content = "\n".join(lines)

        # Append to archive
        if existing_content:
            full_content = existing_content + "\n\n" + new_content
        else:
            full_content = new_content

        self.archive_file.write_text(full_content, encoding="utf-8")
