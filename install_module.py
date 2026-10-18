#!/usr/bin/env python3
"""Install Odoo modules via CLI (avoids browser HTTP timeouts on Docker Desktop)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run_compose(*args: str) -> None:
    cmd = ["docker", "compose", *args]
    print(f"-> {' '.join(cmd)}")
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install Odoo module(s) with --stop-after-init, then start Odoo again."
    )
    parser.add_argument(
        "modules",
        nargs="+",
        help="Technical module names, e.g. account sale stock",
    )
    parser.add_argument(
        "-d",
        "--database",
        required=True,
        help="Odoo database name (the one created in the UI)",
    )
    parser.add_argument(
        "--upgrade",
        action="store_true",
        help="Use -u (upgrade) instead of -i (install)",
    )
    args = parser.parse_args()
    module_list = ",".join(args.modules)
    flag = "-u" if args.upgrade else "-i"

    try:
        run_compose("stop", "odoo")
        run_compose(
            "run",
            "--rm",
            "--no-deps",
            "odoo",
            "odoo",
            "--config=/etc/odoo/odoo.conf",
            "-d",
            args.database,
            flag,
            module_list,
            "--stop-after-init",
        )
        run_compose("start", "odoo")
    except FileNotFoundError:
        print("ERROR: docker not found in PATH.", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: command failed (exit {exc.returncode}).", file=sys.stderr)
        print("Start Odoo again with: docker compose start odoo", file=sys.stderr)
        return 1

    print(f"Done. Installed/upgraded: {module_list} on database {args.database}")
    print("Open http://localhost:8069")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
