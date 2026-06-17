#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

python3 - "$repo_root" <<'PY'
import csv
import json
import sys
import zipfile
from collections import Counter
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
range_uuids = []
range_rows_by_label = {}
numeric_columns = [
    "Absolute low",
    "Critical low",
    "Normal low",
    "Normal high",
    "Critical high",
    "Absolute high",
]


def as_number(csv_path, line_number, label, field, value):
    try:
        return float(value)
    except (TypeError, ValueError):
        errors.append(f"{csv_path}:{line_number}: {label}: non-numeric {field}: {value!r}")
        return None


for csv_path in csv_paths:
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if "Concept Numeric uuid" not in (reader.fieldnames or []):
            errors.append(f"{csv_path}: missing 'Concept Numeric uuid' column")
            continue
        for column in ["Uuid", "Label", *numeric_columns, "Criteria"]:
            if column not in (reader.fieldnames or []):
                errors.append(f"{csv_path}: missing '{column}' column")

        for line_number, row in enumerate(reader, start=2):
            checked += 1
            label = (row.get("Label") or "").strip()
            range_uuid = (row.get("Uuid") or "").strip()
            if range_uuid:
                range_uuids.append((range_uuid, csv_path, line_number))
            if label:
                range_rows_by_label[label] = (csv_path, line_number, row)

            concept_uuid = (row.get("Concept Numeric uuid") or "").strip()
            if not concept_uuid:
                errors.append(f"{csv_path}:{line_number}: empty Concept Numeric uuid")
            elif concept_uuid not in concept_uuids:
                errors.append(
                    f"{csv_path}:{line_number}: Concept Numeric uuid not found "
                    f"in bundled OCL exports: {concept_uuid}"
                )

            values = [
                as_number(csv_path, line_number, label, column, row.get(column))
                for column in numeric_columns
            ]
            if all(value is not None for value in values) and values != sorted(values):
                errors.append(
                    f"{csv_path}:{line_number}: {label}: reference range values "
                    f"must be monotonic: {values}"
                )

            criteria = row.get("Criteria") or ""
            if "gestante" in label.lower() and "getLatestObs" in criteria and "!= null" not in criteria:
                errors.append(
                    f"{csv_path}:{line_number}: {label}: gestante criteria must guard "
                    "getLatestObs(...) with != null"
                )

duplicates = [uuid for uuid, count in Counter(uuid for uuid, _, _ in range_uuids).items() if count > 1]
if duplicates:
    for duplicate_uuid in duplicates:
        locations = [
            f"{csv_path}:{line_number}"
            for uuid, csv_path, line_number in range_uuids
            if uuid == duplicate_uuid
        ]
        errors.append(f"Duplicate reference range UUID {duplicate_uuid}: {', '.join(locations)}")


def require_value(label, field, expected):
    if label not in range_rows_by_label:
        errors.append(f"Missing reference range row required by NT 042-MINSA/DGSP-V.01: {label}")
        return
    csv_path, line_number, row = range_rows_by_label[label]
    value = as_number(csv_path, line_number, label, field, row.get(field))
    if value is not None and value != expected:
        errors.append(
            f"{csv_path}:{line_number}: {label}: {field} should be {expected:g} "
            f"per NT 042-MINSA/DGSP-V.01 priority-I vital signs, got {value:g}"
        )


def require_at_most(label, field, threshold):
    if label not in range_rows_by_label:
        errors.append(f"Missing reference range row required by NT 042-MINSA/DGSP-V.01: {label}")
        return
    csv_path, line_number, row = range_rows_by_label[label]
    value = as_number(csv_path, line_number, label, field, row.get(field))
    if value is not None and value > threshold:
        errors.append(
            f"{csv_path}:{line_number}: {label}: {field} must be <= {threshold:g} "
            f"to avoid rejecting/underflagging NT 042-MINSA/DGSP-V.01 priority-I values; got {value:g}"
        )


def require_at_least(label, field, threshold):
    if label not in range_rows_by_label:
        errors.append(f"Missing reference range row required by NT 042-MINSA/DGSP-V.01: {label}")
        return
    csv_path, line_number, row = range_rows_by_label[label]
    value = as_number(csv_path, line_number, label, field, row.get(field))
    if value is not None and value < threshold:
        errors.append(
            f"{csv_path}:{line_number}: {label}: {field} must be >= {threshold:g} "
            f"to avoid rejecting/underflagging NT 042-MINSA/DGSP-V.01 priority-I values; got {value:g}"
        )


adult_labels = ["adulto 18 - <60 yrs", "adulto mayor >=60 yrs"]
for suffix in adult_labels:
    require_value(f"Frecuencia cardiaca {suffix}", "Critical low", 50)
    require_value(f"Frecuencia cardiaca {suffix}", "Critical high", 150)
    require_at_most(f"Frecuencia cardiaca {suffix}", "Absolute low", 50)
    require_at_least(f"Frecuencia cardiaca {suffix}", "Absolute high", 150)

    require_value(f"Presion sistolica {suffix}", "Critical low", 90)
    require_value(f"Presion sistolica {suffix}", "Critical high", 220)
    require_at_most(f"Presion sistolica {suffix}", "Absolute low", 90)
    require_at_least(f"Presion sistolica {suffix}", "Absolute high", 220)

    require_value(f"Presion diastolica {suffix}", "Critical high", 110)
    require_at_least(f"Presion diastolica {suffix}", "Absolute high", 110)

    require_value(f"Frecuencia respiratoria {suffix}", "Critical low", 10)
    require_value(f"Frecuencia respiratoria {suffix}", "Critical high", 35)
    require_at_most(f"Frecuencia respiratoria {suffix}", "Absolute low", 10)
    require_at_least(f"Frecuencia respiratoria {suffix}", "Absolute high", 35)

for label in ["0 - <6 wks", "6 - <1 yrs"]:
    require_value(f"Frecuencia cardiaca {label}", "Critical low", 60)
    require_value(f"Frecuencia cardiaca {label}", "Critical high", 200)
    require_value(f"Presion sistolica {label}", "Critical low", 60)
    require_value(f"Saturación de oxígeno {label}", "Critical low", 85)

require_value("Frecuencia respiratoria 0 - <2 mos", "Critical high", 60)
require_value("Frecuencia respiratoria 2 mos - <1 yrs", "Critical high", 50)

for label in ["1 - <2 yrs", "2 - <6 yrs"]:
    require_value(f"Frecuencia cardiaca {label}", "Critical low", 60)
    require_value(f"Frecuencia cardiaca {label}", "Critical high", 180)
    require_value(f"Presion sistolica {label}", "Critical low", 80)
    require_value(f"Frecuencia respiratoria {label}", "Critical high", 40)
    require_value(f"Saturación de oxígeno {label}", "Critical low", 85)

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
