#!/usr/bin/env python3
import csv
import sys
from pathlib import Path


CONFIG_DIR = Path("configuration/backend_configuration")
LOCATION_TAGS_PATH = CONFIG_DIR / "locationtags" / "locationtags.csv"
ROLES_CORE_PATH = CONFIG_DIR / "roles" / "roles-core.csv"
MODULE_LOCATION_TAGS = {"Appointment Location", "Queue Location"}
ADMISSION_ROLE_UUID = "71dcb611-756a-4ad3-a9bb-73b6cfe28066"
ADMISSION_REQUIRED_PRIVILEGES = {
    "Add Patients",
    "Edit Patient Identifiers",
    "Edit Patients",
    "Get Concepts",
    "Get Patient Identifiers",
}


def main():
    errors = []
    checked = 0

    for path in sorted(CONFIG_DIR.rglob("*.csv")):
        with path.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.reader(handle))

        if not rows:
            continue

        checked += 1
        header_width = len(rows[0])
        for line_number, row in enumerate(rows[1:], start=2):
            if len(row) != header_width:
                errors.append(
                    f"{path}:{line_number}: expected {header_width} columns, "
                    f"found {len(row)}"
                )

        if path == LOCATION_TAGS_PATH:
            uuid_index = rows[0].index("Uuid")
            name_index = rows[0].index("Name")
            module_tag_rows = {
                name: [
                    row
                    for row in rows[1:]
                    if len(row) > name_index and row[name_index] == name
                ]
                for name in MODULE_LOCATION_TAGS
            }
            for name, matching_rows in sorted(module_tag_rows.items()):
                if len(matching_rows) != 1:
                    errors.append(
                        f"{path}: expected exactly one {name!r} row, found {len(matching_rows)}"
                    )
                elif matching_rows[0][uuid_index]:
                    errors.append(
                        f"{path}: {name!r} must have an empty UUID so Initializer "
                        "resolves the module-created tag by name"
                    )

        if path == ROLES_CORE_PATH:
            uuid_index = rows[0].index("Uuid")
            role_index = rows[0].index("Role name")
            privileges_index = rows[0].index("Privileges")
            admission_rows = [
                row
                for row in rows[1:]
                if len(row) > role_index and row[role_index] == "Admision"
            ]
            if len(admission_rows) != 1:
                errors.append(
                    f"{path}: expected exactly one 'Admision' role, "
                    f"found {len(admission_rows)}"
                )
            else:
                admission_row = admission_rows[0]
                if admission_row[uuid_index] != ADMISSION_ROLE_UUID:
                    errors.append(
                        f"{path}: 'Admision' must keep UUID {ADMISSION_ROLE_UUID}"
                    )
                privileges = {
                    privilege.strip()
                    for privilege in admission_row[privileges_index].split(";")
                    if privilege.strip()
                }
                missing_privileges = ADMISSION_REQUIRED_PRIVILEGES - privileges
                if missing_privileges:
                    errors.append(
                        f"{path}: 'Admision' is missing required privileges: "
                        f"{', '.join(sorted(missing_privileges))}"
                    )

    if errors:
        print("CSV width validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Validated column counts, module-owned location tags, and admission "
        f"role invariants for {checked} CSV files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
