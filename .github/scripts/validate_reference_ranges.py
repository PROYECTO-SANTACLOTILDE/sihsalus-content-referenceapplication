#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
import zipfile
from pathlib import Path

from ci_common import BACKEND_CONFIG_DIR, print_errors, require_dir


RANGE_DIR = BACKEND_CONFIG_DIR / "conceptreferencerange"
OCL_DIR = BACKEND_CONFIG_DIR / "ocl"
CONCEPT_UUID_COLUMN = "Concept Numeric uuid"


def load_export(zip_path: Path) -> dict:
    with zipfile.ZipFile(zip_path) as archive:
        try:
            return json.loads(archive.read("export.json"))
        except KeyError as exc:
            raise ValueError(f"{zip_path}: missing export.json") from exc


def load_concept_identifiers(zip_paths: list[Path]) -> dict[str, str]:
    identifiers: dict[str, str] = {}
    for zip_path in zip_paths:
        export = load_export(zip_path)
        for concept in export.get("concepts", []):
            if concept.get("retired"):
                continue
            for key in ("uuid", "external_id"):
                value = concept.get(key)
                if value:
                    identifiers.setdefault(value, zip_path.name)
    return identifiers


def validate_reference_range_file(
    csv_path: Path,
    concept_identifiers: dict[str, str],
) -> tuple[int, list[str]]:
    checked = 0
    errors: list[str] = []

    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if CONCEPT_UUID_COLUMN not in (reader.fieldnames or []):
            return checked, [f"{csv_path}: missing '{CONCEPT_UUID_COLUMN}' column"]

        for line_number, row in enumerate(reader, start=2):
            checked += 1
            concept_uuid = (row.get(CONCEPT_UUID_COLUMN) or "").strip()
            if not concept_uuid:
                errors.append(f"{csv_path}:{line_number}: empty {CONCEPT_UUID_COLUMN}")
            elif concept_uuid not in concept_identifiers:
                errors.append(
                    f"{csv_path}:{line_number}: {CONCEPT_UUID_COLUMN} not found "
                    f"in bundled OCL exports: {concept_uuid}"
                )

    return checked, errors


def main() -> int:
    require_dir(RANGE_DIR, "Reference range directory")
    require_dir(OCL_DIR, "OCL export directory")

    csv_paths = sorted(RANGE_DIR.glob("*.csv"))
    zip_paths = sorted(OCL_DIR.glob("*.zip"))
    if not csv_paths:
        print(f"No reference range CSV files found in: {RANGE_DIR}", file=sys.stderr)
        return 1
    if not zip_paths:
        print(f"No OCL ZIP exports found in: {OCL_DIR}", file=sys.stderr)
        return 1

    try:
        concept_identifiers = load_concept_identifiers(zip_paths)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    checked = 0
    errors: list[str] = []
    for csv_path in csv_paths:
        file_checked, file_errors = validate_reference_range_file(
            csv_path,
            concept_identifiers,
        )
        checked += file_checked
        errors.extend(file_errors)

    if errors:
        print_errors("Reference range validation failed.", errors)
        return 1

    print(
        f"Validated {checked} reference range rows against "
        f"{len(concept_identifiers)} OCL concept identifiers from {len(zip_paths)} ZIP exports."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
