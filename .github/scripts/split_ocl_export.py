#!/usr/bin/env python3
import argparse
import json
import zipfile
from pathlib import Path


ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def canonical_json_bytes(payload):
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def read_export(path):
    with zipfile.ZipFile(path) as archive:
        members = archive.namelist()
        if members != ["export.json"]:
            raise ValueError(f"{path}: expected only export.json; found {members}")
        export = json.loads(archive.read("export.json"))

    if export.get("type") != "Source Version":
        raise ValueError(f"{path}: expected a Source Version export")
    if not isinstance(export.get("concepts"), list) or not isinstance(export.get("mappings"), list):
        raise ValueError(f"{path}: concepts and mappings must be arrays")
    return export


def write_export(path, export):
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = zipfile.ZipInfo("export.json", ZIP_TIMESTAMP)
    entry.compress_type = zipfile.ZIP_DEFLATED
    entry.create_system = 3
    entry.external_attr = 0o100644 << 16
    entry.extra = b""
    entry.comment = b""

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.writestr(entry, canonical_json_bytes(export), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def split_export(input_path, concepts_path, mappings_path):
    export = read_export(input_path)

    concepts_export = dict(export)
    concepts_export["mappings"] = []
    write_export(concepts_path, concepts_export)

    mappings_export = dict(export)
    mappings_export["concepts"] = []
    write_export(mappings_path, mappings_export)


def main():
    parser = argparse.ArgumentParser(
        description="Split one official OCL Source Version export reproducibly."
    )
    parser.add_argument("input", type=Path, help="Official combined OCL export ZIP")
    parser.add_argument("concepts_output", type=Path, help="Concepts-only output ZIP")
    parser.add_argument("mappings_output", type=Path, help="Mappings-only output ZIP")
    arguments = parser.parse_args()

    if arguments.concepts_output == arguments.mappings_output:
        parser.error("concepts and mappings outputs must be different paths")
    split_export(arguments.input, arguments.concepts_output, arguments.mappings_output)


if __name__ == "__main__":
    main()
