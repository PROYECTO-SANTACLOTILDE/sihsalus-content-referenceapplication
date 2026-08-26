#!/usr/bin/env python3

import copy
import csv
import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("validate_csv_widths.py")
sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location("validate_csv_widths", SCRIPT_PATH)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def read_csv(relative_path):
    with (REPOSITORY_ROOT / relative_path).open(
        newline="", encoding="utf-8-sig"
    ) as handle:
        return list(csv.reader(handle))


class LaboratoryAttachmentRoleContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core_rows = read_csv(VALIDATOR.ROLES_CORE_PATH)
        cls.peru_rows = read_csv(VALIDATOR.ROLES_PERU_HCE_PATH)

    def laboratory_row(self, rows):
        uuid_index = rows[0].index("Uuid")
        return next(
            row
            for row in rows[1:]
            if row[uuid_index] == VALIDATOR.LABORATORY_ROLE_UUID
        )

    def test_repository_laboratory_attachment_contract_is_valid(self):
        self.assertEqual(
            [],
            VALIDATOR.validate_laboratory_attachment_contract(self.core_rows),
        )
        self.assertEqual(
            [],
            VALIDATOR.validate_legacy_laboratory_attachment_scope(self.peru_rows),
        )

    def test_requires_both_attachment_markers_and_add_observations(self):
        rows = copy.deepcopy(self.core_rows)
        privileges_index = rows[0].index("Privileges")
        laboratory = self.laboratory_row(rows)
        privileges = VALIDATOR.split_privileges(laboratory[privileges_index])
        privileges.remove("Create Attachments")
        privileges.remove("Add Observations")
        laboratory[privileges_index] = ";".join(sorted(privileges))

        errors = "\n".join(
            VALIDATOR.validate_laboratory_attachment_contract(rows)
        )

        self.assertIn("Create Attachments", errors)
        self.assertIn("must preserve Add Observations", errors)

    def test_rejects_general_attachments_ui_edit_marker(self):
        rows = copy.deepcopy(self.core_rows)
        privileges_index = rows[0].index("Privileges")
        laboratory = self.laboratory_row(rows)
        laboratory[privileges_index] += ";app:hoja.clinica.adjuntos.editar"

        errors = "\n".join(
            VALIDATOR.validate_laboratory_attachment_contract(rows)
        )

        self.assertIn("outside the declarative", errors)
        self.assertIn("app:hoja.clinica.adjuntos.editar", errors)

    def test_rejects_attachment_markers_on_legacy_laboratory_role(self):
        rows = copy.deepcopy(self.peru_rows)
        uuid_index = rows[0].index("Uuid")
        privileges_index = rows[0].index("Privileges")
        legacy = next(
            row
            for row in rows[1:]
            if row[uuid_index] == VALIDATOR.LEGACY_LABORATORY_ROLE_UUID
        )
        legacy[privileges_index] += ";View Attachments"

        errors = "\n".join(
            VALIDATOR.validate_legacy_laboratory_attachment_scope(rows)
        )

        self.assertIn("legacy role", errors)
        self.assertIn("View Attachments", errors)

    def test_rejects_global_property_access_as_attachment_workaround(self):
        rows = copy.deepcopy(self.core_rows)
        privileges_index = rows[0].index("Privileges")
        laboratory = self.laboratory_row(rows)
        laboratory[privileges_index] += ";Get Global Properties"

        errors = "\n".join(
            VALIDATOR.validate_laboratory_attachment_contract(rows)
        )

        self.assertIn("outside the declarative", errors)
        self.assertIn("Get Global Properties", errors)

    def test_rejects_canonical_laboratory_identity_drift(self):
        rows = copy.deepcopy(self.core_rows)
        role_index = rows[0].index("Role name")
        self.laboratory_row(rows)[role_index] = "Laboratorio alterno"

        errors = "\n".join(
            VALIDATOR.validate_laboratory_attachment_contract(rows)
        )

        self.assertIn("must keep the name 'Laboratorio'", errors)


if __name__ == "__main__":
    unittest.main()
