#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
classifier="${script_dir}/classify_validation_log.sh"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

printf '%s\n' 'OpenMRS started without content errors.' > "$tmp_dir/clean.log"
bash "$classifier" "$tmp_dir/clean.log" >/dev/null

printf '%s\n' 'ERROR - BaseCsvLoader: row was not saved' > "$tmp_dir/csv.log"
if bash "$classifier" "$tmp_dir/csv.log" >/dev/null 2>&1; then
  echo "Classifier accepted a BaseCsvLoader error" >&2
  exit 1
fi

printf 'binary-prefix\0ERROR - BaseFileLoader: duplicate file\n' > "$tmp_dir/file.log"
if bash "$classifier" "$tmp_dir/file.log" >/dev/null 2>&1; then
  echo "Classifier accepted a BaseFileLoader error after a NUL byte" >&2
  exit 1
fi

printf '%s\n' \
  'ERROR - LiquibaseLoader.load(72) | Visit Note contract precondition failed' \
  'INFO - BaseFileLoader.load(84) | liquibase has finished loading' > "$tmp_dir/liquibase.log"
if bash "$classifier" "$tmp_dir/liquibase.log" >/dev/null 2>&1; then
  echo "Classifier accepted a LiquibaseLoader error followed by a success-looking line" >&2
  exit 1
fi

printf '%s\n' 'Application startup failed' > "$tmp_dir/fatal.log"
if bash "$classifier" "$tmp_dir/fatal.log" >/dev/null 2>&1; then
  echo "Classifier accepted a fatal runtime error" >&2
  exit 1
fi

echo "Validated clean, CSV, BaseFileLoader, Liquibase fail-fast, and fatal log fixtures."
