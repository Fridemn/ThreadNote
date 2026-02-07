"""Central management of tasks."""

from typing import Dict, List, Optional
import uuid

from .task import Task, TaskStatus
from .priority_queue import TaskPriorityQueue


class TaskManager:
    """Manages CRUD operations and priority ordering of tasks."""

    def __init__(self) -> None:
        self._tasks: Dict[str, Task] = {}
        self._priority_queue = TaskPriorityQueue()

    def create_task(
        self, title: str, level: int = 1, parent_id: Optional[str] = None
    ) -> Task:
        """Create a new task and add it to the manager."""
        task_id = str(uuid.uuid4())
        task = Task(id=task_id, title=title, level=level, parent_id=parent_id)

        self._tasks[task_id] = task

        # If parent exists, link it
        if parent_id and parent_id in self._tasks:
            parent = self._tasks[parent_id]
            parent.children.append(task_id)
            # Inherit priority if not set? (Implementation logic: default is 4, user changes later?
            # Or inherit immediately. Req: "Child tasks inherit parent priority by default")
            if parent.priority != 4:  # If parent has specific priority
                task.priority = parent.priority

        self._refresh_queue()
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID."""
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks."""
        return list(self._tasks.values())

    def update_task(self, task: Task) -> None:
        """Update task in storage and refresh queue."""
        task.touch()
        self._tasks[task.id] = task
        self._refresh_queue()

    def delete_task(self, task_id: str) -> None:
        """Remove a task and its children."""
        if task_id not in self._tasks:
            return

        task = self._tasks[task_id]
        # Remove from parent's children list
        if task.parent_id and task.parent_id in self._tasks:
            parent = self._tasks[task.parent_id]
            if task_id in parent.children:
                parent.children.remove(task_id)

        # Recursively delete children? Or promote them?
        # Usually delete children for a strict tree.
        for child_id in list(task.children):
            self.delete_task(child_id)

        del self._tasks[task_id]
        self._refresh_queue()

    def _refresh_queue(self) -> None:
        """Rebuild the priority queue."""
        # This is expensive (O(N)), optimize later if needed.
        # For a few thousand tasks, it's instant.
        self._priority_queue.clear()
        for task in self._tasks.values():
            if task.status in (TaskStatus.TODO, TaskStatus.DOING):
                self._priority_queue.push(task)

    def get_next_task(self) -> Optional[Task]:
        """Get the highest priority task."""
        return self._priority_queue.peek()
