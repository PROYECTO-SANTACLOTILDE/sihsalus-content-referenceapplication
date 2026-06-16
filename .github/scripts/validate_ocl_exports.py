#!/usr/bin/env python3
import json
import sys
import zipfile
from collections import defaultdict
from pathlib import Path


OCL_DIR = Path("configuration/backend_configuration/ocl")


def main():
    errors = []
    checked = 0

    for zip_path in sorted(OCL_DIR.glob("*.zip")):
        with zipfile.ZipFile(zip_path) as archive:
            try:
                export = json.loads(archive.read("export.json"))
            except KeyError:
                errors.append(f"{zip_path}: missing export.json")
                continue

        for concept in export.get("concepts", []):
            checked += 1
            names_by_external_id = defaultdict(list)

            for name in concept.get("names", []):
                if name.get("retired"):
                    continue

                external_id = (name.get("external_id") or "").strip()
                if external_id:
                    names_by_external_id[external_id].append(name)

            for external_id, names in names_by_external_id.items():
                if len(names) < 2:
                    continue

                concept_identifier = concept.get("external_id") or concept.get("id") or concept.get("uuid")
                rendered_names = ", ".join(
                    f"{name.get('locale')}:{name.get('name')} ({name.get('name_type')})" for name in names
                )
                errors.append(
                    f"{zip_path}: concept {concept_identifier} has duplicated active concept-name "
                    f"external_id {external_id}: {rendered_names}"
                )

    if errors:
        print("OCL export validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated concept-name external IDs for {checked} OCL concepts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
