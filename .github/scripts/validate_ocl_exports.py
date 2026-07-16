#!/usr/bin/env python3
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


OCL_DIR = Path("configuration/backend_configuration/ocl")
FORM_DIR = Path("configuration/backend_configuration/ampathforms")
GLOBAL_PROPERTIES_PATH = Path(
    "configuration/backend_configuration/globalproperties/globalproperties-sihsalus.xml"
)
EXPECTED_SIHSALUS_SUBSCRIPTION_URL = (
    "https://api.openconceptlab.org/orgs/SIHSALUS/sources/sihsalus/2026-07-16-01"
)
OCCUPATIONS_SOURCE = "ocupaciones"
OCCUPATIONS_ROOT_URL = "/orgs/SIHSALUS/sources/ocupaciones/concepts/1/"
OCCUPATIONS_CONCEPT_URL_PREFIX = "/orgs/SIHSALUS/sources/ocupaciones/concepts/"
EXPECTED_OCCUPATION_UNIT_GROUPS = 436
SIHSALUS_SOURCE = "sihsalus"
TPED_ROOT_ID = "3798"
TPED_LINES = {
    "90": ("A", ["91", "92", "93", "94", "95"]),
    "96": ("B", ["97", "98", "99"]),
    "100": ("C", ["101", "103", "105", "106", "107", "108"]),
    "109": ("D", [str(concept_id) for concept_id in range(130, 141)]),
    "141": ("E", ["142", "143", "144"]),
    "145": ("F", ["146", "147", "148"]),
    "149": ("G", [str(concept_id) for concept_id in range(150, 159)]),
    "159": ("H", [str(concept_id) for concept_id in range(160, 168)]),
    "168": ("I", [str(concept_id) for concept_id in range(169, 180)]),
    "180": ("J", [str(concept_id) for concept_id in range(181, 190)]),
    "190": ("K", [str(concept_id) for concept_id in range(191, 201)]),
    "201": ("L", [str(concept_id) for concept_id in range(202, 213)]),
}
INSTRUMENT_SETS = {
    TPED_ROOT_ID: {
        *TPED_LINES,
        "3791",
        "1036",
    },
    "1070": {
        "3774",
        "1028",
        "1030",
        "1029",
        "1035",
        "1031",
        "1032",
        "1033",
        "1034",
        "1036",
        "1037",
        "1042",
        "1038",
        "1043",
        "1039",
        "1044",
        "1040",
        "1045",
        "1041",
        "1046",
        "1047",
        "1048",
        "1049",
        "1050",
        "1051",
        "1052",
        "1053",
        "1054",
        "1055",
    },
    "1071": {
        "1069",
        "1056",
        "1031",
        "1032",
        "1033",
        "1034",
        "1057",
        "1058",
        "1059",
        "1060",
        "1061",
        "1062",
        "1063",
        "1064",
        "1065",
        "1066",
        "1067",
        "1068",
        "1050",
        "1053",
        "1054",
        "1055",
    },
    "4167": {"4443", "4143", "4144"},
    "4168": {"4148", "4447", "4149", "4144"},
}
INSTRUMENT_NAMES = {
    "3798": "Test Peruano de Evaluación del Desarrollo del Niño (TPED)",
    "1070": "Test de Vigilancia del Neurodesarrollo (Huanca Test)",
    "1071": "Lista de Habilidades y Conductas Esperadas por Edad",
    "4167": "Prueba de Evaluación del Desarrollo Infantil (EDI)",
    "4168": "M-CHAT-R/F versión peruana",
}
CODED_RESULT_SETS = {
    "4443": ["4444", "4445", "4446"],
    "4447": ["4448", "4449", "4450"],
}
PROCEDURE_STATUS_ID = "4451"
PROCEDURE_STATUS_EXTERNAL_ID = "f0d47b45-8303-4cdc-a9f2-c37135a3700f"
PROCEDURE_STATUS_ANSWERS = [
    ("4452", "167153AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "Preparación"),
    ("4453", "163723AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "En progreso"),
    ("4454", "1118AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "No realizado"),
    ("4455", "167154AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "En espera"),
    ("4456", "167155AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "Discontinuado"),
    ("4457", "1267AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "Completado"),
    ("4458", "162983AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "Registrado por error"),
    ("4459", "1067AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "Desconocido (procedimiento)"),
]
DURATION_UNITS_ID = "612"
DURATION_UNITS_EXTERNAL_ID = "1732AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
DURATION_UNIT_MEMBERS = [
    ("615", "162583AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "Segundos"),
    ("609", "1733AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "Minuto"),
    ("603", "1822AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "Horas"),
    ("610", "1072AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "Días"),
    ("611", "1073AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "Semanas"),
    ("613", "1074AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "Meses"),
    ("608", "1734AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "Años"),
    ("614", "162582AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "Cantidad de veces"),
]


def main():
    errors = []
    checked = 0
    occupation_unit_ids = set()
    occupation_mapping_targets = []
    concepts_by_source = defaultdict(dict)
    mappings_by_source = defaultdict(list)
    concepts_by_url = {}
    concept_records = []
    mapping_records = []

    for zip_path in sorted(OCL_DIR.glob("*.zip")):
        with zipfile.ZipFile(zip_path) as archive:
            try:
                export = json.loads(archive.read("export.json"))
            except KeyError:
                errors.append(f"{zip_path}: missing export.json")
                continue

        source = export.get("source") or {}
        source_id = source.get("id") if isinstance(source, dict) else export.get("short_code")

        for concept in export.get("concepts", []):
            concept_id = concept.get("id")
            if source_id and concept_id:
                concepts_by_source[source_id][concept_id] = concept
            concept_records.append((zip_path, source_id, concept))

            concept_url = normalize_ocl_url(concept.get("url"))
            if concept_url:
                existing = concepts_by_url.get(concept_url)
                if existing and existing[2].get("external_id") != concept.get("external_id"):
                    errors.append(
                        f"{zip_path}: concept URL {concept_url} is duplicated by "
                        f"{existing[0]} and {concept.get('external_id') or concept_id}"
                    )
                else:
                    concepts_by_url[concept_url] = (zip_path, source_id, concept)

        if source_id:
            mappings_by_source[source_id].extend(export.get("mappings", []))
            mapping_records.extend(
                (zip_path, source_id, mapping) for mapping in export.get("mappings", [])
            )

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

            if source_id != OCCUPATIONS_SOURCE or concept.get("retired"):
                continue
            if (concept.get("extras") or {}).get("level") != "unit_group":
                continue

            concept_id = concept.get("id") or ""
            if not re.fullmatch(r"\d{4}", concept_id):
                errors.append(f"{zip_path}: occupation unit group has invalid id {concept_id!r}")
                continue

            occupation_unit_ids.add(concept_id)
            active_names = [name for name in concept.get("names", []) if not name.get("retired")]
            preferred_es = [
                name for name in active_names if name.get("locale") == "es" and name.get("locale_preferred")
            ]
            preferred_en = [
                name for name in active_names if name.get("locale") == "en" and name.get("locale_preferred")
            ]
            short_es = [
                name
                for name in active_names
                if name.get("locale") == "es"
                and name.get("name_type") == "Short"
                and name.get("name") == concept_id
            ]

            if len(preferred_es) != 1:
                errors.append(
                    f"{zip_path}: occupation {concept_id} must have exactly one preferred Spanish name"
                )
            if len(preferred_en) != 1:
                errors.append(
                    f"{zip_path}: occupation {concept_id} must have exactly one preferred English name"
                )
            if len(short_es) != 1:
                errors.append(f"{zip_path}: occupation {concept_id} must have its code as a Spanish Short name")

            if preferred_es:
                spanish_name = preferred_es[0].get("name") or ""
                if spanish_name.startswith(f"CIUO-08 {concept_id} -"):
                    errors.append(
                        f"{zip_path}: occupation {concept_id} still has the generated untranslated Spanish label"
                    )
                if preferred_en and concept_id != "3434" and spanish_name == preferred_en[0].get("name"):
                    errors.append(
                        f"{zip_path}: occupation {concept_id} has the same preferred name in Spanish and English"
                    )

            extras = concept.get("extras") or {}
            for field in ("major_label_es", "sub_major_label_es", "minor_label_es"):
                if not extras.get(field):
                    errors.append(f"{zip_path}: occupation {concept_id} is missing {field}")

        if source_id == OCCUPATIONS_SOURCE:
            for mapping in export.get("mappings", []):
                if mapping.get("retired") or mapping.get("map_type") != "CONCEPT-SET":
                    continue
                if mapping.get("from_concept_url") != OCCUPATIONS_ROOT_URL:
                    continue
                target_url = mapping.get("to_concept_url") or ""
                if not target_url.startswith(OCCUPATIONS_CONCEPT_URL_PREFIX):
                    continue
                target_id = target_url.removeprefix(OCCUPATIONS_CONCEPT_URL_PREFIX).rstrip("/")
                if re.fullmatch(r"\d{4}", target_id):
                    occupation_mapping_targets.append(target_id)

    if len(occupation_unit_ids) != EXPECTED_OCCUPATION_UNIT_GROUPS:
        errors.append(
            "occupation terminology must contain "
            f"{EXPECTED_OCCUPATION_UNIT_GROUPS} active CIUO-08 unit groups; found {len(occupation_unit_ids)}"
        )

    if len(occupation_mapping_targets) != EXPECTED_OCCUPATION_UNIT_GROUPS:
        errors.append(
            "occupation root must have exactly "
            f"{EXPECTED_OCCUPATION_UNIT_GROUPS} active unit-group mappings; "
            f"found {len(occupation_mapping_targets)}"
        )
    elif set(occupation_mapping_targets) != occupation_unit_ids:
        missing = sorted(occupation_unit_ids - set(occupation_mapping_targets))
        unexpected = sorted(set(occupation_mapping_targets) - occupation_unit_ids)
        errors.append(f"occupation mapping coverage mismatch: missing={missing}, unexpected={unexpected}")

    validate_mapping_integrity(concepts_by_url, mapping_records, errors)
    validate_default_name_collision_safety(concept_records, errors)

    validate_development_instruments(
        concepts_by_source[SIHSALUS_SOURCE], mappings_by_source[SIHSALUS_SOURCE], errors
    )
    validate_procedure_terminology(
        concepts_by_source[SIHSALUS_SOURCE], mappings_by_source[SIHSALUS_SOURCE], errors
    )
    validate_ocl_global_properties(errors)

    if errors:
        print("OCL export validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {checked} OCL concepts and {len(mapping_records)} mapping endpoints.")
    return 0


def normalize_ocl_url(url):
    if not isinstance(url, str) or not url.strip():
        return None
    return url.strip().rstrip("/") + "/"


def validate_mapping_integrity(concepts_by_url, mapping_records, errors):
    internal_map_types = {"Q-AND-A", "CONCEPT-SET"}

    for zip_path, source_id, mapping in mapping_records:
        mapping_identifier = mapping.get("url") or mapping.get("external_id") or mapping.get("id")
        prefix = f"{zip_path}: mapping {mapping_identifier}"

        from_url = normalize_ocl_url(mapping.get("from_concept_url"))
        if not from_url:
            errors.append(f"{prefix} has no from_concept_url")
        elif from_url not in concepts_by_url:
            errors.append(f"{prefix} references unbundled origin concept {from_url}")

        if mapping.get("map_type") in internal_map_types:
            to_url = normalize_ocl_url(mapping.get("to_concept_url"))
            if not to_url:
                errors.append(
                    f"{prefix} ({mapping.get('map_type')}) has no to_concept_url"
                )
            elif to_url not in concepts_by_url:
                errors.append(f"{prefix} references unbundled target concept {to_url}")
            continue

        target_source_name = mapping.get("to_source_name") or mapping.get(
            "to_source_name_resolved"
        )
        if not target_source_name:
            errors.append(f"{prefix} has no target source name")
        if not normalize_ocl_url(mapping.get("to_source_url")):
            errors.append(f"{prefix} has no to_source_url")
        if not str(mapping.get("to_concept_code") or "").strip():
            errors.append(f"{prefix} has no to_concept_code")


def normalize_name_type(name_type):
    return re.sub(r"[-_]+", " ", str(name_type or "").strip().casefold())


def normalize_concept_name(name):
    return " ".join(str(name or "").strip().casefold().split())


def validate_default_name_collision_safety(concept_records, errors):
    default_names = defaultdict(list)

    for zip_path, source_id, concept in concept_records:
        if concept.get("retired"):
            continue

        active_names = [name for name in concept.get("names", []) if not name.get("retired")]
        for name in active_names:
            if normalize_name_type(name.get("name_type")) == "index term":
                continue
            if not (
                name.get("locale_preferred")
                or normalize_name_type(name.get("name_type")) == "fully specified"
            ):
                continue

            key = (name.get("locale"), normalize_concept_name(name.get("name")))
            default_names[key].append(
                (zip_path, source_id, concept, active_names, name)
            )

    for key, matches in default_names.items():
        concept_uuids = {
            concept.get("external_id") or f"{source_id}:{concept.get('id')}"
            for _, source_id, concept, _, _ in matches
        }
        if len(concept_uuids) < 2:
            continue

        for zip_path, source_id, concept, active_names, name in matches:
            alternatives = [
                candidate
                for candidate in active_names
                if normalize_name_type(candidate.get("name_type")) != "index term"
                and (
                    candidate.get("locale"),
                    normalize_concept_name(candidate.get("name")),
                )
                != key
            ]
            if alternatives:
                continue

            rendered_matches = ", ".join(
                f"{other_source}:{other_concept.get('id')} "
                f"({other_name.get('name')!r})"
                for _, other_source, other_concept, _, other_name in matches
            )
            errors.append(
                f"{zip_path}: active concept {source_id}:{concept.get('id')} has no safe "
                f"fully-specified-name fallback for case-insensitive default-name collision "
                f"{name.get('name')!r}; matches: {rendered_matches}"
            )


def validate_development_instruments(concepts, mappings, errors):
    active_mappings = [mapping for mapping in mappings if not mapping.get("retired")]

    def targets(from_id, map_type):
        matching = [
            mapping
            for mapping in active_mappings
            if mapping.get("from_concept_code") == from_id and mapping.get("map_type") == map_type
        ]
        if matching and all(mapping.get("sort_weight") is not None for mapping in matching):
            matching.sort(key=lambda mapping: float(mapping["sort_weight"]))
        return [mapping.get("to_concept_code") for mapping in matching]

    for concept_id, expected_name in INSTRUMENT_NAMES.items():
        concept = concepts.get(concept_id)
        if not concept:
            errors.append(f"sihsalus: missing development instrument concept {concept_id}")
            continue
        if concept.get("concept_class") != "ConvSet" or concept.get("datatype") != "N/A":
            errors.append(
                f"sihsalus: instrument {concept_id} must be ConvSet/N/A; "
                f"found {concept.get('concept_class')}/{concept.get('datatype')}"
            )
        if concept.get("display_name") != expected_name:
            errors.append(
                f"sihsalus: instrument {concept_id} must display as {expected_name!r}; "
                f"found {concept.get('display_name')!r}"
            )

    tped_answer_ids = set()
    for line_id, (line_code, expected_targets) in TPED_LINES.items():
        line = concepts.get(line_id)
        if not line:
            errors.append(f"sihsalus: missing TPED line {line_code} ({line_id})")
            continue
        if line.get("concept_class") != "Question" or line.get("datatype") != "Coded":
            errors.append(
                f"sihsalus: TPED line {line_code} ({line_id}) must be Question/Coded"
            )
        if (line.get("extras") or {}).get("tped_line") != line_code:
            errors.append(f"sihsalus: TPED line {line_code} ({line_id}) has invalid metadata")

        actual_targets = targets(line_id, "Q-AND-A")
        if actual_targets != expected_targets:
            errors.append(
                f"sihsalus: TPED line {line_code} mappings mismatch: "
                f"expected={expected_targets}, actual={actual_targets}"
            )

        for order, target_id in enumerate(expected_targets, start=1):
            tped_answer_ids.add(target_id)
            target = concepts.get(target_id)
            extras = (target or {}).get("extras") or {}
            if not target or target.get("concept_class") != "Misc" or target.get("datatype") != "N/A":
                errors.append(f"sihsalus: TPED milestone {target_id} must be Misc/N/A")
            if extras.get("tped_line") != line_code or extras.get("tped_order") != order:
                errors.append(
                    f"sihsalus: TPED milestone {target_id} must have line={line_code}, order={order}"
                )

    if len(tped_answer_ids) != 89:
        errors.append(f"sihsalus: TPED must have 89 unique milestones; found {len(tped_answer_ids)}")

    for instrument_id, expected_targets in INSTRUMENT_SETS.items():
        actual_targets = set(targets(instrument_id, "CONCEPT-SET"))
        if actual_targets != expected_targets:
            errors.append(
                f"sihsalus: instrument set {instrument_id} mismatch: "
                f"missing={sorted(expected_targets - actual_targets)}, "
                f"unexpected={sorted(actual_targets - expected_targets)}"
            )

    for question_id, expected_targets in CODED_RESULT_SETS.items():
        question = concepts.get(question_id)
        if not question or question.get("concept_class") != "Question" or question.get("datatype") != "Coded":
            errors.append(f"sihsalus: result concept {question_id} must be Question/Coded")
        actual_targets = targets(question_id, "Q-AND-A")
        if actual_targets != expected_targets:
            errors.append(
                f"sihsalus: result answers for {question_id} mismatch: "
                f"expected={expected_targets}, actual={actual_targets}"
            )

    validate_development_forms(concepts, active_mappings, errors)


def validate_procedure_terminology(concepts, mappings, errors):
    active_mappings = [mapping for mapping in mappings if not mapping.get("retired")]

    def preferred_spanish_names(concept):
        return [
            name.get("name")
            for name in (concept or {}).get("names", [])
            if not name.get("retired")
            and name.get("locale") == "es"
            and name.get("locale_preferred")
        ]

    def ordered_targets(from_id, map_type):
        matching = [
            mapping
            for mapping in active_mappings
            if mapping.get("from_concept_code") == from_id and mapping.get("map_type") == map_type
        ]
        matching.sort(
            key=lambda mapping: (
                float(mapping["sort_weight"])
                if mapping.get("sort_weight") is not None
                else float("inf")
            )
        )
        return [mapping.get("to_concept_code") for mapping in matching]

    procedure_status = concepts.get(PROCEDURE_STATUS_ID)
    if not procedure_status:
        errors.append(f"sihsalus: missing procedure status concept {PROCEDURE_STATUS_ID}")
    else:
        if procedure_status.get("external_id") != PROCEDURE_STATUS_EXTERNAL_ID:
            errors.append(
                f"sihsalus: procedure status must use OpenMRS UUID {PROCEDURE_STATUS_EXTERNAL_ID}; "
                f"found {procedure_status.get('external_id')}"
            )
        if (
            procedure_status.get("concept_class") != "Question"
            or procedure_status.get("datatype") != "Coded"
        ):
            errors.append("sihsalus: procedure status must be Question/Coded")
        if preferred_spanish_names(procedure_status) != ["Estado del procedimiento"]:
            errors.append("sihsalus: procedure status must prefer 'Estado del procedimiento' in Spanish")

    expected_answer_ids = [concept_id for concept_id, _, _ in PROCEDURE_STATUS_ANSWERS]
    actual_answer_ids = ordered_targets(PROCEDURE_STATUS_ID, "Q-AND-A")
    if actual_answer_ids != expected_answer_ids:
        errors.append(
            f"sihsalus: procedure status answers mismatch: "
            f"expected={expected_answer_ids}, actual={actual_answer_ids}"
        )

    for concept_id, external_id, spanish_name in PROCEDURE_STATUS_ANSWERS:
        concept = concepts.get(concept_id)
        if not concept:
            errors.append(f"sihsalus: missing procedure status answer {concept_id}")
            continue
        if concept.get("external_id") != external_id:
            errors.append(
                f"sihsalus: procedure status answer {concept_id} must use UUID {external_id}; "
                f"found {concept.get('external_id')}"
            )
        if concept.get("concept_class") != "Misc" or concept.get("datatype") != "N/A":
            errors.append(f"sihsalus: procedure status answer {concept_id} must be Misc/N/A")
        if preferred_spanish_names(concept) != [spanish_name]:
            errors.append(
                f"sihsalus: procedure status answer {concept_id} must prefer {spanish_name!r} in Spanish"
            )

    unknown = concepts.get("4459")
    unknown_spanish_names = {
        name.get("name")
        for name in (unknown or {}).get("names", [])
        if not name.get("retired") and name.get("locale") == "es"
    }
    if "Desconocido" not in unknown_spanish_names:
        errors.append("sihsalus: procedure status Unknown answer must retain Spanish alias 'Desconocido'")

    medication_dispense_uuid = "167157AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    if any(
        (concepts.get(concept_id) or {}).get("external_id") == medication_dispense_uuid
        for concept_id in actual_answer_ids
    ):
        errors.append("sihsalus: medication dispense status must not be used as a procedure status answer")

    snomed_mappings = [
        mapping
        for mapping in active_mappings
        if mapping.get("from_concept_code") == PROCEDURE_STATUS_ID
        and mapping.get("map_type") == "NARROWER-THAN"
        and mapping.get("to_source_url") == "/orgs/IHTSDO/sources/SNOMED-CT/"
        and mapping.get("to_concept_code") == "416342005"
    ]
    if len(snomed_mappings) != 1:
        errors.append(
            "sihsalus: procedure status must have exactly one NARROWER-THAN mapping to SNOMED 416342005"
        )

    duration_units = concepts.get(DURATION_UNITS_ID)
    if not duration_units:
        errors.append(f"sihsalus: missing duration units concept {DURATION_UNITS_ID}")
    else:
        if duration_units.get("external_id") != DURATION_UNITS_EXTERNAL_ID:
            errors.append(
                f"sihsalus: duration units must use OpenMRS UUID {DURATION_UNITS_EXTERNAL_ID}; "
                f"found {duration_units.get('external_id')}"
            )
        if duration_units.get("concept_class") != "ConvSet" or duration_units.get("datatype") != "N/A":
            errors.append("sihsalus: duration units must be ConvSet/N/A")
        if preferred_spanish_names(duration_units) != ["Unidades de duración"]:
            errors.append("sihsalus: duration units must prefer 'Unidades de duración' in Spanish")

    expected_duration_ids = [concept_id for concept_id, _, _ in DURATION_UNIT_MEMBERS]
    actual_duration_ids = ordered_targets(DURATION_UNITS_ID, "CONCEPT-SET")
    if actual_duration_ids != expected_duration_ids:
        errors.append(
            f"sihsalus: duration units members mismatch: "
            f"expected={expected_duration_ids}, actual={actual_duration_ids}"
        )

    for concept_id, external_id, spanish_name in DURATION_UNIT_MEMBERS:
        concept = concepts.get(concept_id)
        if not concept:
            errors.append(f"sihsalus: missing duration unit {concept_id}")
            continue
        if concept.get("external_id") != external_id:
            errors.append(
                f"sihsalus: duration unit {concept_id} must use UUID {external_id}; "
                f"found {concept.get('external_id')}"
            )
        if preferred_spanish_names(concept) != [spanish_name]:
            errors.append(f"sihsalus: duration unit {concept_id} must prefer {spanish_name!r} in Spanish")


def validate_ocl_global_properties(errors):
    try:
        root = ET.parse(GLOBAL_PROPERTIES_PATH).getroot()
    except (OSError, ET.ParseError) as error:
        errors.append(f"{GLOBAL_PROPERTIES_PATH}: cannot parse global properties: {error}")
        return

    properties = {}
    for global_property in root.findall(".//globalProperty"):
        key = global_property.findtext("property")
        value = global_property.findtext("value")
        if key:
            properties[key.strip()] = (value or "").strip()

    if properties.get("openconceptlab.subscriptionUrl") != EXPECTED_SIHSALUS_SUBSCRIPTION_URL:
        errors.append(
            "openconceptlab.subscriptionUrl must point to the bundled SIHSALUS release "
            f"{EXPECTED_SIHSALUS_SUBSCRIPTION_URL}"
        )
    if properties.get("order.durationUnitsConceptUuid") != DURATION_UNITS_EXTERNAL_ID:
        errors.append(
            f"order.durationUnitsConceptUuid must be {DURATION_UNITS_EXTERNAL_ID}; "
            f"found {properties.get('order.durationUnitsConceptUuid')!r}"
        )


def validate_development_forms(concepts, mappings, errors):
    concept_id_by_external_id = {
        concept.get("external_id"): concept.get("id")
        for concept in concepts.values()
        if concept.get("external_id")
    }

    def load_form(filename):
        path = FORM_DIR / filename
        try:
            return json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{path}: cannot load form: {error}")
            return None

    def form_questions(form):
        for page in form.get("pages", []):
            for section in page.get("sections", []):
                yield from section.get("questions", [])

    mapping_targets = defaultdict(list)
    for mapping in mappings:
        if mapping.get("map_type") == "Q-AND-A":
            mapping_targets[mapping.get("from_concept_code")].append(mapping.get("to_concept_code"))

    for filename in (
        "CRED-009-EDI.json",
        "CRED-010-TAMIZAJE TEA.json",
        "CRED-011-SALUD MENTAL NIÑO Y CUIDADOR.json",
        "CRED-026-HUANCA TEST VIGILANCIA NEURODESARROLLO.json",
        "CRED-027-LISTA HABILIDADES Y CONDUCTAS ESPERADAS.json",
        "CRED-028-TPED.json",
    ):
        form = load_form(filename)
        if not form:
            continue
        for question in form_questions(form):
            options = question.get("questionOptions") or {}
            question_external_id = options.get("concept")
            if not question_external_id:
                continue
            question_id = concept_id_by_external_id.get(question_external_id)
            if not question_id:
                errors.append(f"{filename}: unresolved question concept {question_external_id}")
                continue
            expected_answers = [
                concept_id_by_external_id.get(answer.get("concept")) for answer in options.get("answers", [])
            ]
            unresolved_answers = [
                answer.get("concept")
                for answer in options.get("answers", [])
                if answer.get("concept") not in concept_id_by_external_id
            ]
            if unresolved_answers:
                errors.append(f"{filename}: unresolved answer concepts {unresolved_answers}")
            if expected_answers and not set(expected_answers).issubset(mapping_targets[question_id]):
                errors.append(
                    f"{filename}: Q-AND-A mismatch for {question_id}: "
                    f"form={expected_answers}, mappings={mapping_targets[question_id]}"
                )

    def questions_by_id(filename):
        form = load_form(filename)
        if not form:
            return None, {}
        return form, {question.get("id"): question for question in form_questions(form)}

    anemia_form, anemia = questions_by_id("CRED-001-TAMIZAJE DE ANEMIA.json")
    if anemia_form:
        if "NTS 213" not in anemia_form.get("description", "") or "NTS 137" in anemia_form.get(
            "description", ""
        ):
            errors.append("CRED-001: description must cite NTS 213 and must not cite NTS 137")
        for question_id in ("edadMeses", "hemoglobina", "altitud", "clasificacionAnemia"):
            if not anemia.get(question_id, {}).get("required"):
                errors.append(f"CRED-001: {question_id} must be required")
        anemia_labels = {
            answer.get("label")
            for answer in (anemia.get("clasificacionAnemia", {}).get("questionOptions") or {}).get(
                "answers", []
            )
        }
        if anemia_labels != {"Sin anemia", "Anemia leve", "Anemia moderada", "Anemia severa"}:
            errors.append("CRED-001: anemia answer labels must not embed a fixed hemoglobin cutoff")
        altitude_alert = anemia.get("altitud", {}).get("alert") or {}
        if altitude_alert.get("alertWhenExpression") != "altitud > 500":
            errors.append("CRED-001: altitude correction alert must start above 500 m.s.n.m.")

    edi_form, edi = questions_by_id("CRED-009-EDI.json")
    if edi_form:
        for question_id in ("edadCronologicaDias", "resultadoGlobal", "observaciones"):
            if not edi.get(question_id, {}).get("required"):
                errors.append(f"CRED-009: {question_id} must be required")
        if "cinco ejes" not in (edi.get("observaciones", {}).get("questionInfo") or ""):
            errors.append("CRED-009: the summary must explicitly cover the five EDI axes")
        if "No reemplaza" not in edi_form.get("description", ""):
            errors.append("CRED-009: description must state that the summary does not replace the official form")

    mchat_form, mchat = questions_by_id("CRED-010-TAMIZAJE TEA.json")
    if mchat_form:
        for question_id in ("edadMeses", "puntaje", "resultadoGlobal", "senalesAlerta"):
            if not mchat.get(question_id, {}).get("required"):
                errors.append(f"CRED-010: {question_id} must be required")
        if "20 ítems" not in (mchat.get("senalesAlerta", {}).get("questionInfo") or ""):
            errors.append("CRED-010: risk-item traceability must refer to the official 20 items")

    mental_form, mental = questions_by_id("CRED-011-SALUD MENTAL NIÑO Y CUIDADOR.json")
    if mental_form:
        expected_concepts = {
            "instrumentoTamizaje": "f1000000-0000-4000-8000-000000000028",
            "puntajeTamizaje": "f1000000-0000-4000-8000-000000000029",
            "resultadoTamizaje": "f1000000-0000-4000-8000-000000000030",
        }
        for question_id, expected_concept in expected_concepts.items():
            actual = (mental.get(question_id, {}).get("questionOptions") or {}).get("concept")
            if actual != expected_concept:
                errors.append(
                    f"CRED-011: {question_id} must use {expected_concept}; found {actual}"
                )
        if "resultadoSaludMental" in mental:
            errors.append("CRED-011: generic normal/risk/abnormal result must not replace instrument identity")
        if mental.get("observaciones", {}).get("required") is not True:
            errors.append("CRED-011: additional instruments and their results must be documented")
        if "instrumento adicional" not in (mental.get("observaciones", {}).get("questionInfo") or ""):
            errors.append("CRED-011: observations must request every additional instrument")

    growth_form, growth = questions_by_id("CRED-015-CRECIMIENTO Y ESTADO NUTRICIONAL.json")
    if growth_form:
        ambiguous_ids = {
            "clasificacionPesoEdad",
            "clasificacionTallaEdad",
            "clasificacionPesoTalla",
        }
        if ambiguous_ids.intersection(growth):
            errors.append("CRED-015: nutritional indicators must not reuse one generic classification concept")
        for question_id in ("edadMeses", "imc", "perimetroAbdominalCm", "diagnosticoNutricional"):
            if question_id not in growth:
                errors.append(f"CRED-015: missing {question_id}")
        imc_expression = (
            (growth.get("imc", {}).get("questionOptions") or {}).get("calculate") or {}
        ).get("calculateExpression", "")
        if "Math." in imc_expression or "pesoKg" not in imc_expression or "tallaCm" not in imc_expression:
            errors.append("CRED-015: BMI must use a portable calculation from weight and height")

    huanca_form, huanca = questions_by_id("CRED-026-HUANCA TEST VIGILANCIA NEURODESARROLLO.json")
    if huanca_form:
        if "pautaEdad" in huanca:
            errors.append("CRED-026: the obsolete mixed EDI/Huanca age selector must not be exposed")
        for area in ("MotorGrueso", "MotorFino", "Social", "Cognitivo", "Habla"):
            count = huanca.get(f"noLogrados{area}", {})
            detail = huanca.get(f"detalle{area}", {})
            if count.get("required") is not True:
                errors.append(f"CRED-026: noLogrados{area} must be required")
            if not isinstance(detail.get("required"), str):
                errors.append(f"CRED-026: detalle{area} must be conditionally required")

    skills_form, skills = questions_by_id("CRED-027-LISTA HABILIDADES Y CONDUCTAS ESPERADAS.json")
    if skills_form:
        if skills.get("edadMeses", {}).get("required") is not True:
            errors.append("CRED-027: age in months must be required for EDI/referral decisions")
        if skills.get("factorRiesgo", {}).get("required") is not True:
            errors.append("CRED-027: development risk factor must be required for the normative decision")
        if skills.get("accionInmediata", {}).get("readonly") is not True:
            errors.append("CRED-027: immediate action must be calculated and readonly")
        action_expression = (
            (skills.get("accionInmediata", {}).get("questionOptions") or {}).get("calculate") or {}
        ).get("calculateExpression", "")
        if "factorRiesgo" not in action_expression or "edadMeses <= 60" not in action_expression:
            errors.append("CRED-027: EDI/referral calculation must require absence plus a risk factor and age")
        for question_id in ("requiereEdi", "requiereInterconsulta"):
            if "factorRiesgo" not in str(skills.get(question_id, {}).get("required", "")):
                errors.append(f"CRED-027: {question_id} must require a development risk factor")
        if "No sustituye" not in skills_form.get("description", ""):
            errors.append("CRED-027: description must state that the summary does not replace the official list")

    tped_form = load_form("CRED-028-TPED.json")
    if tped_form:
        line_questions = [
            question
            for question in form_questions(tped_form)
            if (question.get("id") or "").startswith("tpedLinea")
        ]
        answer_count = sum(
            len((question.get("questionOptions") or {}).get("answers", []))
            for question in line_questions
        )
        if len(line_questions) != 12 or answer_count != 89:
            errors.append(
                f"CRED-028-TPED.json: expected 12 line questions and 89 answers; "
                f"found {len(line_questions)} and {answer_count}"
            )


if __name__ == "__main__":
    raise SystemExit(main())
