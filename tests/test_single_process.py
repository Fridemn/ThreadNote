"""Tests for single_process.py"""

from time import sleep

from PyQt6.QtCore import QCoreApplication

from threadnote.utils.single_process import ActivationServer, SingleProcessLock


def _get_app():
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    return app


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


def test_single_process_lock_uses_activation_file_next_to_lock(tmp_path):
    """Test that the activation file is created next to the lock file."""
    process_lock = SingleProcessLock(tmp_path / "threadnote.lock")

    if process_lock.activation_path != tmp_path / "threadnote.activate":
        raise AssertionError


def test_activation_request_notifies_server(tmp_path):
    """Test that a later launch can request activation from the owner process."""
    app = _get_app()
    process_lock = SingleProcessLock(tmp_path / "threadnote.lock")
    server = ActivationServer(process_lock.activation_path, poll_interval_ms=1)
    activations = []
    server.activation_requested.connect(lambda: activations.append(True))

    try:
        if not server.listen():
            raise AssertionError
        if not process_lock.request_activation():
            raise AssertionError

        for _ in range(20):
            app.processEvents()
            if activations:
                break
            sleep(0.01)

        if not activations:
            raise AssertionError
    finally:
        server.close()
