#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import zipfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
BACKEND_CONFIG_DIR = REPO_ROOT / "configuration" / "backend_configuration"

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


def print_errors(title: str, errors: list[str]) -> None:
    print(f"::error::{title}", file=sys.stderr)
    for error in errors:
        print(f"::error::{error}", file=sys.stderr)


def load_ocl_concept_identifiers(ocl_dir: Path) -> dict[str, str]:
    identifiers: dict[str, str] = {}
    zip_paths = sorted(ocl_dir.glob("*.zip"))
    if not zip_paths:
        raise ValueError(f"No OCL ZIP exports found in: {ocl_dir}")

    for zip_path in zip_paths:
        with zipfile.ZipFile(zip_path) as archive:
            try:
                export = json.loads(archive.read("export.json"))
            except KeyError as exc:
                raise ValueError(f"{zip_path}: missing export.json") from exc

        for concept in export.get("concepts", []):
            if concept.get("retired"):
                continue
            for key in ("uuid", "external_id"):
                value = concept.get(key)
                if value:
                    identifiers.setdefault(value, zip_path.name)

    return identifiers


def validate_reference_ranges(_: argparse.Namespace) -> int:
    range_dir = BACKEND_CONFIG_DIR / "conceptreferencerange"
    ocl_dir = BACKEND_CONFIG_DIR / "ocl"
    csv_paths = sorted(range_dir.glob("*.csv"))

    if not range_dir.is_dir():
        print(f"Reference range directory not found: {range_dir}", file=sys.stderr)
        return 1
    if not csv_paths:
        print(f"No reference range CSV files found in: {range_dir}", file=sys.stderr)
        return 1

    try:
        concept_identifiers = load_ocl_concept_identifiers(ocl_dir)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    errors: list[str] = []
    checked = 0
    column = "Concept Numeric uuid"
    for csv_path in csv_paths:
        with csv_path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if column not in (reader.fieldnames or []):
                errors.append(f"{csv_path}: missing '{column}' column")
                continue

            for line_number, row in enumerate(reader, start=2):
                checked += 1
                concept_uuid = (row.get(column) or "").strip()
                if not concept_uuid:
                    errors.append(f"{csv_path}:{line_number}: empty {column}")
                elif concept_uuid not in concept_identifiers:
                    errors.append(
                        f"{csv_path}:{line_number}: {column} not found "
                        f"in bundled OCL exports: {concept_uuid}"
                    )

    if errors:
        print_errors("Reference range validation failed.", errors)
        return 1

    print(
        f"Validated {checked} reference range rows against "
        f"{len(concept_identifiers)} OCL concept identifiers."
    )
    return 0


def classify_validation_log(args: argparse.Namespace) -> int:
    log_file = Path(args.log_file)
    if not log_file.is_file():
        print(f"Validation log not found: {log_file}", file=sys.stderr)
        return 1

    lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
    csv_hits = [line for line in lines if CSV_ERROR_PATTERN.search(line)]
    fatal_hits = [line for line in lines if FATAL_ERROR_PATTERN.search(line)]

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


def main() -> int:
    parser = argparse.ArgumentParser(description="SIHSALUS content CI utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    reference_ranges = subparsers.add_parser("reference-ranges")
    reference_ranges.set_defaults(func=validate_reference_ranges)

    classify_log = subparsers.add_parser("classify-log")
    classify_log.add_argument("log_file")
    classify_log.set_defaults(func=classify_validation_log)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
