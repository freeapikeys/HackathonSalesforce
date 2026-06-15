#!/usr/bin/env python3

from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "config" / "core-salesforce-model.json"
DEFAULT_OUTPUT = ROOT / "force-app" / "main" / "default"
METADATA_NAMESPACE = "http://soap.sforce.com/2006/04/metadata"

ET.register_namespace("", METADATA_NAMESPACE)

FIELD_SETS = {
    "tenantRecord": [
        {
            "api": "External_Key__c",
            "label": "External Key",
            "type": "Text",
            "length": 160,
            "required": True,
            "externalId": True,
            "unique": True,
        },
        {
            "api": "Tenant_Key__c",
            "label": "Tenant Key",
            "type": "Text",
            "length": 80,
            "required": True,
        },
    ],
    "sourceEvent": [
        {
            "api": "Source_Event__c",
            "label": "Source Event",
            "type": "Lookup",
            "referenceTo": "HFS_Event__c",
            "required": True,
        }
    ],
}

REQUIRED_LOOKUPS = {
    "HFS_Entity__c": {"Source_Event__c": "HFS_Event__c"},
    "HFS_Relationship__c": {
        "Source_Event__c": "HFS_Event__c",
        "Subject_Entity__c": "HFS_Entity__c",
        "Object_Entity__c": "HFS_Entity__c",
    },
    "HFS_Event_Participant__c": {
        "Event__c": "HFS_Event__c",
        "Entity__c": "HFS_Entity__c",
    },
    "HFS_Agreement__c": {
        "Source_Event__c": "HFS_Event__c",
        "Party_One__c": "HFS_Entity__c",
        "Party_Two__c": "HFS_Entity__c",
    },
    "HFS_Work_Item__c": {
        "Primary_Entity__c": "HFS_Entity__c",
        "Trigger_Event__c": "HFS_Event__c",
    },
    "HFS_SOP_Execution__c": {"Work_Item__c": "HFS_Work_Item__c"},
    "HFS_Evidence__c": {
        "Source_Event__c": "HFS_Event__c",
        "Work_Item__c": "HFS_Work_Item__c",
    },
    "HFS_Recommendation__c": {
        "Work_Item__c": "HFS_Work_Item__c",
        "Subject_Entity__c": "HFS_Entity__c",
        "Primary_Evidence__c": "HFS_Evidence__c",
    },
    "HFS_Approval__c": {"Recommendation__c": "HFS_Recommendation__c"},
    "HFS_Action__c": {
        "Recommendation__c": "HFS_Recommendation__c",
        "Approval__c": "HFS_Approval__c",
        "Target_Entity__c": "HFS_Entity__c",
    },
    "HFS_Outcome__c": {
        "Source_Event__c": "HFS_Event__c",
        "Action__c": "HFS_Action__c",
    },
    "HFS_Evaluation__c": {"Outcome__c": "HFS_Outcome__c"},
}


def metadata_element(name: str) -> ET.Element:
    return ET.Element(f"{{{METADATA_NAMESPACE}}}{name}")


def child(parent: ET.Element, name: str, value: object) -> ET.Element:
    element = ET.SubElement(parent, f"{{{METADATA_NAMESPACE}}}{name}")
    if isinstance(value, bool):
        element.text = str(value).lower()
    else:
        element.text = str(value)
    return element


