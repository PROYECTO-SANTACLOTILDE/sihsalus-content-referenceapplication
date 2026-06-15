#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


FORM_DIR = Path("configuration/backend_configuration/ampathforms")
REQUIRED_TOP_LEVEL = {
    "name",
    "version",
    "published",
    "retired",
    "encounter",
    "processor",
    "referencedForms",
    "pages",
}
ID_RE = re.compile(r"^[a-z][A-Za-z0-9]*$")


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def validate_form(path):
    errors = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON: {exc}"]

    missing = sorted(REQUIRED_TOP_LEVEL - data.keys())
    if missing:
        errors.append(f"{path}: missing top-level keys: {', '.join(missing)}")

    ids = set()
    for node in walk(data):
        node_id = node.get("id")
        if node_id is not None:
            if not isinstance(node_id, str) or not ID_RE.fullmatch(node_id):
                errors.append(f"{path}: invalid question id: {node_id!r}")
            elif node_id in ids:
                errors.append(f"{path}: duplicate question id: {node_id}")
            else:
                ids.add(node_id)

        node_type = node.get("type")
        if node_type in {"obs", "obsGroup"}:
            options = node.get("questionOptions")
            if not isinstance(options, dict) or not options.get("concept"):
                errors.append(
                    f"{path}: {node_type} {node_id!r} is missing questionOptions.concept"
                )

        options = node.get("questionOptions")
        if isinstance(options, dict):
            for answer in options.get("answers") or []:
                if isinstance(answer, dict) and not answer.get("concept"):
                    errors.append(
                        f"{path}: question {node_id!r} has answer without concept: "
                        f"{answer.get('label')!r}"
                    )

    return errors


def main():
    paths = sorted(FORM_DIR.glob("*.json"))
    errors = []
    for path in paths:
        errors.extend(validate_form(path))

    if errors:
        print("AMPATH form validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(paths)} AMPATH form JSON files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
