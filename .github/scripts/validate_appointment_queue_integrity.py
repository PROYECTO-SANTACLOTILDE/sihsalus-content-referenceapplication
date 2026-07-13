#!/usr/bin/env python3
import csv
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


CONFIG_DIR = Path("configuration/backend_configuration")
PRIVILEGES_PATH = CONFIG_DIR / "privileges" / "privileges_core-demo.csv"
ATTRIBUTE_TYPES_PATH = CONFIG_DIR / "attributetypes" / "attribute_types.csv"
GLOBAL_PROPERTIES_PATH = (
    CONFIG_DIR / "globalproperties" / "globalproperties-sihsalus.xml"
)
SERVICE_DEFINITIONS_PATH = (
    CONFIG_DIR / "appointmentservicedefinitions" / "servicedefinitions.csv"
)
SERVICE_TYPES_PATH = CONFIG_DIR / "appointmentservicetypes" / "servicetypes.csv"
QUEUES_PATH = CONFIG_DIR / "queues" / "sihsalus-queues.csv"
MAPPING_AUDIT_PATH = (
    Path("docs/audits/2026-07-13-appointment-service-queue-mapping.csv")
)

LIFECYCLE_PRIVILEGE_UUID = "ef67b22e-25c8-4d0f-ab6e-427be7f72cc4"
LIFECYCLE_PRIVILEGE = "Manage Appointment Queue Lifecycle"
GENERATE_FUA_PRIVILEGE_UUID = "2293389f-8595-491f-b842-5da867f59608"
GENERATE_FUA_PRIVILEGE = "Generate Fua from Visit"
QUEUE_NUMBER_ATTRIBUTE_UUID = "06a0b8c6-cbdf-4b42-9cbd-871129db8758"

TARGET_ROLES = {
    "71dcb611-756a-4ad3-a9bb-73b6cfe28066": "Admision",
    "75abd7e6-9dcd-446d-8468-04837f314c4f": "Application: Register Appointments",
    "72dd34eb-0295-4684-ab3f-1ccb0cfaab20": "Application: Gestionar Colas Servicio",
    "cf627580-0372-47fc-87b6-319d4a4d4973": "Personal de Emergencia",
}
CLINICAL_ROLE_UUID = "7a4dd4c0-8f45-49f2-91b8-a4349952d07b"
CLINICAL_ROLE_NAME = "Doctor Consulta Externa"
FUA_OPERATOR_ROLE_UUID = "68256ae6-d81c-4ef9-bda9-fc1471022cd3"
FUA_OPERATOR_ROLE_NAME = "Digitadores FUA"
SUPER_ADMIN_ROLE_UUID = "227fa2ff-f7ed-49f8-9fec-3ca63814df9e"
ALLOWED_DIRECT_ASSIGNMENTS = set(TARGET_ROLES) | {
    CLINICAL_ROLE_UUID,
    SUPER_ADMIN_ROLE_UUID,
}
ALLOWED_DIRECT_FUA_GENERATION_ASSIGNMENTS = {
    CLINICAL_ROLE_UUID,
    FUA_OPERATOR_ROLE_UUID,
    SUPER_ADMIN_ROLE_UUID,
}
COMMON_OPERATIONAL_PRIVILEGES = {
    LIFECYCLE_PRIVILEGE,
    "Add Visits",
    "Edit Visits",
    "Get Concepts",
    "Get Locations",
    "Get Queue Entries",
    "Get Queues",
    "Get Visit Attribute Types",
    "Get Visit Types",
    "Get Visits",
    "View Locations",
}
ROLE_REQUIRED_PRIVILEGES = {
    "71dcb611-756a-4ad3-a9bb-73b6cfe28066": {"app:home.citas.editar"},
    "75abd7e6-9dcd-446d-8468-04837f314c4f": {"app:home.citas.editar"},
    "72dd34eb-0295-4684-ab3f-1ccb0cfaab20": {
        "Manage Queue Entries",
        "View Appointments",
        "app:home.colasAtencion",
        "app:home.colasAtencion.editar",
    },
    "cf627580-0372-47fc-87b6-319d4a4d4973": {
        "Add Encounters",
        "Add Observations",
        "Add Patient Identifiers",
        "Add Patients",
        "Add People",
        "Edit Encounters",
        "Edit Observations",
        "Form Entry",
        "Get Encounter Types",
        "Get Encounters",
        "Get Forms",
        "Get Identifier Types",
        "Get Observations",
        "Get Patient Identifiers",
        "Get Patients",
        "Get People",
        "Manage Queue Entries",
        "View Encounters",
        "View Forms",
        "View Identifier Types",
        "View Observations",
        "View Patient Identifiers",
        "View Patients",
        "View People",
        "app:home.emergencia",
        "app:home.emergencia.editar",
        "app:opciones.registrarPaciente",
    },
}
ROLE_FORBIDDEN_PRIVILEGES = {
    "71dcb611-756a-4ad3-a9bb-73b6cfe28066": {
        "Get Global Properties",
        "Manage Queue Rooms",
        "Manage Queue Entries",
        "Manage Queues",
        "Purge Queue Entries",
        "Purge Queue Rooms",
        "Reset Appointment Status",
        "View Global Properties",
        "app:home.colasAtencion",
        "app:home.colasAtencion.editar",
    },
    "75abd7e6-9dcd-446d-8468-04837f314c4f": {
        "Get Global Properties",
        "Manage Queue Rooms",
        "Manage Queue Entries",
        "Manage Queues",
        "Purge Queue Entries",
        "Purge Queue Rooms",
        "Reset Appointment Status",
        "View Global Properties",
        "app:home.colasAtencion",
        "app:home.colasAtencion.editar",
    },
    "72dd34eb-0295-4684-ab3f-1ccb0cfaab20": {
        "Get Global Properties",
        "Manage Appointments",
        "Manage Own Appointments",
        "Purge Queue Entries",
        "Purge Queue Rooms",
        "Reset Appointment Status",
        "View Global Properties",
    },
    "cf627580-0372-47fc-87b6-319d4a4d4973": {
        "Delete Encounters",
        "Delete Observations",
        "Delete Patients",
        "Delete Visits",
        "Get Global Properties",
        "Manage Appointment Services",
        "Manage Appointment Specialities",
        "Manage Appointments",
        "Manage Global Properties",
        "Manage Queue Rooms",
        "Manage Queues",
        "Purge Queue Entries",
        "Purge Queue Rooms",
        "Reset Appointment Status",
        "View Global Properties",
    },
}


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def is_retired(value):
    return value.strip().lower() in {"1", "true", "yes"}


