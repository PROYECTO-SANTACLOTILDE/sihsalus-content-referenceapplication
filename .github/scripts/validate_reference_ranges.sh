#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

python3 - "$repo_root" <<'PY'
import csv
import json
import re
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

concepts_by_identifier = {}
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
            concepts_by_identifier.setdefault(concept_uuid, concept)
        external_id = concept.get("external_id")
        if external_id:
            concepts_by_identifier.setdefault(external_id, concept)

errors = []
warnings = []
checked = 0
range_uuids = []
range_rows_by_label = {}
inert_pregnancy_criteria = []

CURRENTLY_PREGNANT_UUID = "abaf7d91-e9cb-4569-ab65-2b2ab8226a2c"
BOOLEAN_OBS_RE = re.compile(
    r'getLatestObs\(\s*["\']([^"\']+)["\']\s*,[^)]*\)\.getValueBoolean\(\)'
)

for integer_concept_uuid in [
    "5085AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "5086AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "5242AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "5087AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "5092AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
]:
    concept = concepts_by_identifier.get(integer_concept_uuid)
    allow_decimal = (concept.get("extras") or {}).get("allow_decimal") if concept else None
    if allow_decimal not in {False, 0}:
        errors.append(
            f"OCL concept {integer_concept_uuid} must disallow decimals before "
            "encoding strict NT 042 thresholds as adjacent inclusive integers"
        )

numeric_columns = [
    "Absolute low",
    "Critical low",
    "Normal low",
    "Normal high",
    "Critical high",
    "Absolute high",
]


def as_number(csv_path, line_number, label, field, value, required=False):
    if value is None or not str(value).strip():
        if required:
            errors.append(f"{csv_path}:{line_number}: {label}: empty required {field}")
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        errors.append(f"{csv_path}:{line_number}: {label}: non-numeric {field}: {value!r}")
        return None


