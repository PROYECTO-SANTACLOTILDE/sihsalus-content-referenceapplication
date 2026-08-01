#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: wait_for_maven_central.sh <version> [max-attempts] [retry-delay-seconds]" >&2
}

if (( $# < 1 || $# > 3 )); then
  usage
  exit 2
fi

version="$1"
max_attempts="${2:-90}"
retry_delay_seconds="${3:-30}"

if [[ ! "$version" =~ ^[A-Za-z0-9][A-Za-z0-9._+-]*$ ]]; then
  echo "Invalid Maven version: ${version}" >&2
  exit 2
fi

if [[ ! "$max_attempts" =~ ^[1-9][0-9]*$ ]]; then
  echo "max-attempts must be a positive integer: ${max_attempts}" >&2
  exit 2
fi

if [[ ! "$retry_delay_seconds" =~ ^[0-9]+$ ]]; then
  echo "retry-delay-seconds must be a non-negative integer: ${retry_delay_seconds}" >&2
  exit 2
fi

base_url="${MAVEN_CENTRAL_BASE_URL:-https://repo1.maven.org/maven2}"
curl_bin="${CURL_BIN:-curl}"
artifact_name="sihsalus-content-${version}"
artifact_base="${base_url%/}/io/github/proyecto-santaclotilde/sihsalus-content/${version}/${artifact_name}"
artifact_urls=(
  "${artifact_base}.pom"
  "${artifact_base}.zip"
)

for (( attempt = 1; attempt <= max_attempts; attempt++ )); do
  missing_urls=()

  for url in "${artifact_urls[@]}"; do
    if ! "$curl_bin" \
      --fail \
      --silent \
      --show-error \
      --location \
      --head \
      --connect-timeout 10 \
      --max-time 30 \
      "$url" >/dev/null 2>&1; then
      missing_urls+=("$url")
    fi
  done

  if (( ${#missing_urls[@]} == 0 )); then
    echo "Maven Central publication is available: ${artifact_name}.pom and ${artifact_name}.zip"
    exit 0
  fi

  echo "Maven Central publication is not fully available; attempt ${attempt}/${max_attempts}."
  for url in "${missing_urls[@]}"; do
    echo "Missing: ${url}"
  done

  if (( attempt < max_attempts && retry_delay_seconds > 0 )); then
    sleep "$retry_delay_seconds"
  fi
done

echo "::error::Maven Central publication did not become fully available for ${artifact_name}." >&2
exit 1
