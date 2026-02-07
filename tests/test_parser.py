"""Tests for parser.py"""

from threadnote.data.parser import MarkdownParser


def test_parse_simple_headers():
    """Test parsing simple markdown headers."""
    content = """# Task 1
Some content for task 1.

## Subtask 1.1
Content for subtask.

# Task 2
Content for task 2.
"""
    parser = MarkdownParser()
    result = parser.parse(content)
    expected = [
        (1, "Task 1", "Some content for task 1."),
        (2, "Subtask 1.1", "Content for subtask."),
        (1, "Task 2", "Content for task 2."),
    ]
    assert result == expected


def test_parse_no_headers():
    """Test parsing content with no headers."""
    content = "Just some text."
    parser = MarkdownParser()
    result = parser.parse(content)
    assert result == []


def test_parse_only_headers():
    """Test parsing only headers without content."""
    content = "# Task 1\n## Task 2\n### Task 3"
    parser = MarkdownParser()
    result = parser.parse(content)
    expected = [(1, "Task 1", ""), (2, "Task 2", ""), (3, "Task 3", "")]
    assert result == expected
