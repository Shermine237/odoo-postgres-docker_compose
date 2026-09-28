#!/usr/bin/env python3
"""Reset Odoo/Postgres volumes to a fresh-install state.

Stops containers, wipes runtime data (DB, filestore, logs),
keeps odoo.conf and custom addons, then optionally restarts the stack.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Directories wiped on reset (content only; folder + .gitkeep kept)
WIPE_DIRS = [
    ROOT / "volumes" / "postgres-data",
    ROOT / "volumes" / "odoo" / "web-data",
    ROOT / "logs",
]

KEEP_NAMES = {".gitkeep"}


def run_compose(*args: str) -> None:
    cmd = ["docker", "compose", *args]
    print(f"→ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=ROOT, check=True)


def clear_directory(path: Path) -> int:
    """Remove everything in path except KEEP_NAMES. Recreate dir if missing."""
    path.mkdir(parents=True, exist_ok=True)
    removed = 0
    for child in path.iterdir():
        if child.name in KEEP_NAMES:
            continue
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink(missing_ok=True)
        removed += 1
        print(f"  removed: {child.relative_to(ROOT)}")
    if removed == 0:
        print(f"  (already empty) {path.relative_to(ROOT)}")
    return removed


def confirm(force: bool) -> bool:
    if force:
        return True
    print("This will DELETE:")
    for d in WIPE_DIRS:
        print(f"  - {d.relative_to(ROOT)}/*")
    print("Kept: volumes/odoo/conf/odoo.conf, addons/")
    answer = input("Continue? [y/N] ").strip().lower()
    return answer in {"y", "yes"}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Clean Odoo/Postgres volumes (fresh install)."
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip confirmation prompt",
    )
    parser.add_argument(
        "--up",
        action="store_true",
        help="Restart stack with docker compose up -d after cleanup",
    )
    parser.add_argument(
        "--no-down",
        action="store_true",
        help="Do not run docker compose down (volumes must be unused)",
    )
    args = parser.parse_args()

    if not confirm(args.yes):
        print("Aborted.")
        return 1

    if not args.no_down:
        try:
            run_compose("down")
        except FileNotFoundError:
            print("ERROR: docker not found in PATH.", file=sys.stderr)
            return 1
        except subprocess.CalledProcessError as exc:
            print(f"ERROR: docker compose down failed (exit {exc.returncode}).", file=sys.stderr)
            return 1

    print("Cleaning volumes...")
    total = 0
    for directory in WIPE_DIRS:
        print(f"* {directory.relative_to(ROOT)}")
        total += clear_directory(directory)

    # Ensure .gitkeep exists after wipe
    for directory in WIPE_DIRS:
        keep = directory / ".gitkeep"
        if not keep.exists():
            keep.touch()

    print(f"Done. Removed {total} item(s). Fresh install ready.")
    print("Preserved: volumes/odoo/conf/odoo.conf and addons/")

    if args.up:
        try:
            run_compose("up", "-d")
        except subprocess.CalledProcessError as exc:
            print(f"ERROR: docker compose up failed (exit {exc.returncode}).", file=sys.stderr)
            return 1
        print("Stack started. Open http://localhost:8069")
    else:
        print("Start again with: docker compose up -d")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
