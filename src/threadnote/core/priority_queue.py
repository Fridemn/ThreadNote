"""Priority queue logic for tasks."""
import heapq
from datetime import datetime
from typing import List, Optional, Tuple

from .task import Task


class TaskPriorityQueue:
    """
    Manages tasks based on priority rules:
    1. Priority (1-4, Ascending)
    2. Created Date (Earliest first)
    """

    def __init__(self) -> None:
        # Tuple structure: (sort_key, task)
        # sort_key: (priority, created_at_timestamp)
        self._heap: List[Tuple[Tuple[int, float], Task]] = []

    def push(self, task: Task) -> None:
        """Add a task to the priority queue."""
        created_ts = task.created_at.timestamp()
        
        sort_key = (task.priority, created_ts, task.id)
        heapq.heappush(self._heap, (sort_key, task))

    def pop(self) -> Optional[Task]:
        """Remove and return the highest priority task."""
        if not self._heap:
            return None
        return heapq.heappop(self._heap)[1]

    def peek(self) -> Optional[Task]:
        """View the highest priority task without removing it."""
        if not self._heap:
            return None
        return self._heap[0][1]

    def clear(self) -> None:
        """Empty the queue."""
        self._heap.clear()

    def __len__(self) -> int:
        return len(self._heap)
