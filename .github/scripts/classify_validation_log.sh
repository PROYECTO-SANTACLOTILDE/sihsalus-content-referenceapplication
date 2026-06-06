#!/usr/bin/env bash
set -euo pipefail

log_file="${1:?usage: classify_validation_log.sh <log-file>}"

if [[ ! -f "$log_file" ]]; then
  echo "::error::Validation log not found: $log_file"
  exit 1
fi

csv_pattern='(An OpenMRS object could not be constructed or saved from the following CSV line|BEGINNING OF CSV FILE ERROR SUMMARY|was processed and [0-9]+ out of [0-9]+ entities were not saved|No encounter was found for this form|failed to validate with reason|ERROR - BaseCsvLoader|ERROR - BaseFileLoader|ERROR - CommonsLoggingOutput\.error)'
fatal_pattern='(Exception in thread|NoClassDefFoundError|ClassNotFoundException|BeanCreationException|OutOfMemoryError|Application startup failed|Unable to start|Failed to start|fatal)'

csv_hits="$(grep -Ei "$csv_pattern" "$log_file" || true)"
fatal_hits="$(grep -Ei "$fatal_pattern" "$log_file" || true)"

has_errors=0

if [[ -n "$csv_hits" ]]; then
  csv_count="$(printf '%s\n' "$csv_hits" | sed '/^$/d' | wc -l | tr -d ' ')"
  echo "::error::Found ${csv_count} CSV/Initializer error lines in the SIHSALUS validation log."
  printf '%s\n' "$csv_hits" | sed 's/^/::error::/g'
  has_errors=1
fi

if [[ -n "$fatal_hits" ]]; then
  echo "::error::Found fatal runtime errors in the SIHSALUS validation log."
  printf '%s\n' "$fatal_hits" | sed 's/^/::error::/g'
  has_errors=1
fi

if [[ "$has_errors" -ne 0 ]]; then
  exit 1
fi

echo "Validation log classification complete: no blocking errors."
