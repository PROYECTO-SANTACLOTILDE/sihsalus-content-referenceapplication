#!/usr/bin/env python3
import csv
import importlib.util
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("validate_hospital_institution_metadata.py")
SPEC = importlib.util.spec_from_file_location("hospital_metadata_validator", SCRIPT_PATH)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class HospitalInstitutionMetadataValidatorTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)

        for relative_path in (
            VALIDATOR.ATTRIBUTE_TYPES_PATH,
            VALIDATOR.LOCATIONS_PATH,
            VALIDATOR.INSTITUTIONAL_LOCATION_ATTRIBUTES_PATH,
            VALIDATOR.GLOBAL_PROPERTIES_PATH,
        ):
            destination = self.root / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPOSITORY_ROOT / relative_path, destination)

    def _update_csv(self, relative_path, update):
        path = self.root / relative_path
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames
            rows = list(reader)

        update(rows)

        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

    def test_repository_contract_is_valid(self):
        self.assertEqual([], VALIDATOR.validate(self.root))

    def test_rejects_invented_street_and_wrong_province(self):
        def update(rows):
            hospital = next(
                row for row in rows if row["Uuid"] == VALIDATOR.HOSPITAL_UUID
            )
            hospital["Address 4"] = "Calle no verificada"
            hospital["State/Province"] = "LORETO"

        self._update_csv(VALIDATOR.LOCATIONS_PATH, update)
        errors = "\n".join(VALIDATOR.validate(self.root))

        self.assertIn("Address 4=''", errors)
        self.assertIn("State/Province='MAYNAS'", errors)

    def test_rejects_drift_in_attributes_and_outpatient_requirement(self):
        def update_attribute_types(rows):
            phone_type = next(
                row
                for row in rows
                if row["Uuid"] == VALIDATOR.PHONE_ATTRIBUTE_UUID
            )
            phone_type["Max occurs"] = "2"

        def update_location(rows):
            hospital = next(
                row for row in rows if row["Uuid"] == VALIDATOR.HOSPITAL_UUID
            )
            hospital[VALIDATOR.PHONE_ATTRIBUTE_HEADER] = "999 999 999"
            hospital[VALIDATOR.IPRESS_ATTRIBUTE_HEADER] = ""
            hospital["Description"] = ""
            hospital["State/Province"] = "LORETO"

        self._update_csv(VALIDATOR.ATTRIBUTE_TYPES_PATH, update_attribute_types)
        self._update_csv(
            VALIDATOR.INSTITUTIONAL_LOCATION_ATTRIBUTES_PATH, update_location
        )

        global_properties = self.root / VALIDATOR.GLOBAL_PROPERTIES_PATH
        document = ET.parse(global_properties)
        for element in document.findall("./globalProperties/globalProperty"):
            if (
                element.findtext("property") or ""
            ).strip() == VALIDATOR.OUTPATIENT_QUANTITY_PROPERTY:
                element.find("value").text = "false"
        document.write(global_properties, encoding="utf-8", xml_declaration=True)

        errors = "\n".join(VALIDATOR.validate(self.root))
        self.assertIn("Max occurs='1'", errors)
        self.assertIn("965 336 199", errors)
        self.assertIn("00000066", errors)
        self.assertIn("Description=", errors)
        self.assertIn("State/Province='MAYNAS'", errors)
        self.assertIn("valor 'true'", errors)

    def test_rejects_attribute_columns_in_shared_locations_file(self):
        path = self.root / VALIDATOR.LOCATIONS_PATH
        with path.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.reader(handle))

        rows[0].append(VALIDATOR.PHONE_ATTRIBUTE_HEADER)
        for row in rows[1:]:
            row.append("")

        with path.open("w", newline="", encoding="utf-8") as handle:
            csv.writer(handle).writerows(rows)

        errors = "\n".join(VALIDATOR.validate(self.root))
        self.assertIn("CSV compartido no debe declarar atributos institucionales", errors)


if __name__ == "__main__":
    unittest.main()
