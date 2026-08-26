#!/usr/bin/env python3
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_PATH = Path(__file__).with_name("validate_ocl_exports.py")
sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location("validate_ocl_exports", SCRIPT_PATH)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ReferralTransportCatalogValidationTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.ocl_directory = Path(self.temporary_directory.name) / "ocl"
        self.ocl_directory.mkdir()
        self.concepts_path = self.ocl_directory / (
            "16_SIHSALUS_referencia-institucional_concepts_2026-08-25-01.zip"
        )
        self.concepts_path.touch()
        self.csv_path = Path(self.temporary_directory.name) / "referral_transport_concepts.csv"

    def tearDown(self):
        self.temporary_directory.cleanup()

    def concept(self, terminology):
        (
            concept_id,
            external_id,
            spanish_fsn,
            spanish_short,
            english_fsn,
            english_short,
            spanish_description,
        ) = terminology
        return {
            "id": concept_id,
            "external_id": external_id,
            "concept_class": "Misc",
            "datatype": "N/A",
            "retired": False,
            "url": (
                f"/orgs/SIHSALUS/sources/{VALIDATOR.REFERRAL_SOURCE}/"
                f"concepts/{concept_id}/"
            ),
            "names": [
                {
                    "name": spanish_fsn,
                    "locale": "es",
                    "locale_preferred": True,
                    "name_type": "Fully-Specified",
                    "retired": False,
                },
                {
                    "name": spanish_short,
                    "locale": "es",
                    "locale_preferred": False,
                    "name_type": "Short",
                    "retired": False,
                },
                {
                    "name": english_fsn,
                    "locale": "en",
                    "locale_preferred": True,
                    "name_type": "Fully-Specified",
                    "retired": False,
                },
                {
                    "name": english_short,
                    "locale": "en",
                    "locale_preferred": False,
                    "name_type": "Short",
                    "retired": False,
                },
            ],
            "descriptions": [
                {
                    "description": spanish_description,
                    "locale": "es",
                    "locale_preferred": True,
                    "retired": False,
                }
            ],
        }

    def valid_export(self):
        return {
            "type": "Source Version",
            "id": VALIDATOR.REFERRAL_VERSION,
            "version": VALIDATOR.REFERRAL_VERSION,
            "short_code": VALIDATOR.REFERRAL_SOURCE,
            "owner": "SIHSALUS",
            "owner_type": "Organization",
            "released": True,
            "source": {
                "id": VALIDATOR.REFERRAL_SOURCE,
                "owner": "SIHSALUS",
                "owner_type": "Organization",
                "url": f"/orgs/SIHSALUS/sources/{VALIDATOR.REFERRAL_SOURCE}/",
                "custom_validation_schema": "OpenMRS",
                "default_locale": "es",
                "supported_locales": ["es", "en"],
                "extras": {"catalog_domain": "institutional-referral"},
            },
            "concepts": [
                self.concept(terminology)
                for terminology in VALIDATOR.REFERRAL_TRANSPORT_CONCEPTS
            ],
            "mappings": [],
        }

    def concept_records(self, export):
        return [
            (self.concepts_path, VALIDATOR.REFERRAL_SOURCE, concept)
            for concept in export["concepts"]
        ]

    def canonical_digest(self, export):
        canonical = VALIDATOR.json.dumps(
            export,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        return VALIDATOR.hashlib.sha256(canonical).hexdigest()

    def validator_globals(self, export):
        return mock.patch.multiple(
            VALIDATOR,
            OCL_DIR=self.ocl_directory,
            REFERRAL_CONCEPTS_EXPORT=self.concepts_path,
            REFERRAL_TRANSPORT_CSV=self.csv_path,
            EXPECTED_REFERRAL_CANONICAL_SHA256=self.canonical_digest(export),
        )

    def test_accepts_exact_released_catalog(self):
        export = self.valid_export()
        errors = []
        with self.validator_globals(export):
            VALIDATOR.validate_referral_transport_terminology(
                {self.concepts_path: export}, self.concept_records(export), errors
            )
        self.assertEqual([], errors)

    def test_rejects_initializer_csv_after_migration(self):
        export = self.valid_export()
        self.csv_path.touch()
        errors = []
        with self.validator_globals(export):
            VALIDATOR.validate_referral_transport_terminology(
                {self.concepts_path: export}, self.concept_records(export), errors
            )
        self.assertTrue(any("remove the Initializer CSV" in error for error in errors))

    def test_rejects_uuid_bundled_from_another_source(self):
        export = self.valid_export()
        records = self.concept_records(export)
        records.append(
            (
                self.ocl_directory / "10_SIHSALUS_sihsalus_concepts.zip",
                "sihsalus",
                {
                    "id": "legacy",
                    "external_id": VALIDATOR.REFERRAL_TRANSPORT_CONCEPTS[0][1],
                },
            )
        )
        errors = []
        with self.validator_globals(export):
            VALIDATOR.validate_referral_transport_terminology(
                {self.concepts_path: export}, records, errors
            )
        self.assertTrue(any("must be bundled exactly once" in error for error in errors))

    def test_rejects_changed_short_name(self):
        export = self.valid_export()
        export["concepts"][0]["names"][1]["name"] = "Tierra"
        errors = []
        with self.validator_globals(export):
            VALIDATOR.validate_referral_transport_terminology(
                {self.concepts_path: export}, self.concept_records(export), errors
            )
        self.assertTrue(any("names mismatch" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
