"""Main window for ThreadNote."""

from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QCloseEvent, QIcon, QKeySequence
from PyQt6.QtWidgets import (
    QMainWindow,
    QMenu,
    QSplitter,
    QStatusBar,
    QSystemTrayIcon,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from ..constants import APP_NAME, DEFAULT_WINDOW_SIZE
from ..utils.resources import get_resource_path
from .editor_widget import EditorWidget
from .task_tree_widget import TaskTreeWidget


class MainWindow(QMainWindow):
    """Primary application window."""

    def __init__(self, translator: Callable[[str], str]) -> None:
        super().__init__()
        self._ = translator
        self._force_quit = False  # Flag for actual quit vs minimize to tray
        self._init_ui()
        self._configure_window()
        self._init_tray_icon()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        # Toolbar
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        # Actions (Theme Toggle placeholder)
        self.theme_action = QAction(self._("Toggle Theme"), self)
        self.theme_action.setShortcut(QKeySequence("Ctrl+T"))
        self.toolbar.addAction(self.theme_action)

        self.toolbar.addSeparator()

        # Archive action
        self.archive_action = QAction(self._("Archive"), self)
        self.archive_action.setShortcut(QKeySequence("Ctrl+Shift+A"))
        self.toolbar.addAction(self.archive_action)

        self.toolbar.addSeparator()

        # Language switch action
        self.language_action = QAction(self._("Language"), self)
        self.language_action.setShortcut(QKeySequence("Ctrl+L"))
        self.toolbar.addAction(self.language_action)

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

        is_collapsible = False
        self.splitter.setCollapsible(0, is_collapsible)
        self.splitter.setCollapsible(1, is_collapsible)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        main_layout.addWidget(self.splitter)

        # Status bar for temporary messages
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Additional shortcuts (not in toolbar)
        self._setup_shortcuts()

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Ctrl+S: Manual save (even though we auto-save)
        save_action = QAction(self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(lambda: None)  # Auto-save already handles this
        self.addAction(save_action)

        # Ctrl+F: Focus editor (search in the future)
        focus_editor_action = QAction(self)
        focus_editor_action.setShortcut(QKeySequence.StandardKey.Find)
        focus_editor_action.triggered.connect(self.editor_widget.setFocus)
        self.addAction(focus_editor_action)

    def _configure_window(self) -> None:
        """Configure the window title and size."""
        self.setWindowTitle(self._(APP_NAME))
        width, height = DEFAULT_WINDOW_SIZE
        self.resize(width, height)
        self.splitter.setSizes(
            [self.tree_widget.PREFERRED_WIDTH, width - self.tree_widget.PREFERRED_WIDTH]
        )

        # Set window icon
        icon_path = get_resource_path("logo.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

    def show_temporary_message(self, message: str, duration_ms: int = 3000) -> None:
        """Show a temporary message in the status bar."""
        self.status_bar.showMessage(message, duration_ms)

    def show_and_activate(self) -> None:
        """Show the window and request focus."""
        if self.isMinimized():
            self.showNormal()
        else:
            self.show()
        self.setWindowState(self.windowState() | Qt.WindowState.WindowActive)
        self.raise_()
        self.activateWindow()

    def _init_tray_icon(self) -> None:
        """Initialize system tray icon."""
        # Get icon
        icon_path = get_resource_path("logo.png")
        icon = QIcon(str(icon_path)) if icon_path.exists() else QIcon()

        # Create tray icon
        self.tray_icon = QSystemTrayIcon(icon, self)

        # Create tray menu
        tray_menu = QMenu()

        # Show/Hide action
        show_action = tray_menu.addAction(self._("Show/Hide"))
        show_action.triggered.connect(self._toggle_window_visibility)

        tray_menu.addSeparator()

        # Quit action
        quit_action = tray_menu.addAction(self._("Quit"))
        quit_action.triggered.connect(self.quit_application)

        # Set menu and show tray icon
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_icon_activated)
        self.tray_icon.show()

        # Set tooltip
        self.tray_icon.setToolTip(self._(APP_NAME))

    def _toggle_window_visibility(self) -> None:
        """Toggle window visibility."""
        if self.isVisible():
            self.hide()
        else:
            self.show_and_activate()

    def _on_tray_icon_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Handle tray icon activation (click)."""
        # On left click, toggle window visibility
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._toggle_window_visibility()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Override close event to minimize to tray instead of quitting."""
        if not self._force_quit:
            # Just hide the window
            event.ignore()
            self.hide()

            # Show a tray message on first minimize
            if not hasattr(self, "_first_minimize_shown"):
                self.tray_icon.showMessage(
                    self._(APP_NAME),
                    self._(
                        "Application minimized to tray. Right-click the tray icon to quit."
                    ),
                    QSystemTrayIcon.MessageIcon.Information,
                    3000,
                )
                self._first_minimize_shown = True
        else:
            # Actually quit - hide tray icon and accept close event
            self.tray_icon.hide()
            event.accept()
            # Quit the application to ensure process exits
            from PyQt6.QtWidgets import QApplication

            QApplication.quit()

    def quit_application(self) -> None:
        """Actually quit the application."""
        self._force_quit = True
        self.close()
