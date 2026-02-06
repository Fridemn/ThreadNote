"""Task data model."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class TaskStatus(str, Enum):
    """Task lifecycle states."""
    TODO = "todo"
    DOING = "doing"
    DONE = "done"
    TIMEOUT = "timeout"


@dataclass
class Task:
    """Represents a single task in the system."""
    id: str
    title: str
    content: str = ""
    level: int = 1  # 1=Urgent+Important, 4=Not Urgent+Not Important in priority context?
                    # Wait, level is Markdown header level (1-3).
                    # Priority is separate (1-4).
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    priority: int = 4  # Default: Not Urgent + Not Important
    status: TaskStatus = TaskStatus.TODO
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None

    def touch(self) -> None:
        """Update the modification timestamp."""
        self.updated_at = datetime.now()
