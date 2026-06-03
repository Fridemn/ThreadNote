"""Single-process locking for ThreadNote."""

from pathlib import Path

from PyQt6.QtCore import QLockFile


class SingleProcessLock:
    """Hold a lock file while the application is running."""

    def __init__(self, lock_path: Path) -> None:
        self.lock_path = lock_path
        self._lock_file = QLockFile(str(lock_path))
        self._lock_file.setStaleLockTime(0)

    @classmethod
    def for_data_dir(cls, data_dir: Path) -> "SingleProcessLock":
        """Create the process lock in the application's data directory."""
        return cls(data_dir / "threadnote.lock")

    def acquire(self) -> bool:
        """Try to acquire the lock without waiting."""
        return self._lock_file.tryLock(0)

    def release(self) -> None:
        """Release the lock if this process owns it."""
        if self._lock_file.isLocked():
            self._lock_file.unlock()
