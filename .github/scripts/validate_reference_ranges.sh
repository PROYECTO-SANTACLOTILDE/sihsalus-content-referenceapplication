#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
csv_file="${repo_root}/configuration/backend_configuration/conceptreferencerange/conceptreferencerange_vital_signs.csv"
ocl_dir="${repo_root}/configuration/backend_configuration/ocl"

openmrs_uuid="18fcbd1f-5b4f-44ed-a664-8637a83cc7eb"
range_concept_uuid="$openmrs_uuid"

if [[ ! -f "$csv_file" ]]; then
  echo "Reference range CSV not found: $csv_file"
  exit 1
fi

if [[ ! -d "$ocl_dir" ]]; then
  echo "OCL export directory not found: $ocl_dir"
  exit 1
fi

# ZIP actual del source sihsalus en la org SIHSALUS.
# Antes era PeruHCE_SIHSALUS-v4_*.zip, pero ahora el source nuevo es SIHSALUS_sihsalus_v*.zip.
ocl_zip="$(find "$ocl_dir" -maxdepth 1 -type f -name 'SIHSALUS_sihsalus_v*.zip' | sort | tail -n 1)"
if [[ -z "${ocl_zip:-}" || ! -f "$ocl_zip" ]]; then
  echo "OCL export not found in: $ocl_dir"
  echo "Expected a file matching: SIHSALUS_sihsalus_v*.zip"
  echo
  echo "Available OCL ZIPs:"
  find "$ocl_dir" -maxdepth 1 -type f -name '*.zip' -print | sort || true
  exit 1
fi

echo "Using OCL export: $ocl_zip"

range_count="$(awk -F, -v uuid="$range_concept_uuid" 'NR > 1 && $2 == uuid { count++ } END { print count + 0 }' "$csv_file")"
if [[ "$range_count" -lt "2" ]]; then
  echo "Expected at least 2 abdominal circumference ranges for ${range_concept_uuid}, found ${range_count}."
  exit 1
fi

require_range() {
  local label="$1"
  local normal_high="$2"
  local critical_high="$3"
  local gender="$4"
  local gender_criteria="\$patient.getGender().equals(\"\"${gender}\"\")"

  awk -F, \
    -v uuid="$range_concept_uuid" \
    -v label="$label" \
    -v normal_high="$normal_high" \
    -v critical_high="$critical_high" \
    -v gender_criteria="$gender_criteria" '
      $2 == uuid && $3 == label {
        found = 1
        if ($4 != "0" || $5 != "0" || $6 != "0" || $7 != normal_high || $8 != critical_high || $9 != "200") {
          printf("Unexpected thresholds for %s\n", label)
          exit 2
        }
        if (index($10, "$patient.getAge() >= 18") == 0 || index($10, gender_criteria) == 0) {
          printf("Unexpected criteria for %s: %s\n", label, $10)
          exit 3
        }
      }
      END {
        if (!found) {
          exit 1
        }
      }
    ' "$csv_file" || {
      echo "Missing or invalid abdominal circumference range: ${label}"
      exit 1
    }
}

require_range "Perimetro abdominal adulto mujer >=18 yrs" "79.9" "88" "F"
require_range "Perimetro abdominal adulto hombre >=18 yrs" "93.9" "102" "M"

node -e '
  const fs = require("node:fs");
  const externalId = process.argv[1];
  const raw = fs.readFileSync(0, "utf8");
  const data = JSON.parse(raw);
  const concepts = Array.isArray(data.concepts) ? data.concepts : [];
  const concept = concepts.find((candidate) => candidate.external_id === externalId);

  if (!concept) {
    console.error(`OCL export does not include OpenMRS UUID ${externalId}.`);
    process.exit(1);
  }

  if (concept.datatype !== "Numeric") {
    console.error(`Expected abdominal circumference concept datatype Numeric, found ${concept.datatype}.`);
    process.exit(1);
  }

  console.log(`Validated OCL concept ${concept.id} (${concept.display_name}) for OpenMRS UUID ${externalId}.`);
' "$openmrs_uuid" < <(unzip -p "$ocl_zip" export.json)

echo "Reference range validation complete."
