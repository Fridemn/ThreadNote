"""Markdown editor widget."""

from __future__ import annotations

import re
from dataclasses import dataclass

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


@dataclass
class MarkdownPage:
    """One top-level markdown task page."""

    title: str
    body: str = ""


class EditorWidget(QWidget):
    """Markdown editor with one page per level-1 heading."""

    content_changed = pyqtSignal(str)

    _ROOT_HEADING_PATTERN = re.compile(r"^#\s+(.+)$")

    def __init__(self, translator=None, parent=None):
        super().__init__(parent)
        self._ = translator or (lambda x: x)
        self._pages: list[MarkdownPage] = []
        self._current_index = 0
        self._updating = False

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._tab_layout = QHBoxLayout()
        self._tab_layout.setContentsMargins(4, 4, 4, 4)
        self._tab_layout.setSpacing(6)
        self._layout.addLayout(self._tab_layout)

        self._editor = QTextEdit()
        self._editor.setPlaceholderText(self._("Details..."))
        self._editor.textChanged.connect(self._on_text_changed)
        self._layout.addWidget(self._editor)

        self._rebuild_tabs()

    def setFocus(self):  # noqa: N802
        """Focus the markdown text editor."""
        self._editor.setFocus()

    def toPlainText(self) -> str:  # noqa: N802
        """Return the full markdown document."""
        self._save_current_page()
        return self._compose_content()

    def set_content(self, content: str):
        """Update content without triggering signal loop if possible."""
        self._updating = True
        self._pages = self._split_pages(content)
        self._current_index = min(self._current_index, max(len(self._pages) - 1, 0))
        self._rebuild_tabs()
        self._load_current_page()
        self._updating = False

    def _on_text_changed(self):
        if self._updating:
            return
        self._sync_current_page_from_editor()
        self.content_changed.emit(self._compose_content())

    def _switch_page(self, index: int):
        if index == self._current_index or index < 0 or index >= len(self._pages):
            return

        self._save_current_page()
        self._current_index = index
        self._rebuild_tabs()
        self._load_current_page()

    def _add_page(self):
        self._save_current_page()
        base_title = self._("New Task")
        title = self._unique_title(base_title)
        self._pages.append(MarkdownPage(title=title))
        self._current_index = len(self._pages) - 1
        self._rebuild_tabs()
        self._load_current_page()
        self.content_changed.emit(self._compose_content())

    def _save_current_page(self):
        if not self._pages:
            return
        self._sync_current_page_from_editor(reload_on_split=False)

    def _load_current_page(self):
        self._updating = True
        if not self._pages:
            self._editor.clear()
        else:
            self._editor.setPlainText(self._page_to_markdown(self._pages[self._current_index]))
        self._updating = False

    def _rebuild_tabs(self):
        while self._tab_layout.count():
            item = self._tab_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not self._pages:
            self._pages.append(MarkdownPage(title=self._("New Task")))

        for index, page in enumerate(self._pages):
            tab = QLineEdit(page.title)
            tab.setReadOnly(True)
            tab.setMinimumWidth(120)
            tab.setMaximumWidth(180)
            tab.setProperty("active", index == self._current_index)
            tab.setStyleSheet(
                "QLineEdit { padding: 3px 6px; }"
                "QLineEdit[active='true'] { border: 1px solid palette(highlight); }"
            )
            tab.mousePressEvent = self._make_tab_mouse_press_handler(tab, index)
            self._tab_layout.addWidget(tab)

        add_button = QPushButton("+")
        add_button.setFixedWidth(28)
        add_button.clicked.connect(self._add_page)
        self._tab_layout.addWidget(add_button)
        self._tab_layout.addStretch()

    def _make_tab_mouse_press_handler(self, tab: QLineEdit, index: int):
        original_handler = tab.mousePressEvent

        def handler(event):
            if index != self._current_index:
                self._switch_page(index)
                return
            original_handler(event)

        return handler

    def _sync_current_page_from_editor(self, *, reload_on_split: bool = True):
        if not self._pages:
            return

        old_page_count = len(self._pages)
        old_titles = [page.title for page in self._pages]
        fallback_title = self._pages[self._current_index].title
        parsed_pages = self._split_pages(
            self._editor.toPlainText(),
            fallback_title=fallback_title,
        )
        if not parsed_pages:
            return

        start_index = self._current_index
        self._pages[start_index : start_index + 1] = parsed_pages
        if len(parsed_pages) > 1:
            self._current_index = start_index + len(parsed_pages) - 1
        elif self._current_index >= len(self._pages):
            self._current_index = len(self._pages) - 1

        page_count_changed = old_page_count != len(self._pages)
        titles_changed = old_titles != [page.title for page in self._pages]
        if page_count_changed or titles_changed:
            self._rebuild_tabs()

        if page_count_changed and reload_on_split:
            self._load_current_page()
            self._move_cursor_to_end()

    def _move_cursor_to_end(self):
        cursor = self._editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self._editor.setTextCursor(cursor)
        self._editor.setFocus()

    def _split_pages(
        self,
        content: str,
        fallback_title: str | None = None,
    ) -> list[MarkdownPage]:
        lines = content.splitlines()
        pages: list[MarkdownPage] = []
        current_title = ""
        current_body: list[str] = []

        def flush_page():
            if current_title:
                pages.append(MarkdownPage(current_title, "\n".join(current_body).strip()))

        for line in lines:
            match = self._ROOT_HEADING_PATTERN.match(line)
            if match:
                flush_page()
                current_title = match.group(1).strip()
                current_body = []
            elif current_title:
                current_body.append(line)
            elif line.strip():
                current_title = fallback_title or self._("New Task")
                current_body = [line]

        flush_page()
        return pages or [MarkdownPage(title=fallback_title or self._("New Task"))]

    def _compose_content(self) -> str:
        return "\n\n".join(self._page_to_markdown(page) for page in self._pages)

    def _page_to_markdown(self, page: MarkdownPage) -> str:
        title = page.title.strip() or self._("New Task")
        chunk_lines = [f"# {title}"]
        body = page.body.strip()
        if body:
            chunk_lines.append(body)
        return "\n".join(chunk_lines)

    def _unique_title(self, base_title: str) -> str:
        existing_titles = {page.title for page in self._pages}
        if base_title not in existing_titles:
            return base_title

        index = 2
        while f"{base_title} {index}" in existing_titles:
            index += 1
        return f"{base_title} {index}"
