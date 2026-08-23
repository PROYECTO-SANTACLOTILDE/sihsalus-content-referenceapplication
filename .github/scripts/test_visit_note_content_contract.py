#!/usr/bin/env python3

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("validate_visit_note_content_contract.py")
sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location("validate_visit_note_content_contract", SCRIPT_PATH)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class VisitNoteContentContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[2]
        cls.contract = json.loads((cls.root / VALIDATOR.CONTRACT_PATH).read_text())
        errors = []
        cls.catalog = VALIDATOR.load_concept_catalog(cls.root, errors)
        if errors:
            raise AssertionError(errors)

    def test_repository_contract_is_valid(self):
        self.assertEqual([], VALIDATOR.validate(self.root))

    def test_rejects_wrong_concept_datatype(self):
        contract = copy.deepcopy(self.contract)
        contract["concepts"][0]["datatype"] = "Coded"
        errors = VALIDATOR.validate_concepts(contract, self.catalog)
        self.assertTrue(any("must be Coded" in error for error in errors))

    def test_rejects_misleading_run_always_contract(self):
        xml_text = (self.root / VALIDATOR.LIQUIBASE_PATH).read_text().replace(
            '<changeSet id="ensure-canonical-visit-note-encounter-type-20260823" author="sihsalus">',
            '<changeSet id="ensure-canonical-visit-note-encounter-type-20260823" '
            'author="sihsalus" runAlways="true">',
            1,
        )
        errors = VALIDATOR.validate_liquibase_contract(self.contract, xml_text)
        self.assertTrue(any("must not rely on runAlways" in error for error in errors))

    def test_requires_one_start_encounter_type_bootstrap(self):
        xml_text = (self.root / VALIDATOR.LIQUIBASE_PATH).read_text().replace(
            "'Notas de Atención'", "'Wrong encounter name'", 1
        )
        errors = VALIDATOR.validate_liquibase_contract(self.contract, xml_text)
        self.assertTrue(any("bootstrapped idempotently" in error for error in errors))

    def test_rejects_reassigning_an_existing_encounter_type(self):
        xml_text = (self.root / VALIDATOR.LIQUIBASE_PATH).read_text().replace(
            "AND visit_note.encounter_type IS NULL;", "AND 1 = 1;", 1
        )
        errors = VALIDATOR.validate_liquibase_contract(self.contract, xml_text)
        self.assertTrue(any("only complete a missing encounter_type" in error for error in errors))

    def test_rejects_frontend_default_drift(self):
        expected = VALIDATOR.expected_frontend_defaults(self.contract)
        schema = "\n".join(
            f"  {key}: {{\n    _default: '{value}',\n  }}," for key, value in expected.items()
        )
        schema = schema.replace(expected["formConceptUuid"], "00000000-0000-0000-0000-000000000000")
        errors = VALIDATOR.validate_frontend_schema(self.contract, schema, Path("fixture.ts"))
        self.assertTrue(any("formConceptUuid must default" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