def split_privileges(value):
    return {part.strip() for part in value.split(";") if part.strip()}


def validate_privilege_and_roles(errors):
    privilege_rows = read_csv(PRIVILEGES_PATH)
    matching_uuid = [
        row for row in privilege_rows if row["Uuid"] == LIFECYCLE_PRIVILEGE_UUID
    ]
    matching_name = [
        row for row in privilege_rows if row["Privilege name"] == LIFECYCLE_PRIVILEGE
    ]
    if len(matching_uuid) != 1 or len(matching_name) != 1:
        errors.append(
            f"{PRIVILEGES_PATH}: lifecycle privilege must have one UUID and one name row"
        )
    elif matching_uuid[0] is not matching_name[0]:
        errors.append(
            f"{PRIVILEGES_PATH}: {LIFECYCLE_PRIVILEGE!r} must use UUID "
            f"{LIFECYCLE_PRIVILEGE_UUID}"
        )

    matching_fua_uuid = [
        row for row in privilege_rows if row["Uuid"] == GENERATE_FUA_PRIVILEGE_UUID
    ]
    matching_fua_name = [
        row for row in privilege_rows if row["Privilege name"] == GENERATE_FUA_PRIVILEGE
    ]
    if len(matching_fua_uuid) != 1 or len(matching_fua_name) != 1:
        errors.append(
            f"{PRIVILEGES_PATH}: FUA generation privilege must have one UUID and one name row"
        )
    elif matching_fua_uuid[0] is not matching_fua_name[0]:
        errors.append(
            f"{PRIVILEGES_PATH}: {GENERATE_FUA_PRIVILEGE!r} must use UUID "
            f"{GENERATE_FUA_PRIVILEGE_UUID}"
        )

    role_rows = []
    for path in sorted((CONFIG_DIR / "roles").glob("*.csv")):
        for row in read_csv(path):
            row["_path"] = str(path)
            role_rows.append(row)

    direct_assignments = {
        row["Uuid"]
        for row in role_rows
        if LIFECYCLE_PRIVILEGE in split_privileges(row.get("Privileges", ""))
    }
    if direct_assignments != ALLOWED_DIRECT_ASSIGNMENTS:
        errors.append(
            "lifecycle privilege direct assignments must match the approved "
            "admission, appointment, queue, emergency, clinical, and backend-admin roles; "
            "found UUIDs: "
            + ", ".join(sorted(direct_assignments))
        )

    direct_fua_generation_assignments = {
        row["Uuid"]
        for row in role_rows
        if GENERATE_FUA_PRIVILEGE in split_privileges(row.get("Privileges", ""))
    }
    if direct_fua_generation_assignments != ALLOWED_DIRECT_FUA_GENERATION_ASSIGNMENTS:
        errors.append(
            "FUA generation privilege direct assignments must match the approved clinical "
            "and backend-admin roles; found UUIDs: "
            + ", ".join(sorted(direct_fua_generation_assignments))
        )

    for role_uuid, expected_name in TARGET_ROLES.items():
        matching_roles = [row for row in role_rows if row["Uuid"] == role_uuid]
        if len(matching_roles) != 1:
            errors.append(
                f"roles: expected exactly one {expected_name!r} row with UUID {role_uuid}"
            )
            continue

        row = matching_roles[0]
        if row["Role name"] != expected_name:
            errors.append(
                f"{row['_path']}: role UUID {role_uuid} must be named {expected_name!r}"
            )
        privileges = split_privileges(row["Privileges"])
        required = COMMON_OPERATIONAL_PRIVILEGES | ROLE_REQUIRED_PRIVILEGES[role_uuid]
        missing = required - privileges
        forbidden = ROLE_FORBIDDEN_PRIVILEGES[role_uuid] & privileges
        if missing:
            errors.append(
                f"{row['_path']}: {expected_name!r} is missing lifecycle privileges: "
                + ", ".join(sorted(missing))
            )
        if forbidden:
            errors.append(
                f"{row['_path']}: {expected_name!r} has forbidden administrative privileges: "
                + ", ".join(sorted(forbidden))
            )

    clinical_matches = [row for row in role_rows if row["Uuid"] == CLINICAL_ROLE_UUID]
    if len(clinical_matches) != 1:
        errors.append(
            f"roles: expected exactly one {CLINICAL_ROLE_NAME!r} row with UUID "
            f"{CLINICAL_ROLE_UUID}"
        )
    else:
        clinical = clinical_matches[0]
        privileges = split_privileges(clinical["Privileges"])
        required = {
            GENERATE_FUA_PRIVILEGE,
            LIFECYCLE_PRIVILEGE,
            "Edit Visits",
            "Get Queue Entries",
            "Get Queues",
            "Get Visits",
            "Manage Appointments",
            "Read Fua",
            "app:hoja.clinica.citas.editar",
        }
        forbidden = {
            "Get Global Properties",
            "Manage Fua",
            "Manage Queue Entries",
            "Manage Queues",
            "Purge Queue Entries",
            "Update Fua",
            "View Global Properties",
        }
        if required - privileges:
            errors.append(
                f"{clinical['_path']}: {CLINICAL_ROLE_NAME!r} is missing lifecycle "
                "privileges: " + ", ".join(sorted(required - privileges))
            )
        if forbidden & privileges:
            errors.append(
                f"{clinical['_path']}: {CLINICAL_ROLE_NAME!r} has forbidden queue "
                "administration privileges: "
                + ", ".join(sorted(forbidden & privileges))
            )

    fua_operator_matches = [
        row for row in role_rows if row["Uuid"] == FUA_OPERATOR_ROLE_UUID
    ]
    if len(fua_operator_matches) != 1:
        errors.append(
            f"roles: expected exactly one {FUA_OPERATOR_ROLE_NAME!r} row with UUID "
            f"{FUA_OPERATOR_ROLE_UUID}"
        )
    else:
        fua_operator = fua_operator_matches[0]
        privileges = split_privileges(fua_operator["Privileges"])
        required = {
            GENERATE_FUA_PRIVILEGE,
            "Fua Privilege",
            "Get Visits",
            "Manage Fua",
            "Read Fua",
            "Update Fua",
            "app:home",
            "app:home.fua",
            "app:home.fua.editar",
        }
        forbidden = {
            "Delete Fua",
            "Delete Visits",
            "Get Global Properties",
            "Manage Global Properties",
            "View Global Properties",
        }
        if required - privileges:
            errors.append(
                f"{fua_operator['_path']}: {FUA_OPERATOR_ROLE_NAME!r} is missing FUA "
                "workflow privileges: " + ", ".join(sorted(required - privileges))
            )
        if forbidden & privileges:
            errors.append(
                f"{fua_operator['_path']}: {FUA_OPERATOR_ROLE_NAME!r} has forbidden "
                "administrative privileges: "
                + ", ".join(sorted(forbidden & privileges))
            )


