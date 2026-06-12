#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

csv_file="${repo_root}/configuration/backend_configuration/conceptreferencerange/conceptreferencerange_vital_signs.csv"
ocl_dir="${repo_root}/configuration/backend_configuration/ocl"

# ZIP actual del source sihsalus en la org SIHSALUS.
# Antes era PeruHCE_SIHSALUS-v4_*.zip, pero ahora el source nuevo puede
# tener prefijo numerico para controlar el orden de carga del Initializer.
ocl_zip="$(find "$ocl_dir" -maxdepth 1 -type f -name '*SIHSALUS_sihsalus_*.zip' | sort | tail -n 1)"

openmrs_uuid="18fcbd1f-5b4f-44ed-a664-8637a83cc7eb"
range_concept_uuid="$openmrs_uuid"

if [[ ! -f "$csv_file" ]]; then
  echo "Reference range CSV not found: $csv_file"
  exit 1
fi

if [[ -z "${ocl_zip:-}" || ! -f "$ocl_zip" ]]; then
  echo "OCL export not found in: $ocl_dir"
  echo "Expected a file matching: *SIHSALUS_sihsalus_*.zip"
  echo
  echo "Available OCL ZIPs:"
  find "$ocl_dir" -maxdepth 1 -type f -name '*.zip' -print | sort || true
  exit 1
fi

echo "Using OCL export: $ocl_zip"
