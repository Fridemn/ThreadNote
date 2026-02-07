"""Tests for storage.py"""
import json
import pytest
from pathlib import Path
from threadnote.data.storage import DataStore
from threadnote.core.task import Task, TaskStatus


def test_load_metadata(tmp_path):
    """Test loading metadata from JSON file."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    metadata_file = data_dir / "todo.metadata.json"
    metadata = {
        "1": {
            "title": "Task 1",
            "level": 1,
            "priority": 1,
            "status": "todo",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
    }
    metadata_file.write_text(json.dumps(metadata), encoding="utf-8")

    store = DataStore(data_dir)
    loaded = store._load_metadata()
    assert loaded == metadata


def test_load_metadata_missing_file(tmp_path):
    """Test loading metadata when file doesn't exist."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    store = DataStore(data_dir)
    loaded = store._load_metadata()
    assert loaded == {}


def test_save_metadata(tmp_path):
    """Test saving metadata to JSON file."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    store = DataStore(data_dir)

    tasks = [
        Task(id="1", title="Task 1", level=1, priority=1, status=TaskStatus.TODO)
    ]
    store.save_metadata(tasks)

    metadata_file = data_dir / "todo.metadata.json"
    assert metadata_file.exists()
    loaded = json.loads(metadata_file.read_text(encoding="utf-8"))
    assert "1" in loaded
    assert loaded["1"]["title"] == "Task 1"