def validate_queue_number_metadata(errors):
    rows = read_csv(ATTRIBUTE_TYPES_PATH)
    matches = [row for row in rows if row["Uuid"] == QUEUE_NUMBER_ATTRIBUTE_UUID]
    if len(matches) != 1:
        errors.append(
            f"{ATTRIBUTE_TYPES_PATH}: expected one queue-number visit attribute row"
        )
    else:
        row = matches[0]
        expected = {
            "Void/Retire": "",
            "Entity name": "Visit",
            "Name": "N\u00famero de turno de cola",
            "Min occurs": "0",
            "Max occurs": "1",
            "Datatype classname": "org.openmrs.customdatatype.datatype.FreeTextDatatype",
        }
        for column, value in expected.items():
            if row[column] != value:
                errors.append(
                    f"{ATTRIBUTE_TYPES_PATH}: queue-number attribute {column!r} must be "
                    f"{value!r}, found {row[column]!r}"
                )

    root = ET.parse(GLOBAL_PROPERTIES_PATH).getroot()
    properties = defaultdict(list)
    for item in root.findall(".//globalProperty"):
        property_element = item.find("property")
        value_element = item.find("value")
        if property_element is None:
            continue
        properties[(property_element.text or "").strip()].append(
            (value_element.text or "").strip() if value_element is not None else ""
        )

    expected_properties = {
        "sihsalus.queue.visitQueueNumberAttributeUuid": QUEUE_NUMBER_ATTRIBUTE_UUID,
        "sihsalus.timezone": "America/Lima",
    }
    for name, expected_value in expected_properties.items():
        values = properties.get(name, [])
        if values != [expected_value]:
            errors.append(
                f"{GLOBAL_PROPERTIES_PATH}: {name!r} must occur once with value "
                f"{expected_value!r}; found {values!r}"
            )


