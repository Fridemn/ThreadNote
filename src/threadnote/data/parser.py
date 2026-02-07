"""Markdown parsing logic with support for task extraction."""

import re
from typing import List, Tuple

from ..core.task import Task


class MarkdownParser:
    """Parses markdown content into hierarchical structure."""

    # Regex to match headers: # Title, ## Title, etc.
    HEADER_PATTERN = re.compile(r"^(#{1,3})\s+(.+)$")

    def parse(self, content: str) -> List[Tuple[int, str, str]]:
        """
        Parse markdown content into a flat list of logic blocks.
        Returns list of (level, title, content_body).
        Level 1-3 corresponds to #, ##, ###.
        Content body is the text following the header until the next header.
        """
        lines = content.splitlines()
        parsed_items: List[Tuple[int, str, List[str]]] = []

        current_level = 0
        current_title = ""
        current_content: List[str] = []

        for line in lines:
            match = self.HEADER_PATTERN.match(line)
            if match:
                # Flush previous item if it exists and is a task (level > 0)
                if current_level > 0:
                    parsed_items.append(
                        (
                            current_level,
                            current_title,
                            "\n".join(current_content).strip(),
                        )
                    )

                # Start new item
                hashes, title = match.groups()
                current_level = len(hashes)
                current_title = title.strip()
                current_content = []
            else:
                # Accumulate content
                # If we haven't found a header yet, this is preamble text (ignore or attach to root?)
                # Requirement: "Structure: #, ##, ### ... Ignore deeper levels."
                # We interpret text before first header as ignored or belonging to 'root' (which we don't have).
                # For now, append if we are inside a task.
                if current_level > 0:
                    current_content.append(line)

        # Flush last item
        if current_level > 0:
            parsed_items.append(
                (current_level, current_title, "\n".join(current_content).strip())
            )

        # Convert list format if needed, for now returning tuples
        return [(lvl, title, content) for lvl, title, content in parsed_items]

    def to_markdown(self, tasks: List[Task]) -> str:
        """
        Convert tasks back to markdown.
        Note: This is complex because tasks are a tree.
        We need to traverse the tree (Depth First Pre-order) to generate MD.
        """
        # This requires the Task objects to be linked with children.
        # Use a helper that takes a list of root tasks, or handle the flat list if they are ordered.
        # Assuming TaskManager provides full list or tree.
        # For now, let's implement a tree traverser if given root tasks.
        pass  # TODO: Implement generator based on Tree structure
