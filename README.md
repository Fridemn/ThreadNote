# ThreadNote

**ThreadNote** 是一款专为程序员和多线程工作者设计的极简主义桌面端任务管理应用。它结合了 Markdown 的简洁性与四象限法则（Eisenhower Matrix）及计算机科学中的优先级队列逻辑，旨在极大提升工作效率。

## ✨ 功能特性

- **基于 Markdown**: 使用 `#`, `##`, `###` 标题轻松组织任务层级。
- **优先级管理**: 
  - **四象限法则**: 根据紧急与重要程度对任务进行分类。
  - **优先级队列**: 基于优先级规则自动对应任务进行排序。
- **任务生命周期**: 追踪任务的 `待办 (Todo)`, `进行中 (Doing)`, `完成 (Done)`, 和 `超时 (Timeout)` 状态。
- **自动归档**: 已完成的任务会自动移动到 `archive.md` 文件中。
- **多任务工作流**: 支持处理包含嵌套子任务（最多3级）的复杂项目。
- **极简 UI**: 清爽的黑白设计风格，支持亮色/暗色模式切换。
- **国际化**: 支持多语言 (i18n)。

## 🛠 技术栈

- **语言**: Python 3.8+
- **GUI 框架**: PyQt6
- **包管理器**: [uv](https://github.com/astral-sh/uv)
- **数据格式**: Markdown

## 🚀 快速开始

### 前置要求

确保已安装：

- Python 3.8+
- [uv](https://github.com/astral-sh/uv)

### 安装步骤

1. **克隆仓库**

   ```bash
   git clone https://github.com/yourusername/ThreadNote.git
   cd ThreadNote
   ```

2. **安装依赖**

   ```bash
   uv sync
   ```

3. **编译翻译文件**

   首次运行前建议先编译本地化文件，否则语言切换可能不会生效。

   ```bash
   uv run python scripts/compile_translations.py
   ```

4. **运行应用**

   推荐使用项目脚本启动：

   ```bash
   uv run threadnote
   ```

   也可以使用 Python 模块方式启动：

   ```bash
   uv run python -m threadnote
   ```

## 🏗 开发指南

### 项目结构

- `src/threadnote/core`: 业务逻辑与数据模型。
- `src/threadnote/ui`: PyQt6 组件与窗口管理。
- `src/threadnote/data`: Markdown 解析与文件持久化。
- `src/threadnote/utils`: 辅助函数，包括 i18n 和配置管理。
- `data/todo.md`: 当前任务 Markdown 数据。
- `data/todo.metadata.json`: 任务优先级、状态等元数据。

### 打包发布

项目已提供 PyInstaller 配置文件 `ThreadNote.spec` 和打包脚本 `scripts/build.py`。

1. **安装开发依赖**

   ```bash
   uv sync --group dev
   ```

2. **执行打包脚本**

   ```bash
   uv run python scripts/build.py
   ```

   该脚本会先编译翻译文件，再调用：

   ```bash
   uv run pyinstaller ThreadNote.spec
   ```

3. **查看产物**

   Windows 下输出文件通常为：

   ```text
   dist/ThreadNote.exe
   ```

   macOS / Linux 下输出文件通常为：

   ```text
   dist/ThreadNote
   ```

如需手动打包，可直接运行：

```bash
uv run python scripts/compile_translations.py
uv run pyinstaller ThreadNote.spec
```
