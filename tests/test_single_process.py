"""Tests for single_process.py"""

from threadnote.utils.single_process import SingleProcessLock


def test_single_process_lock_allows_one_owner(tmp_path):
    """Test that only one owner can hold the process lock."""
    lock_path = tmp_path / "threadnote.lock"
    first = SingleProcessLock(lock_path)
    second = SingleProcessLock(lock_path)

    try:
        if not first.acquire():
            raise AssertionError
        if second.acquire():
            raise AssertionError
    finally:
        first.release()
        second.release()

    try:
        if not second.acquire():
            raise AssertionError
    finally:
        second.release()


def test_single_process_lock_uses_data_dir(tmp_path):
    """Test that the process lock is created in the data directory."""
    process_lock = SingleProcessLock.for_data_dir(tmp_path)

    if process_lock.lock_path != tmp_path / "threadnote.lock":
        raise AssertionError
