# Copilot Instructions for ThreadNote

You are an expert Python developer assisting with the "ThreadNote" project. 

## Project Overview
ThreadNote is a desktop application for multitasking programmers, using Markdown for task management with a focus on quadrants and priority queues.
- **Stack**: Python 3.8+, PyQt6, uv (package manager).
- **Style**: Minimalist Black & White (ChatGPT-like), with Dark/Light mode.

## Critical Implementation Rules

### 1. Coding Standards
- **NO HARDCODING**: Never hardcode paths, colors, labels, or configuration values. Use `config.py`, `constants.py`, or resource files (JSON/YAML) for all literals.
- **Type Hints**: Always use Python type hints (`from typing import ...`).
- **Docstrings**: Include clear docstrings for all classes and functions.
- **MVC Pattern**: Strictly separate Model (logic/data), View (PyQt widgets), and Controller (interaction).

### 2. Task Management Logic
- **Structure**: Markdown headers `#`, `##`, `###` represent 3 levels of tasks. Ignore deeper levels.
- **Storage**: 
  - `todo.md`: Active tasks (Todo, Doing, Timeout).
  - `archive.md`: Completed tasks (Done).
  - **Auto-Save**: Implement debounce for real-time saving (no manual save button).
- **Priority**: 
  - Levels: 1 (Urgent+Important) to 4 (Not Urgent+Not Important).
  - Sorting: Priority -> Due Date -> Created Date.
  - Inheritance: Child tasks inherit parent priority by default but can be overridden.

### 3. UI/UX Guidelines
- **Theme**: Support dynamic Light/Dark mode switching.
- **I18n**: Use `gettext` for all user-facing strings.
- **Layout**: Tree view (Left) + Markdown Editor (Right). Responsive splitter.

### 4. Deployment
- **Packaging**: PyInstaller.
- **Updates**: Check GitHub Releases.

## Project Structure
```
ThreadNote/
├── src/
│   ├── main.py
│   ├── core/          # Business logic, Task model, PriorityQueue
│   ├── ui/            # PyQt6 widgets, styles, themes
│   ├── data/          # File I/O, Markdown parsing
│   └── utils/         # I18n, Config, Helpers
├── docs/              # Documentation
├── tests/             # pytest tests
├── locales/           # Translation files
├── pyproject.toml     # uv config
└── README.md
```
