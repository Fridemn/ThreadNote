#!/usr/bin/env python3
"""Build script for ThreadNote using PyInstaller."""

import subprocess
import sys
from pathlib import Path


def main():
    """Run the build process."""
    project_root = Path(__file__).parent.parent

    print("=" * 60)
    print("ThreadNote 打包脚本")
    print("=" * 60)
    print()

    # Step 1: Compile translations
    print("步骤 1/3: 编译翻译文件...")
    try:
        subprocess.run(
            [sys.executable, "scripts/compile_translations.py"],
            cwd=project_root,
            check=True,
        )
        print("✓ 翻译文件编译完成")
    except subprocess.CalledProcessError as e:
        print(f"✗ 翻译文件编译失败: {e}")
        return 1
    print()

    # Step 2: Check PyInstaller
    print("步骤 2/3: 检查 PyInstaller...")
    try:
        result = subprocess.run(
            ["uv", "run", "pyinstaller", "--version"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"✓ PyInstaller 版本: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ PyInstaller 未安装，正在安装...")
        try:
            subprocess.run(
                ["uv", "add", "--dev", "pyinstaller"], cwd=project_root, check=True
            )
            print("✓ PyInstaller 安装完成")
        except subprocess.CalledProcessError as e:
            print(f"✗ PyInstaller 安装失败: {e}")
            return 1
    print()

    # Step 3: Build with PyInstaller
    print("步骤 3/3: 使用 PyInstaller 打包...")
    try:
        subprocess.run(
            ["uv", "run", "pyinstaller", "ThreadNote.spec"],
            cwd=project_root,
            check=True,
        )
        print("✓ 打包完成")
    except subprocess.CalledProcessError as e:
        print(f"✗ 打包失败: {e}")
        return 1
    print()

    # Display results
    dist_path = project_root / "dist" / "ThreadNote.exe"
    if dist_path.exists():
        size_mb = dist_path.stat().st_size / (1024 * 1024)
        print("=" * 60)
        print("打包成功！")
        print(f"输出文件: {dist_path}")
        print(f"文件大小: {size_mb:.2f} MB")
        print("=" * 60)
    else:
        print("✗ 未找到输出文件")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
