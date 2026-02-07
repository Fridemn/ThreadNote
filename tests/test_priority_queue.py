"""Tests for priority_queue.py"""

from datetime import datetime
from threadnote.core.task import Task
from threadnote.core.priority_queue import TaskPriorityQueue


def test_priority_queue_init():
    """Test initializing an empty priority queue."""
    pq = TaskPriorityQueue()
    assert len(pq) == 0
    assert pq.peek() is None
    assert pq.pop() is None


def test_priority_queue_push_pop():
    """Test pushing and popping tasks."""
    pq = TaskPriorityQueue()
    task1 = Task(id="1", title="Task 1", priority=2, created_at=datetime(2023, 1, 1))
    task2 = Task(id="2", title="Task 2", priority=1, created_at=datetime(2023, 1, 2))
    task3 = Task(id="3", title="Task 3", priority=2, created_at=datetime(2023, 1, 1))

    pq.push(task1)
    pq.push(task2)
    pq.push(task3)

    # Priority 1 should come first, then for same priority, earlier created_at
    assert pq.pop() == task2  # priority 1
    assert pq.pop() == task1  # priority 2, earlier created
    assert pq.pop() == task3  # priority 2, later created


def test_priority_queue_peek():
    """Test peeking the highest priority task."""
    pq = TaskPriorityQueue()
    task = Task(id="1", title="Task", priority=1)
    pq.push(task)
    assert pq.peek() == task
    assert len(pq) == 1  # peek doesn't remove


def test_priority_queue_clear():
    """Test clearing the queue."""
    pq = TaskPriorityQueue()
    pq.push(Task(id="1", title="Task"))
    assert len(pq) == 1
    pq.clear()
    assert len(pq) == 0
