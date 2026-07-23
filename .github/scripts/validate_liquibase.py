#!/usr/bin/env python3

from pathlib import Path
import xml.etree.ElementTree as ET


LIQUIBASE_NAMESPACE = "http://www.liquibase.org/xml/ns/dbchangelog/1.9"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def validate_change_set(path: Path, change_set: ET.Element) -> None:
    children = [local_name(child.tag) for child in change_set]
    change_set_id = change_set.get("id", "<sin id>")

    if "preConditions" in children and children.index("preConditions") != 0:
        raise ValueError(
            f"{path}: changeSet {change_set_id}: preConditions debe ser el primer elemento"
        )

    if "comment" in children:
        comment_index = children.index("comment")
        first_change_index = 1 if children and children[0] == "preConditions" else 0
        if comment_index != first_change_index:
            raise ValueError(
                f"{path}: changeSet {change_set_id}: comment debe preceder a los cambios"
            )


def main() -> None:
    paths = sorted(Path("configuration").glob("**/liquibase/*.xml"))
    if not paths:
        raise ValueError("No se encontraron changelogs Liquibase para validar")

    for path in paths:
        root = ET.parse(path).getroot()
        namespace = root.tag.removeprefix("{").split("}", 1)[0]
        if namespace != LIQUIBASE_NAMESPACE:
            raise ValueError(f"{path}: namespace Liquibase inesperado: {namespace}")

        for change_set in root.findall(f"{{{LIQUIBASE_NAMESPACE}}}changeSet"):
            validate_change_set(path, change_set)

    print(f"Validated Liquibase 1.9 element ordering in {len(paths)} changelog file(s).")


if __name__ == "__main__":
    main()
