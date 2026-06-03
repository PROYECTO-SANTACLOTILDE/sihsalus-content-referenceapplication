#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
csv_file="${repo_root}/configuration/backend_configuration/conceptreferencerange/conceptreferencerange_vital_signs.csv"
ocl_zip="${repo_root}/configuration/backend_configuration/ocl/PeruHCE_SIHSALUS-v4_v12-05-2026-1.2026-05-12_034600.zip"

concept_id="11032370"
openmrs_uuid="18fcbd1f-5b4f-44ed-a664-8637a83cc7eb"

if [[ ! -f "$csv_file" ]]; then
  echo "Reference range CSV not found: $csv_file"
  exit 1
fi

if [[ ! -f "$ocl_zip" ]]; then
  echo "OCL export not found: $ocl_zip"
  exit 1
fi

range_count="$(awk -F, -v uuid="$openmrs_uuid" 'NR > 1 && $2 == uuid { count++ } END { print count + 0 }' "$csv_file")"
if [[ "$range_count" -lt "2" ]]; then
  echo "Expected at least 2 abdominal circumference ranges for ${openmrs_uuid}, found ${range_count}."
  exit 1
fi

require_range() {
  local label="$1"
  local normal_high="$2"
  local critical_high="$3"
  local gender="$4"
  local gender_criteria="\$patient.getGender().equals(\"\"${gender}\"\")"

  awk -F, \
    -v uuid="$openmrs_uuid" \
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

unzip -p "$ocl_zip" export.json | awk \
  -v concept_pattern="\"uuid\": \"${concept_id}\"" \
  -v openmrs_pattern="\"external_id\": \"${openmrs_uuid}\"" '
    index($0, concept_pattern) > 0 {
      found_concept = 1
    }
    index($0, openmrs_pattern) > 0 {
      found_openmrs_uuid = 1
    }
    END {
      if (!found_concept) {
        printf("OCL export does not include concept %s.\n", concept_pattern)
      }
      if (!found_openmrs_uuid) {
        printf("OCL export does not include OpenMRS UUID %s.\n", openmrs_pattern)
      }
      exit(found_concept && found_openmrs_uuid ? 0 : 1)
    }
  '

echo "Reference range validation complete."
