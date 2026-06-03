"""Single-process locking for ThreadNote."""

from pathlib import Path
from time import time_ns

from PyQt6.QtCore import QLockFile, QObject, QTimer, pyqtSignal


class SingleProcessLock:
    """Hold a lock file while the application is running."""

    def __init__(self, lock_path: Path) -> None:
        self.lock_path = lock_path
        self.activation_path = lock_path.with_suffix(".activate")
        self._lock_file = QLockFile(str(lock_path))
        self._lock_file.setStaleLockTime(0)

    @classmethod
    def for_data_dir(cls, data_dir: Path) -> "SingleProcessLock":
        """Create the process lock in the application's data directory."""
        return cls(data_dir / "threadnote.lock")

    def acquire(self) -> bool:
        """Try to acquire the lock without waiting."""
        return self._lock_file.tryLock(0)

    def request_activation(self) -> bool:
        """Ask the running instance to show itself."""
        try:
            self.activation_path.parent.mkdir(exist_ok=True)
            self.activation_path.write_text(f"{time_ns()}\n", encoding="utf-8")
        except OSError:
            return False
        return True

    def release(self) -> None:
        """Release the lock if this process owns it."""
        if self._lock_file.isLocked():
            self._lock_file.unlock()


class ActivationServer(QObject):
    """Poll a local activation file for requests from later launches."""

    activation_requested = pyqtSignal()

    def __init__(self, activation_path: Path, poll_interval_ms: int = 250) -> None:
        super().__init__()
        self.activation_path = activation_path
        self._last_seen_token = ""
        self._timer = QTimer(self)
        self._timer.setInterval(poll_interval_ms)
        self._timer.timeout.connect(self._poll_activation_file)

    def listen(self) -> bool:
        """Start listening for activation requests."""
        try:
            self.activation_path.parent.mkdir(exist_ok=True)
        except OSError:
            return False

        self._last_seen_token = self._read_activation_token()
        self._timer.start()
        return True

    def close(self) -> None:
        """Stop listening for activation requests."""
        self._timer.stop()

    def _poll_activation_file(self) -> None:
        token = self._read_activation_token()
        if not token or token == self._last_seen_token:
            return

        self._last_seen_token = token
        self.activation_requested.emit()

    def _read_activation_token(self) -> str:
        try:
            return self.activation_path.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            return ""
        except OSError:
            return ""
