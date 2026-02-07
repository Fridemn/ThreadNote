"""Tests for task.py"""
import pytest
import time
from datetime import datetime
from threadnote.core.task import Task, TaskStatus


def test_task_creation():
    """Test creating a Task instance."""
    task = Task(id="1", title="Test Task")
    assert task.id == "1"
    assert task.title == "Test Task"
    assert task.content == ""
    assert task.level == 1
    assert task.parent_id is None
    assert task.children == []
    assert task.priority == 4
    assert task.status == TaskStatus.TODO
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)


def test_task_touch():
    """Test the touch method updates updated_at."""
    task = Task(id="1", title="Test Task")
    old_updated = task.updated_at
    time.sleep(0.001)  # Ensure time difference
    task.touch()
    assert task.updated_at > old_updated


def test_task_status_enum():
    """Test TaskStatus enum values."""
    assert TaskStatus.TODO == "todo"
    assert TaskStatus.DOING == "doing"
    assert TaskStatus.DONE == "done"
    assert TaskStatus.TIMEOUT == "timeout"