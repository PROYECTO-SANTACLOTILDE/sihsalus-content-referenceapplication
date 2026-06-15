#!/usr/bin/env python3
import csv
import sys
from pathlib import Path


CONFIG_DIR = Path("configuration/backend_configuration")


def main():
    errors = []
    checked = 0

    for path in sorted(CONFIG_DIR.rglob("*.csv")):
        with path.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.reader(handle))

        if not rows:
            continue

        checked += 1
        header_width = len(rows[0])
        for line_number, row in enumerate(rows[1:], start=2):
            if len(row) != header_width:
                errors.append(
                    f"{path}:{line_number}: expected {header_width} columns, "
                    f"found {len(row)}"
                )

    if errors:
        print("CSV width validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated column counts for {checked} CSV files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