def validate_absolute_bounds(csv_path, line_number, label, row, concept):
    if csv_path.name != "conceptreferencerange_vital_signs.csv":
        return

    if concept.get("datatype") != "Numeric":
        errors.append(
            f"{csv_path}:{line_number}: {label}: referenced OCL concept is not Numeric"
        )
        return

    extras = concept.get("extras") or {}
    expected_by_field = {
        "Absolute low": extras.get("low_absolute"),
        "Absolute high": extras.get("hi_absolute"),
    }
    for field, expected_raw in expected_by_field.items():
        actual = as_number(csv_path, line_number, label, field, row.get(field))
        expected = None if expected_raw is None else float(expected_raw)
        if actual != expected:
            errors.append(
                f"{csv_path}:{line_number}: {label}: {field} must match the bundled "
                f"ConceptNumeric absolute bound; expected {expected!r}, got {actual!r}"
            )

    if concept.get("external_id") == "5092AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA":
        critical_high = as_number(
            csv_path, line_number, label, "Critical high", row.get("Critical high")
        )
        if critical_high is not None:
            errors.append(
                f"{csv_path}:{line_number}: {label}: Critical high must be empty; "
                "100% oxygen saturation is not critically high"
            )


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
            elif concept_uuid not in concepts_by_identifier:
                errors.append(
                    f"{csv_path}:{line_number}: Concept Numeric uuid not found "
                    f"in bundled OCL exports: {concept_uuid}"
                )
            else:
                validate_absolute_bounds(
                    csv_path,
                    line_number,
                    label,
                    row,
                    concepts_by_identifier[concept_uuid],
                )

            concept = concepts_by_identifier.get(concept_uuid) or {}
            is_oxygen_saturation = (
                concept.get("external_id")
                == "5092AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            )
            required_numeric_columns = {
                "Critical low",
                "Normal low",
                "Normal high",
            }
            if not is_oxygen_saturation:
                required_numeric_columns.add("Critical high")
            values = [
                as_number(
                    csv_path,
                    line_number,
                    label,
                    column,
                    row.get(column),
                    required=column in required_numeric_columns,
                )
                for column in numeric_columns
            ]
            present_values = [value for value in values if value is not None]
            if present_values != sorted(present_values):
                errors.append(
                    f"{csv_path}:{line_number}: {label}: reference range values "
                    f"must be monotonic when present: {values}"
                )

            criteria = row.get("Criteria") or ""
            if "gestante" in label.lower() and "getLatestObs" in criteria and "!= null" not in criteria:
                errors.append(
                    f"{csv_path}:{line_number}: {label}: gestante criteria must guard "
                    "getLatestObs(...) with != null"
                )

            for boolean_concept_uuid in BOOLEAN_OBS_RE.findall(criteria):
                boolean_concept = concepts_by_identifier.get(boolean_concept_uuid)
                datatype = boolean_concept.get("datatype") if boolean_concept else None
                if datatype == "Boolean":
                    continue
                if boolean_concept_uuid == CURRENTLY_PREGNANT_UUID:
                    inert_pregnancy_criteria.append((csv_path, line_number, label))
                else:
                    errors.append(
                        f"{csv_path}:{line_number}: {label}: getValueBoolean() references "
                        f"{boolean_concept_uuid} with OCL datatype {datatype!r}, not Boolean"
                    )

if inert_pregnancy_criteria:
    if len(inert_pregnancy_criteria) != 26:
        errors.append(
            "Known inert pregnancy-range debt changed unexpectedly: expected 26 "
            f"getValueBoolean() criteria, found {len(inert_pregnancy_criteria)}"
        )
    warnings.append(
        f"{len(inert_pregnancy_criteria)} pregnancy criteria are inert: "
        f"{CURRENTLY_PREGNANT_UUID} is bundled as N/A, so Obs.getValueBoolean() returns null"
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
    value = as_number(
        csv_path, line_number, label, field, row.get(field), required=True
    )
    if value is not None and value != expected:
        errors.append(
            f"{csv_path}:{line_number}: {label}: {field} should be {expected:g} "
            "as the inclusive integer encoding of the NT 042-MINSA/DGSP-V.01 "
            f"priority-I boundary, got {value:g}"
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
    require_value(f"Frecuencia cardiaca {suffix}", "Critical low", 49)
    require_value(f"Frecuencia cardiaca {suffix}", "Critical high", 151)
    require_at_most(f"Frecuencia cardiaca {suffix}", "Absolute low", 49)
    require_at_least(f"Frecuencia cardiaca {suffix}", "Absolute high", 151)

    require_value(f"Presion sistolica {suffix}", "Critical low", 89)
    require_value(f"Presion sistolica {suffix}", "Critical high", 221)
    require_at_most(f"Presion sistolica {suffix}", "Absolute low", 89)
    require_at_least(f"Presion sistolica {suffix}", "Absolute high", 221)

    require_value(f"Presion diastolica {suffix}", "Critical high", 111)
    require_at_least(f"Presion diastolica {suffix}", "Absolute high", 111)

    require_value(f"Frecuencia respiratoria {suffix}", "Critical low", 9)
    require_value(f"Frecuencia respiratoria {suffix}", "Critical high", 36)
    require_at_most(f"Frecuencia respiratoria {suffix}", "Absolute low", 9)
    require_at_least(f"Frecuencia respiratoria {suffix}", "Absolute high", 36)

for label in ["0 - <6 wks", "6 - <1 yrs"]:
    require_value(f"Frecuencia cardiaca {label}", "Critical low", 60)
    require_value(f"Frecuencia cardiaca {label}", "Critical high", 200)
    require_value(f"Presion sistolica {label}", "Critical low", 59)
    require_value(f"Saturación de oxígeno {label}", "Critical low", 85)

require_value("Frecuencia respiratoria 0 - <2 mos", "Critical high", 60)
require_value("Frecuencia respiratoria 2 mos - <1 yrs", "Critical high", 50)

for label in ["1 - <2 yrs", "2 - <6 yrs"]:
    require_value(f"Frecuencia cardiaca {label}", "Critical low", 60)
    require_value(f"Frecuencia cardiaca {label}", "Critical high", 180)
    require_value(f"Presion sistolica {label}", "Critical low", 79)
    require_value(f"Frecuencia respiratoria {label}", "Critical high", 41)
    require_value(f"Saturación de oxígeno {label}", "Critical low", 85)

if errors:
    print("Reference range validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

for warning in warnings:
    print(f"Reference range validation warning: {warning}", file=sys.stderr)

print(
    f"Validated {checked} reference range rows against "
    f"{len(concepts_by_identifier)} OCL concept identifiers from {len(zip_paths)} ZIP exports."
)
PY
