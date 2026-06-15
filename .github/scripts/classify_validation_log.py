#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

from ci_common import print_errors, require_file


CSV_ERROR_PATTERN = re.compile(
    r"An OpenMRS object could not be constructed or saved from the following CSV line"
    r"|BEGINNING OF CSV FILE ERROR SUMMARY"
    r"|was processed and \d+ out of \d+ entities were not saved"
    r"|No encounter was found for this form"
    r"|ERROR - BaseCsvLoader",
    re.IGNORECASE,
)
FATAL_ERROR_PATTERN = re.compile(
    r"Exception in thread"
    r"|NoClassDefFoundError"
    r"|ClassNotFoundException"
    r"|BeanCreationException"
    r"|OutOfMemoryError"
    r"|Application startup failed"
    r"|Unable to start"
    r"|Failed to start"
    r"|fatal",
    re.IGNORECASE,
)


def matching_lines(log_file: Path, pattern: re.Pattern[str]) -> list[str]:
    return [
        line.rstrip("\n")
        for line in log_file.read_text(encoding="utf-8", errors="replace").splitlines()
        if pattern.search(line)
    ]


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: classify_validation_log.py <log-file>", file=sys.stderr)
        return 2

    log_file = Path(sys.argv[1])
    require_file(log_file, "Validation log")

    csv_hits = matching_lines(log_file, CSV_ERROR_PATTERN)
    fatal_hits = matching_lines(log_file, FATAL_ERROR_PATTERN)

    if csv_hits:
        print_errors(
            f"Found {len(csv_hits)} CSV/Initializer error lines in the SIHSALUS validation log.",
            csv_hits,
        )

    if fatal_hits:
        print_errors("Found fatal runtime errors in the SIHSALUS validation log.", fatal_hits)

    if csv_hits or fatal_hits:
        return 1

    print("Validation log classification complete: no blocking errors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
