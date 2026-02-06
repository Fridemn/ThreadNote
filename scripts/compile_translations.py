"""Compile .po files to .mo binary format."""
import os
import subprocess
import sys
from pathlib import Path

# Try using Python's msgfmt module
try:
    import polib
    use_polib = True
except ImportError:
    use_polib = False
    # Try system msgfmt as fallback
    pass

def compile_po_file(po_path: Path):
    """Compile a single .po file to .mo."""
    mo_path = po_path.with_suffix('.mo')
    
    if use_polib:
        # Use polib library
        po = polib.pofile(str(po_path))
        po.save_as_mofile(str(mo_path))
        print(f"Compiled {po_path} -> {mo_path}")
    else:
        # Use Python's built-in msgfmt.py
        try:
            from Tools.i18n import msgfmt as python_msgfmt
            python_msgfmt.make(str(po_path), str(mo_path))
            print(f"Compiled {po_path} -> {mo_path}")
        except Exception as e:
            print(f"Warning: Could not compile {po_path}: {e}")
            print("Translations may not work. Install gettext tools or polib library.")

def main():
    """Find and compile all .po files in locales directory."""
    project_root = Path(__file__).resolve().parents[1]
    locales_dir = project_root / "locales"
    
    if not locales_dir.exists():
        print(f"Locales directory not found: {locales_dir}")
        return
    
    po_files = list(locales_dir.rglob("*.po"))
    
    if not po_files:
        print("No .po files found to compile.")
        return
    
    for po_file in po_files:
        compile_po_file(po_file)
    
    print(f"Compilation complete. {len(po_files)} file(s) processed.")

if __name__ == "__main__":
    main()
