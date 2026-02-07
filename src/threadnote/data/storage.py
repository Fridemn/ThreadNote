"""Data persistence layer handling Markdown and Metadata JSON."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from ..core.task import Task, TaskStatus
from .parser import MarkdownParser
from datetime import datetime


class DataStore:
    """Handles reading/writing of tasks to files."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.todo_file = data_dir / "todo.md"
        self.metadata_file = data_dir / "todo.metadata.json"
        self.archive_file = data_dir / "archive.md"

        self.parser = MarkdownParser()

        # Ensure directory exists
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True, exist_ok=True)

    def reconcile_tasks(self, content: str) -> List[Task]:
        """Parse content and reconcile with metadata."""
        metadata_map = self._load_metadata()
        parsed_items = self.parser.parse(content)  # list of (level, title, content)

        # Reconstruct Tree & Task Objects
        parent_stack: List[Tuple[int, str]] = []
        tasks: List[Task] = []

        # Map: (title, level) -> list of ID candidates
        candidates: Dict[Tuple[str, int], List[str]] = {}
        for tid, meta in metadata_map.items():
            key = (meta.get("title"), meta.get("level"))
            if key not in candidates:
                candidates[key] = []
            candidates[key].append(tid)

        import uuid  # Ensure uuid is imported

        for level, title, body in parsed_items:
            # Find parent (closest item in stack with level < current)
            while parent_stack and parent_stack[-1][0] >= level:
                parent_stack.pop()

            parent_id = parent_stack[-1][1] if parent_stack else None

            # Identify Task
            matched_id = None
            key = (title, level)
            if key in candidates and candidates[key]:
                matched_id = candidates[key].pop(0)  # Take first match

            if matched_id:
                # Update existing task
                meta = metadata_map[matched_id]
                t = Task(
                    id=matched_id,
                    title=title,
                    content=body,
                    level=level,
                    parent_id=parent_id,
                    priority=meta.get("priority", 4),
                    status=TaskStatus(meta.get("status", "todo")),
                    created_at=datetime.fromisoformat(meta.get("created_at"))
                    if meta.get("created_at")
                    else datetime.now(),
                    updated_at=datetime.now(),
                )
            else:
                # New Task
                # Inherit priority from parent if possible
                inherited_priority = 4
                if parent_id:
                    # Find parent task object in 'tasks' list (not efficient O(N), but safe)
                    parent_task = next((pt for pt in tasks if pt.id == parent_id), None)
                    if parent_task:
                        inherited_priority = parent_task.priority

                t = Task(
                    id=str(uuid.uuid4()),
                    title=title,
                    content=body,
                    level=level,
                    parent_id=parent_id,
                    status=TaskStatus.TODO,
                    priority=inherited_priority,
                )

            tasks.append(t)
            parent_stack.append((level, t.id))

        # Build children relationships
        for task in tasks:
            task.children = []

        for task in tasks:
            if task.parent_id:
                parent = next((t for t in tasks if t.id == task.parent_id), None)
                if parent and task.id not in parent.children:
                    parent.children.append(task.id)

        return tasks

    def load_tasks(self) -> List[Task]:
        """Load tasks from todo.md and sync with metadata."""
        if not self.todo_file.exists():
            return []
        content = self.todo_file.read_text(encoding="utf-8")
        return self.reconcile_tasks(content)

    def save_raw_md(self, content: str) -> None:
        """Save raw markdown content."""
        self.todo_file.write_text(content, encoding="utf-8")

    def save_metadata(self, tasks: List[Task]) -> None:
        """Save metadata for tasks."""
        metadata = {}
        for t in tasks:
            metadata[t.id] = {
                "title": t.title,
                "level": t.level,
                "priority": t.priority,
                "status": t.status.value,
                "created_at": t.created_at.isoformat(),
                "updated_at": t.updated_at.isoformat(),
            }
        self.metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    def _load_metadata(self) -> Dict[str, Dict[str, Any]]:
        if not self.metadata_file.exists():
            return {}
        try:
            return json.loads(self.metadata_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def save_tasks(self, tasks: List[Task]) -> None:
        """
        Save tasks to todo.md and todo.metadata.json.
        """
        # 1. Generate Markdown
        # Sort tasks to ensure hierarchy is correct for printing
        # The parser logic expects a flat list in DFS order (Document order)
        # We assume the list passed in is valid, or we need to traverse from roots.

        # Organize by parents to rebuild tree for ordering
        children_map: Dict[Optional[str], List[Task]] = {}

        for t in tasks:
            pid = t.parent_id
            if pid not in children_map:
                children_map[pid] = []
            children_map[pid].append(t)

        # 2. Build ordered list (DFS)
        ordered_tasks: List[Task] = []

        def visit(parent_id: Optional[str]):
            if parent_id in children_map:
                # Sort children? Keeping original order is best if possible.
                # But here we might want to respect the 'Priority' if that's how we display?
                # "Sorting: Priority -> Due -> Created" matches the requirements.
                # BUT, if we reorder the markdown file, the user might be confused.
                # However, requirements say "Sorting: ...".
                # Let's sort by the business logic rules using PriorityQueue logic or simple sort.
                sorted_children = sorted(
                    children_map[parent_id],
                    key=lambda x: (x.priority, x.created_at.timestamp()),
                )

                for child in sorted_children:
                    ordered_tasks.append(child)
                    visit(child.id)

        visit(None)  # Start from roots

        # 3. Write Markdown
        lines = []
        for t in ordered_tasks:
            prefix = "#" * t.level
            lines.append(f"{prefix} {t.title}")
            if t.content:
                lines.append(t.content)
            lines.append("")  # Empty line after content

        self.todo_file.write_text("\n".join(lines), encoding="utf-8")

        # 4. Write Metadata
        metadata = {}
        for t in tasks:
            metadata[t.id] = {
                "title": t.title,
                "level": t.level,
                "priority": t.priority,
                "status": t.status.value,
                "created_at": t.created_at.isoformat(),
                "updated_at": t.updated_at.isoformat(),
            }

        self.metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