def xml_bytes(root: ET.Element) -> bytes:
    ET.indent(root, space="    ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def write_xml(path: Path, root: ET.Element) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(xml_bytes(root))
    with path.open("ab") as output:
        output.write(b"\n")


def expanded_fields(object_definition: dict[str, object]) -> list[dict[str, object]]:
    fields: list[dict[str, object]] = []
    for field_set in object_definition.get("fieldSets", []):
        fields.extend(copy.deepcopy(FIELD_SETS[field_set]))
    fields.extend(copy.deepcopy(object_definition.get("fields", [])))
    return fields


def metadata_required(field: dict[str, object]) -> bool:
    return bool(field.get("required")) and field["type"] != "LongTextArea"


def relationship_name(object_api: str, field_api: str) -> str:
    object_name = object_api.removesuffix("__c")
    field_name = field_api.removesuffix("__c")
    return f"{object_name}_{field_name}"[:40]


def relationship_label(object_definition: dict[str, object], field: dict[str, object]) -> str:
    return f"{object_definition['pluralLabel']} by {field['label']}"[:80]


def render_object(object_definition: dict[str, object], output: Path) -> None:
    object_api = str(object_definition["api"])
    object_dir = output / "objects" / object_api

    root = metadata_element("CustomObject")
    child(root, "deploymentStatus", "Deployed")
    child(root, "description", object_definition["description"])
    child(root, "enableActivities", False)
    child(root, "enableHistory", True)
    child(root, "enableReports", True)
    child(root, "enableSearch", True)
    child(root, "label", object_definition["label"])

    name_field = ET.SubElement(root, f"{{{METADATA_NAMESPACE}}}nameField")
    child(name_field, "displayFormat", f"{object_definition['prefix']}-{{000000}}")
    child(name_field, "label", f"{object_definition['label']} Number")
    child(name_field, "type", "AutoNumber")

    child(root, "pluralLabel", object_definition["pluralLabel"])
    child(root, "sharingModel", "ReadWrite")
    write_xml(object_dir / f"{object_api}.object-meta.xml", root)

    for field in expanded_fields(object_definition):
        render_field(object_definition, field, object_dir)

    for rule in object_definition.get("validationRules", []):
        render_validation_rule(rule, object_dir)


def render_field(
    object_definition: dict[str, object],
    field: dict[str, object],
    object_dir: Path,
) -> None:
    root = metadata_element("CustomField")
    child(root, "fullName", field["api"])

    field_type = str(field["type"])
    if field_type == "Lookup":
        child(root, "deleteConstraint", "Restrict" if field.get("required") else "SetNull")

    if field.get("externalId"):
        child(root, "externalId", True)

    child(root, "label", field["label"])

    if field_type in {"Text", "LongTextArea"}:
        child(root, "length", field["length"])

    if field_type == "Lookup":
        child(root, "referenceTo", field["referenceTo"])
        child(
            root,
            "relationshipLabel",
            relationship_label(object_definition, field),
        )
        child(
            root,
            "relationshipName",
            relationship_name(str(object_definition["api"]), str(field["api"])),
        )

    if metadata_required(field):
        child(root, "required", True)

    if field_type == "Number":
        child(root, "precision", field["precision"])
        child(root, "scale", field["scale"])

    child(root, "type", field_type)

    if field.get("unique"):
        child(root, "unique", True)

    if field_type == "LongTextArea":
        child(root, "visibleLines", field.get("visibleLines", 5))

    if field_type == "Picklist":
        value_set = ET.SubElement(root, f"{{{METADATA_NAMESPACE}}}valueSet")
        child(value_set, "restricted", True)
        definition = ET.SubElement(
            value_set,
            f"{{{METADATA_NAMESPACE}}}valueSetDefinition",
        )
        child(definition, "sorted", False)
        for value in field["values"]:
            value_element = ET.SubElement(
                definition,
                f"{{{METADATA_NAMESPACE}}}value",
            )
            child(value_element, "fullName", value)
            child(value_element, "default", False)
            child(value_element, "label", str(value).replace("_", " ").title())

    write_xml(
        object_dir / "fields" / f"{field['api']}.field-meta.xml",
        root,
    )


def render_validation_rule(rule: dict[str, object], object_dir: Path) -> None:
    root = metadata_element("ValidationRule")
    child(root, "fullName", rule["api"])
    child(root, "active", True)
    child(root, "description", rule["message"])
    child(root, "errorConditionFormula", rule["formula"])
    child(root, "errorMessage", rule["message"])
    write_xml(
        object_dir
        / "validationRules"
        / f"{rule['api']}.validationRule-meta.xml",
        root,
    )


def render_custom_permission(
    permission: dict[str, object],
    output: Path,
) -> None:
    root = metadata_element("CustomPermission")
    child(root, "description", permission["description"])
    child(root, "isLicensed", False)
    child(root, "label", permission["label"])
    write_xml(
        output
        / "customPermissions"
        / f"{permission['api']}.customPermission-meta.xml",
        root,
    )


def object_access(
    permission_set: dict[str, object],
    object_api: str,
) -> dict[str, bool]:
    editable_objects = set(permission_set.get("editableObjects", []))
    update_only_objects = set(permission_set.get("updateOnlyObjects", []))
    delete_objects = set(permission_set.get("deleteObjects", []))
    creatable = "*" in editable_objects or object_api in editable_objects
    editable = (
        creatable
        or "*" in update_only_objects
        or object_api in update_only_objects
    )
    deletable = "*" in delete_objects or object_api in delete_objects
    return {
        "allowCreate": creatable,
        "allowDelete": deletable,
        "allowEdit": editable,
        "allowRead": True,
        "modifyAllRecords": bool(permission_set.get("modifyAllRecords")),
        "viewAllRecords": bool(permission_set.get("viewAllRecords")),
    }


def field_editable(
    permission_set: dict[str, object],
    object_api: str,
    field_api: str,
) -> bool:
    editable_objects = set(permission_set.get("editableObjects", []))
    if "*" in editable_objects or object_api in editable_objects:
        return True

    editable_fields = permission_set.get("editableFields", {})
    if not isinstance(editable_fields, dict):
        return False

    object_fields = set(editable_fields.get(object_api, []))
    wildcard_fields = set(editable_fields.get("*", []))
    return (
        "*" in object_fields
        or field_api in object_fields
        or field_api in wildcard_fields
    )


def render_permission_set(
    permission_set: dict[str, object],
    objects: list[dict[str, object]],
    output: Path,
) -> None:
    root = metadata_element("PermissionSet")

    for apex_class in permission_set.get("apexClasses", []):
        class_access = ET.SubElement(
            root,
            f"{{{METADATA_NAMESPACE}}}classAccesses",
        )
        child(class_access, "apexClass", apex_class)
        child(class_access, "enabled", True)

    for custom_permission in permission_set.get("customPermissions", []):
        permission_element = ET.SubElement(
            root,
            f"{{{METADATA_NAMESPACE}}}customPermissions",
        )
        child(permission_element, "enabled", True)
        child(permission_element, "name", custom_permission)

    child(root, "description", permission_set["description"])

    for object_definition in objects:
        access = object_access(permission_set, str(object_definition["api"]))
        for field in expanded_fields(object_definition):
            if metadata_required(field):
                continue
            field_permission = ET.SubElement(
                root,
                f"{{{METADATA_NAMESPACE}}}fieldPermissions",
            )
            child(
                field_permission,
                "editable",
                field_editable(
                    permission_set,
                    str(object_definition["api"]),
                    str(field["api"]),
                ),
            )
            child(
                field_permission,
                "field",
                f"{object_definition['api']}.{field['api']}",
            )
            child(field_permission, "readable", True)

    child(root, "hasActivationRequired", False)
    child(root, "label", permission_set["label"])

    for tab_setting in permission_set.get("tabSettings", []):
        tab_element = ET.SubElement(
            root,
            f"{{{METADATA_NAMESPACE}}}tabSettings",
        )
        child(tab_element, "tab", tab_setting["tab"])
        child(tab_element, "visibility", tab_setting["visibility"])

    for object_definition in objects:
        permissions = ET.SubElement(
            root,
            f"{{{METADATA_NAMESPACE}}}objectPermissions",
        )
        access = object_access(permission_set, str(object_definition["api"]))
        for permission_name in (
            "allowCreate",
            "allowDelete",
            "allowEdit",
            "allowRead",
            "modifyAllRecords",
        ):
            child(permissions, permission_name, access[permission_name])
        child(permissions, "object", object_definition["api"])
        child(permissions, "viewAllRecords", access["viewAllRecords"])

    write_xml(
        output
        / "permissionsets"
        / f"{permission_set['api']}.permissionset-meta.xml",
        root,
    )


def validate_model(model: dict[str, object]) -> None:
    object_apis = [str(item["api"]) for item in model["objects"]]
    assert len(object_apis) == len(set(object_apis)), "Object API names must be unique."

    required_objects = {
        "HFS_Entity__c",
        "HFS_Relationship__c",
        "HFS_Event__c",
        "HFS_Event_Participant__c",
        "HFS_Agreement__c",
        "HFS_Work_Item__c",
        "HFS_SOP_Execution__c",
        "HFS_Evidence__c",
        "HFS_Recommendation__c",
        "HFS_Approval__c",
        "HFS_Action__c",
        "HFS_Outcome__c",
        "HFS_Evaluation__c",
    }
    assert set(object_apis) == required_objects, (
        "Core model objects do not match the vertical-slice contract."
    )

    for object_definition in model["objects"]:
        fields = expanded_fields(object_definition)
        field_apis = [str(field["api"]) for field in fields]
        assert len(field_apis) == len(set(field_apis)), (
            f"Duplicate field API in {object_definition['api']}."
        )
        for field in fields:
            if field["type"] == "Lookup":
                assert field["referenceTo"] in required_objects | {"User"}, (
                    f"Unknown lookup target {field['referenceTo']}."
                )

        fields_by_api = {str(field["api"]): field for field in fields}
        for field_api, target in REQUIRED_LOOKUPS.get(
            str(object_definition["api"]),
            {},
        ).items():
            field = fields_by_api.get(field_api)
            assert field is not None, (
                f"{object_definition['api']} is missing required lookup {field_api}."
            )
            assert metadata_required(field), (
                f"{object_definition['api']}.{field_api} must be metadata-required."
            )
            assert field["referenceTo"] == target, (
                f"{object_definition['api']}.{field_api} must reference {target}."
            )

    permission_names = {
        str(permission["api"]) for permission in model["customPermissions"]
    }
    for permission_set in model["permissionSets"]:
        assert set(permission_set.get("customPermissions", [])) <= permission_names
        assert all(permission_set.get("apexClasses", []))

    permission_sets = {
        str(permission_set["api"]): permission_set
        for permission_set in model["permissionSets"]
    }
    assert "HFS_Approve_Recommendation" in permission_sets[
        "HFS_Approver"
    ].get("customPermissions", [])
    assert "HFS_Execute_Action" in permission_sets[
        "HFS_Integration_User"
    ].get("customPermissions", [])


def generate(model: dict[str, object], output: Path) -> None:
    validate_model(model)
    for object_definition in model["objects"]:
        render_object(object_definition, output)
    for custom_permission in model["customPermissions"]:
        render_custom_permission(custom_permission, output)
    for permission_set in model["permissionSets"]:
        render_permission_set(permission_set, model["objects"], output)


def generated_paths(root: Path) -> set[Path]:
    paths: set[Path] = set()
    for pattern in (
        "objects/HFS_*",
        "permissionsets/HFS_*",
        "customPermissions/HFS_*",
    ):
        for path in root.glob(pattern):
            if path.is_file():
                paths.add(path.relative_to(root))
            elif path.is_dir():
                paths.update(
                    child_path.relative_to(root)
                    for child_path in path.rglob("*")
                    if child_path.is_file()
                )
    return paths


def same_metadata(expected_path: Path, actual_path: Path) -> bool:
    expected = expected_path.read_bytes().replace(b"\r\n", b"\n")
    actual = actual_path.read_bytes().replace(b"\r\n", b"\n")
    return expected == actual


def check_generated(model: dict[str, object]) -> int:
    with tempfile.TemporaryDirectory(prefix="hfs-metadata-") as directory:
        expected_root = Path(directory)
        generate(model, expected_root)
        expected_paths = generated_paths(expected_root)
        actual_paths = generated_paths(DEFAULT_OUTPUT)

        missing = expected_paths - actual_paths
        extra = actual_paths - expected_paths
        changed = {
            path
            for path in expected_paths & actual_paths
            if not same_metadata(expected_root / path, DEFAULT_OUTPUT / path)
        }

        for label, paths in (
            ("missing", missing),
            ("extra", extra),
            ("changed", changed),
        ):
            for path in sorted(paths):
                print(f"{label}: {path}", file=sys.stderr)

        if missing or extra or changed:
            print(
                "Run scripts/generate_core_salesforce_metadata.py to regenerate.",
                file=sys.stderr,
            )
            return 1

    print(
        f"Salesforce metadata matches model {model['version']} "
        f"({len(model['objects'])} objects)."
    )
    return 0


def clear_generated(output: Path) -> None:
    for path in generated_paths(output):
        (output / path).unlink()

    for directory in sorted(
        (
            path
            for root_name in ("objects", "permissionsets", "customPermissions")
            for path in (output / root_name).glob("HFS_*")
            if path.is_dir()
        ),
        reverse=True,
    ):
        shutil.rmtree(directory)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when checked-in metadata differs from the model.",
    )
    args = parser.parse_args()

    model = json.loads(MODEL_PATH.read_text())
    if args.check:
        return check_generated(model)

    clear_generated(DEFAULT_OUTPUT)
    generate(model, DEFAULT_OUTPUT)
    print(
        f"Generated Salesforce metadata model {model['version']} "
        f"with {len(model['objects'])} objects."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