def validate_service_durations(errors):
    definitions = {
        row["Uuid"]: row
        for row in read_csv(SERVICE_DEFINITIONS_PATH)
        if not is_retired(row["Void/Retire"])
    }
    types_by_definition = defaultdict(list)
    for row in read_csv(SERVICE_TYPES_PATH):
        if is_retired(row["Void/Retire"]):
            continue
        definition_uuid = row["Service Definition"]
        if definition_uuid not in definitions:
            errors.append(
                f"{SERVICE_TYPES_PATH}: active service type {row['Name']!r} references "
                f"unknown or retired definition {definition_uuid}"
            )
            continue
        types_by_definition[definition_uuid].append(row)

    aligned = 0
    for definition_uuid, definition in definitions.items():
        service_types = types_by_definition.get(definition_uuid, [])
        if len(service_types) == 1:
            service_type = service_types[0]
            if definition["Duration"] != service_type["Duration"]:
                errors.append(
                    f"{SERVICE_DEFINITIONS_PATH}: {definition['Name']!r} duration must "
                    f"match its only active type ({service_type['Duration']} minutes)"
                )
            try:
                if int(service_type["Duration"]) <= 0:
                    raise ValueError
            except ValueError:
                errors.append(
                    f"{SERVICE_TYPES_PATH}: {service_type['Name']!r} must have a "
                    "positive whole-minute duration"
                )
            aligned += 1
        elif len(service_types) > 1 and definition["Duration"]:
            errors.append(
                f"{SERVICE_DEFINITIONS_PATH}: {definition['Name']!r} has multiple active "
                "types, so its base duration must remain empty until a local rule is defined"
            )
    return aligned


