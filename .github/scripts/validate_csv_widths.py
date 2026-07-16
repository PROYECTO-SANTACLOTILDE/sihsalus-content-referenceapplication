#!/usr/bin/env python3
import csv
import sys
from pathlib import Path


CONFIG_DIR = Path("configuration/backend_configuration")
LOCATION_TAGS_PATH = CONFIG_DIR / "locationtags" / "locationtags.csv"
LOCATIONS_PATH = CONFIG_DIR / "locations" / "sihsalus-locations.csv"
ROLES_CORE_PATH = CONFIG_DIR / "roles" / "roles-core.csv"
MODULE_LOCATION_TAGS = {"Appointment Location", "Queue Location"}
HOSPITAL_LOCATION_UUID = "35d2234e-129a-4c40-abb2-1ae0b72c1602"
ADMISSION_ROLE_UUID = "71dcb611-756a-4ad3-a9bb-73b6cfe28066"
ADMISSION_REQUIRED_PRIVILEGES = {
    "Add Patients",
    "Edit Patient Identifiers",
    "Edit Patients",
    "Get Concept Sources",
    "Get Concepts",
    "Get Patient Identifiers",
    "Get Providers",
}


def is_true(value):
    return value.strip().lower() in {"1", "true", "yes"}


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

        if path == LOCATIONS_PATH:
            uuid_index = rows[0].index("Uuid")
            retired_index = rows[0].index("Void/Retire")
            name_index = rows[0].index("Name")
            active_rows = [
                row
                for row in rows[1:]
                if len(row) == header_width and not is_true(row[retired_index])
            ]
            hospital_rows = [
                row for row in active_rows if row[uuid_index] == HOSPITAL_LOCATION_UUID
            ]
            if len(hospital_rows) != 1:
                errors.append(
                    f"{path}: expected exactly one active Hospital Santa Clotilde row "
                    f"with UUID {HOSPITAL_LOCATION_UUID}, found {len(hospital_rows)}"
                )
            else:
                hospital_row = hospital_rows[0]
                if hospital_row[name_index] != "Hospital Santa Clotilde":
                    errors.append(
                        f"{path}: location {HOSPITAL_LOCATION_UUID} must keep the name "
                        "'Hospital Santa Clotilde'"
                    )

                expected_hospital_tags = {
                    "Tag|Login Location": True,
                    "Tag|Visit Location": False,
                    "Tag|Facility Location": True,
                    "Tag|Queue Location": True,
                    "Tag|Admission Location": False,
                    "Tag|Transfer Location": False,
                    "Tag|Appointment Location": False,
                }
                for column, expected in expected_hospital_tags.items():
                    actual = is_true(hospital_row[rows[0].index(column)])
                    if actual != expected:
                        errors.append(
                            f"{path}: Hospital Santa Clotilde must have {column}="
                            f"{'TRUE' if expected else 'FALSE'}"
                        )

            login_index = rows[0].index("Tag|Login Location")
            active_login_rows = [row for row in active_rows if is_true(row[login_index])]
            active_login_uuids = [row[uuid_index] for row in active_login_rows]
            if active_login_uuids != [HOSPITAL_LOCATION_UUID]:
                login_locations = ", ".join(
                    f"{row[name_index]} ({row[uuid_index]})" for row in active_login_rows
                )
                errors.append(
                    f"{path}: Hospital Santa Clotilde must be the only active Login "
                    f"Location; found: {login_locations or 'none'}"
                )

        if path == ROLES_CORE_PATH:
            uuid_index = rows[0].index("Uuid")
            role_index = rows[0].index("Role name")
            privileges_index = rows[0].index("Privileges")
            admission_rows = [
                row
                for row in rows[1:]
                if len(row) > role_index and row[role_index] == "SIHSALUS Admision"
            ]
            if len(admission_rows) != 1:
                errors.append(
                    f"{path}: expected exactly one 'SIHSALUS Admision' role, "
                    f"found {len(admission_rows)}"
                )
            else:
                admission_row = admission_rows[0]
                if admission_row[uuid_index] != ADMISSION_ROLE_UUID:
                    errors.append(
                        f"{path}: 'SIHSALUS Admision' must keep UUID {ADMISSION_ROLE_UUID}"
                    )
                privileges = {
                    privilege.strip()
                    for privilege in admission_row[privileges_index].split(";")
                    if privilege.strip()
                }
                missing_privileges = ADMISSION_REQUIRED_PRIVILEGES - privileges
                if missing_privileges:
                    errors.append(
                        f"{path}: 'SIHSALUS Admision' is missing required privileges: "
                        f"{', '.join(sorted(missing_privileges))}"
                    )

    if errors:
        print("CSV width validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Validated column counts, module-owned location tags, the single hospital "
        f"login location, and admission role invariants for {checked} CSV files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
