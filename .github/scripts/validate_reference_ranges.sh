#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

python3 - "$repo_root" <<'PY'
import csv
import json
import sys
import zipfile
from pathlib import Path


repo_root = Path(sys.argv[1])
range_dir = repo_root / "configuration/backend_configuration/conceptreferencerange"
ocl_dir = repo_root / "configuration/backend_configuration/ocl"

csv_paths = sorted(range_dir.glob("*.csv"))
zip_paths = sorted(ocl_dir.glob("*.zip"))

if not csv_paths:
    raise SystemExit(f"No reference range CSV files found in: {range_dir}")

if not zip_paths:
    raise SystemExit(f"No OCL ZIP exports found in: {ocl_dir}")

concept_uuids = {}
for zip_path in zip_paths:
    with zipfile.ZipFile(zip_path) as archive:
        try:
            export = json.loads(archive.read("export.json"))
        except KeyError as exc:
            raise SystemExit(f"{zip_path}: missing export.json") from exc

    for concept in export.get("concepts", []):
        if concept.get("retired"):
            continue
        concept_uuid = concept.get("uuid")
        if concept_uuid:
            concept_uuids.setdefault(concept_uuid, zip_path.name)
        external_id = concept.get("external_id")
        if external_id:
            concept_uuids.setdefault(external_id, zip_path.name)

errors = []
checked = 0
for csv_path in csv_paths:
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if "Concept Numeric uuid" not in (reader.fieldnames or []):
            errors.append(f"{csv_path}: missing 'Concept Numeric uuid' column")
            continue

        for line_number, row in enumerate(reader, start=2):
            checked += 1
            concept_uuid = (row.get("Concept Numeric uuid") or "").strip()
            if not concept_uuid:
                errors.append(f"{csv_path}:{line_number}: empty Concept Numeric uuid")
            elif concept_uuid not in concept_uuids:
                errors.append(
                    f"{csv_path}:{line_number}: Concept Numeric uuid not found "
                    f"in bundled OCL exports: {concept_uuid}"
                )

if errors:
    print("Reference range validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

print(
    f"Validated {checked} reference range rows against "
    f"{len(concept_uuids)} OCL concept identifiers from {len(zip_paths)} ZIP exports."
)
PY
