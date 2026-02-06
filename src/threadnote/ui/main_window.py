"""Main window for ThreadNote."""
from typing import Callable
from PyQt6.QtWidgets import QMainWindow, QSplitter, QWidget, QVBoxLayout, QToolBar
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

from ..constants import APP_NAME, DEFAULT_WINDOW_SIZE
from .editor_widget import EditorWidget
from .task_tree_widget import TaskTreeWidget
from .priority_dialog import PriorityDialog
from ..core.task import Task

class MainWindow(QMainWindow):
    """Primary application window."""

    def __init__(self, translator: Callable[[str], str]) -> None:
        super().__init__()
        self._ = translator
        self._init_ui()
        self._configure_window()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        # Toolbar
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        
        # Actions (Theme Toggle placeholder)
        self.theme_action = QAction(self._("Toggle Theme"), self)
        self.toolbar.addAction(self.theme_action)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Tree
        self.tree_widget = TaskTreeWidget(translator=self._)
        self.splitter.addWidget(self.tree_widget)
        
        # Right: Editor
        self.editor_widget = EditorWidget(translator=self._)
        self.splitter.addWidget(self.editor_widget)
        
        # Set initial sizes (30% left, 70% right)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 7)

        main_layout.addWidget(self.splitter)

    def _configure_window(self) -> None:
        """Configure the window title and size."""
        self.setWindowTitle(self._(APP_NAME))
        width, height = DEFAULT_WINDOW_SIZE
        self.resize(width, height)
