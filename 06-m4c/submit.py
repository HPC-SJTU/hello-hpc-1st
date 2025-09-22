#!/usr/bin/env python3
"""
submit.py
Create submit.zip from:
  ./source_code   (recursively, .gitignore aware)
  ./writeup.md
"""
import zipfile
from pathlib import Path
from gitignore import load_gitignore_patterns, walk_files

WORK_DIR = Path(__file__).resolve().parent
MUST_INCLUDE = {
    "writeup.md",
    "source_code/build",
    "source_code/start",
}
IGNORE = {"server"}  # Explicit ignores
SOURCE_DIR = WORK_DIR / "source_code"
WRITEUP_FILE = WORK_DIR / "writeup.md"
ZIP_FILE = WORK_DIR / "submit.zip"

def main() -> None:
    if ZIP_FILE.exists():
        if input("submit.zip exists, overwrite? [N/y]: ").strip().lower() != "y":
            print("Aborted.")
            return
    for p in MUST_INCLUDE:
        if not (WORK_DIR / p).exists():
            print(f"Missing file/dir: {p}")
            return

    # Load .gitignore patterns
    gitignore_patterns = load_gitignore_patterns(SOURCE_DIR)
    print("Adding files:")

    with zipfile.ZipFile(ZIP_FILE, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        # under ./source_code, respecting .gitignore
        for path, arcname in walk_files(SOURCE_DIR, gitignore_patterns, IGNORE):
            arcname = "source_code/"+arcname
            print(" ", arcname)
            zf.write(path, arcname)

        # writeup.md
        arcname = WRITEUP_FILE.relative_to(WORK_DIR)
        print(" ", arcname)
        zf.write(WRITEUP_FILE, arcname)

    print(f"submit.zip created successfully")

if __name__ == "__main__":
    main()
