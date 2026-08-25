#!/usr/bin/env python3
"""Protect the segmented physical-examination contract for Consulta Externa."""

import json
import sys
from pathlib import Path


FORM_PATH = Path(
    "configuration/backend_configuration/ampathforms/CE-SOAP-001-NOTA SOAP.json"
)
EXPECTED_NAME = "CE-SOAP-001-NOTA SOAP"
EXPECTED_VERSION = "1.1.0"
PHYSICAL_EXAM_CONCEPT = "160532AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
REQUIRED_FIELDS = {"estadoGeneral", "resumenExamenRegional"}
SEGMENTED_FIELDS = {
    "estadoGeneral",
    "estadoHidratacion",
    "estadoNutricion",
    "estadoConciencia",
    "pielAnexos",
    "resumenExamenRegional",
    "cabezaCuello",
    "aparatoRespiratorio",
    "aparatoCardiovascular",
    "abdomenDigestivo",
    "genitourinario",
    "musculoesqueleticoExtremidades",
    "neurologico",
    "soapObjetivo",
}
LEGACY_SOAP_FIELDS = {"soapSubjetivo", "soapObjetivo", "soapEvaluacion", "soapPlan"}


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def validate_contract(form):
    errors = []
    if form.get("name") != EXPECTED_NAME:
        errors.append(f"form name must remain {EXPECTED_NAME!r}")
    if form.get("version") != EXPECTED_VERSION:
        errors.append(
            f"form version must remain {EXPECTED_VERSION}; do not overwrite historical 1.0.0"
        )

    questions = {
        node.get("id"): node
        for node in walk(form)
        if isinstance(node.get("id"), str) and node.get("type") == "obs"
    }
    missing = SEGMENTED_FIELDS - questions.keys()
    if missing:
        errors.append(f"missing segmented physical-exam fields: {sorted(missing)}")

    missing_legacy = LEGACY_SOAP_FIELDS - questions.keys()
    if missing_legacy:
        errors.append(f"missing legacy SOAP compatibility fields: {sorted(missing_legacy)}")

    for field_id in sorted(SEGMENTED_FIELDS & questions.keys()):
        question = questions[field_id]
        options = question.get("questionOptions")
        if not isinstance(options, dict):
            errors.append(f"{field_id}: questionOptions must be an object")
            continue
        if options.get("concept") != PHYSICAL_EXAM_CONCEPT:
            errors.append(f"{field_id}: must use the configured physical-exam text concept")
        if options.get("rendering") != "textarea":
            errors.append(f"{field_id}: must remain an open clinical textarea")
        if "default" in options or "answers" in options:
            errors.append(f"{field_id}: must not auto-populate a normal finding")
        expected_required = field_id in REQUIRED_FIELDS
        if (question.get("required") is True) != expected_required:
            errors.append(f"{field_id}: required must be {expected_required}")

    return errors


def main():
    try:
        form = json.loads(FORM_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"Unable to load {FORM_PATH}: {error}", file=sys.stderr)
        return 1

    errors = validate_contract(form)
    if errors:
        print("Consulta Externa physical-exam contract validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Validated CE-SOAP 1.1.0 segmented general/regional examination without "
        "automatic normal findings."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
