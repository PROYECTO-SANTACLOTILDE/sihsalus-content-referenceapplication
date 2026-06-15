#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
BACKEND_CONFIG_DIR = REPO_ROOT / "configuration" / "backend_configuration"


def print_errors(title: str, errors: Iterable[str]) -> None:
    print(f"::error::{title}", file=sys.stderr)
    for error in errors:
        print(f"::error::{error}", file=sys.stderr)


def require_file(path: Path, label: str = "File") -> None:
    if not path.is_file():
        raise SystemExit(f"{label} not found: {path}")


def require_dir(path: Path, label: str = "Directory") -> None:
    if not path.is_dir():
        raise SystemExit(f"{label} not found: {path}")