def validate_documented_queue_mapping(errors):
    definitions = {
        row["Uuid"]: row
        for row in read_csv(SERVICE_DEFINITIONS_PATH)
        if not is_retired(row["Void/Retire"])
    }
    queues = {
        row["Uuid"]: row
        for row in read_csv(QUEUES_PATH)
        if not is_retired(row["Void/Retire"])
    }
    audit_rows = read_csv(MAPPING_AUDIT_PATH)
    rows_by_service = defaultdict(list)
    for row in audit_rows:
        rows_by_service[row["Appointment Service Uuid"]].append(row)

    undocumented = set(definitions) - set(rows_by_service)
    extra = set(rows_by_service) - set(definitions)
    if undocumented:
        errors.append(
            f"{MAPPING_AUDIT_PATH}: active appointment services are undocumented: "
            + ", ".join(sorted(undocumented))
        )
    if extra:
        errors.append(
            f"{MAPPING_AUDIT_PATH}: retired or unknown appointment services are listed: "
            + ", ".join(sorted(extra))
        )

    automatic_pairs = set()
    manual_count = 0
    for service_uuid, rows in rows_by_service.items():
        if len(rows) != 1 or service_uuid not in definitions:
            if len(rows) != 1:
                errors.append(
                    f"{MAPPING_AUDIT_PATH}: service {service_uuid} must have exactly one row"
                )
            continue
        row = rows[0]
        definition = definitions[service_uuid]
        if row["Appointment Service"] != definition["Name"]:
            errors.append(
                f"{MAPPING_AUDIT_PATH}: service name for {service_uuid} is stale"
            )
        if row["Location Uuid"] != definition["Location"]:
            errors.append(
                f"{MAPPING_AUDIT_PATH}: location for {definition['Name']!r} is stale"
            )
        if not row["Reason"].strip():
            errors.append(
                f"{MAPPING_AUDIT_PATH}: {definition['Name']!r} must document a reason"
            )

        resolution = row["Resolution"]
        queue_uuid = row["Queue Uuid"]
        queue = queues.get(queue_uuid) if queue_uuid else None
        if resolution == "automatic":
            if queue is None:
                errors.append(
                    f"{MAPPING_AUDIT_PATH}: automatic mapping for {definition['Name']!r} "
                    "must reference an active queue"
                )
                continue
            exact_matches = [
                candidate
                for candidate in queues.values()
                if candidate["Service"] == service_uuid
                and candidate["Location"] == definition["Location"]
            ]
            if len(exact_matches) != 1 or exact_matches[0]["Uuid"] != queue_uuid:
                errors.append(
                    f"{MAPPING_AUDIT_PATH}: automatic mapping for {definition['Name']!r} "
                    "must be the unique queue with the same service UUID and location"
                )
            if row["Queue"] != queue["Name"]:
                errors.append(
                    f"{MAPPING_AUDIT_PATH}: queue name for {queue_uuid} is stale"
                )
            automatic_pairs.add((service_uuid, queue_uuid))
        elif resolution == "manual-required":
            manual_count += 1
            if queue_uuid and queue is None:
                errors.append(
                    f"{MAPPING_AUDIT_PATH}: manual candidate {queue_uuid} for "
                    f"{definition['Name']!r} is not an active queue"
                )
            if queue and row["Queue"] != queue["Name"]:
                errors.append(
                    f"{MAPPING_AUDIT_PATH}: manual candidate queue name for {queue_uuid} "
                    "is stale"
                )
            if queue and queue["Service"] == service_uuid and queue["Location"] == definition["Location"]:
                errors.append(
                    f"{MAPPING_AUDIT_PATH}: {definition['Name']!r} now has an exact queue "
                    "mapping and must be reviewed as automatic"
                )
        else:
            errors.append(
                f"{MAPPING_AUDIT_PATH}: unsupported resolution {resolution!r} for "
                f"{definition['Name']!r}"
            )

    configured_exact_pairs = {
        (definition_uuid, queue["Uuid"])
        for definition_uuid, definition in definitions.items()
        for queue in queues.values()
        if queue["Service"] == definition_uuid
        and queue["Location"] == definition["Location"]
    }
    if automatic_pairs != configured_exact_pairs:
        errors.append(
            f"{MAPPING_AUDIT_PATH}: documented automatic mappings do not match the "
            "configured service-and-location pairs"
        )
    if not automatic_pairs or not manual_count:
        errors.append(
            f"{MAPPING_AUDIT_PATH}: mapping must remain explicit about both automatic "
            "and manual-required services"
        )
    return len(automatic_pairs), manual_count


def main():
    errors = []
    validate_privilege_and_roles(errors)
    validate_queue_number_metadata(errors)
    aligned_durations = validate_service_durations(errors)
    automatic_mappings, manual_mappings = validate_documented_queue_mapping(errors)

    if errors:
        print("Appointment/visit/queue integrity validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"Validated {len(TARGET_ROLES) + 1} least-privilege lifecycle workflow roles, "
        f"{len(ALLOWED_DIRECT_FUA_GENERATION_ASSIGNMENTS)} narrow FUA generation assignments, "
        "queue-number metadata, "
        f"{aligned_durations} unambiguous durations, {automatic_mappings} automatic "
        f"queue mappings, and {manual_mappings} manual mappings."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
