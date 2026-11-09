#!/usr/bin/env python3
"""Doc guards for the UI spec layer (story #182, rule 38). Stdlib only.

Every folder under --root is one component: <Name>/<Name>.doc.mjs plus <Name>/<Name>.contract.json.
Fails when: a doc or contract is missing; either breaks its JSON schema (ui/schema/); a doc names a prop
the contract lacks (core, a platform, or webOnly); a contract prop has no doc; an enum prop's doc type
does not spell out exactly the contract's literal values. Upstream idea: Astryx docPropReferences and
docPropLiterals tests (meta/astryx, MIT).

A .doc.mjs body is a JSON literal after `export default`, so Node and Python read the same file.
usage: check_ui_docs.py [--root ui/components]
"""
import argparse
import json
import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
SCHEMAS = KIT / "ui" / "schema"
TYPES = {"string": str, "object": dict, "array": list, "boolean": bool, "null": type(None), "number": (int, float)}


def validate(value, schema, root, path="$"):
    """The JSON Schema subset our two schemas use: $ref, type, enum, required, properties, additionalProperties, items."""
    if "$ref" in schema:
        schema = root["$defs"][schema["$ref"].rsplit("/", 1)[1]]
    errs = []
    types = schema.get("type")
    if types:
        allowed = tuple(TYPES[t] for t in ([types] if isinstance(types, str) else types))
        if not isinstance(value, allowed) or (isinstance(value, bool) and bool not in allowed):
            return [f"{path}: must be {types}"]
    if "enum" in schema and value not in schema["enum"]:
        errs.append(f"{path}: must be one of {schema['enum']}")
    if isinstance(value, dict):
        errs += [f"{path}: missing required field '{k}'" for k in schema.get("required", []) if k not in value]
        props, extra = schema.get("properties", {}), schema.get("additionalProperties", True)
        for k, v in value.items():
            if k in props:
                errs += validate(v, props[k], root, f"{path}.{k}")
            elif extra is False:
                errs.append(f"{path}: unknown field '{k}'")
            elif isinstance(extra, dict):
                errs += validate(v, extra, root, f"{path}.{k}")
    if isinstance(value, list) and "items" in schema:
        for i, v in enumerate(value):
            errs += validate(v, schema["items"], root, f"{path}[{i}]")
    return errs


def read_doc(path):
    m = re.search(r"^export default\s*", path.read_text(encoding="utf-8"), re.M)
    if not m:
        raise ValueError("no `export default` found")
    return json.JSONDecoder().raw_decode(path.read_text(encoding="utf-8"), m.end())[0]


def literals(spec_type):
    """The doc `type` string a contract enum needs, e.g. "'sm' | 'md'"."""
    vals = spec_type["values"]
    return " | ".join(f"'{v}'" if spec_type["kind"] == "enum" else str(v) for v in vals)


def check_component(folder, doc_schema, contract_schema):
    name = folder.name
    doc_path, contract_path = folder / f"{name}.doc.mjs", folder / f"{name}.contract.json"
    missing = [f"{name}: missing {p.name}" for p in (doc_path, contract_path) if not p.exists()]
    if missing:
        return missing
    try:
        doc = read_doc(doc_path)
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except ValueError as e:
        return [f"{name}: cannot read as JSON: {e}"]
    errs = [f"{doc_path.name} {e}" for e in validate(doc, doc_schema, doc_schema)]
    errs += [f"{contract_path.name} {e}" for e in validate(contract, contract_schema, contract_schema)]
    if errs:
        return errs
    specs = dict(contract["core"])
    for platform_props in contract["platforms"].values():
        specs.update(platform_props)
    web_only = {w["name"] for w in contract["webOnly"]}
    documented = {p["name"]: p for p in doc["props"]}
    for prop, p in documented.items():
        if prop not in specs and prop not in web_only:
            errs.append(f"{name}: doc names prop '{prop}', but the contract has no such prop (add it to core, a platform, or webOnly with a reason)")
            continue
        t = specs.get(prop, {}).get("type", {})
        if t.get("kind") in ("enum", "numberEnum"):
            want = {str(v) for v in t["values"]}
            got = set(re.findall(r"'([^']*)'", p["type"])) if t["kind"] == "enum" else set(re.findall(r"-?\d+(?:\.\d+)?", p["type"]))
            if got != want:
                errs.append(f"{name}: prop '{prop}' type \"{p['type']}\" must spell out its values: {literals(t)}")
    errs += [f"{name}: contract prop '{prop}' has no doc entry" for prop in specs if prop not in documented]
    return errs


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default="ui/components", help="folder with one subfolder per component")
    root = Path(ap.parse_args().root)
    doc_schema = json.loads((SCHEMAS / "component.schema.json").read_text(encoding="utf-8"))
    contract_schema = json.loads((SCHEMAS / "contract.schema.json").read_text(encoding="utf-8"))
    folders = sorted(p for p in root.iterdir() if p.is_dir()) if root.is_dir() else []
    if not folders:
        print(f"no components under {root}: nothing to check")
        return 0
    errs = [e for f in folders for e in check_component(f, doc_schema, contract_schema)]
    for e in errs:
        print("FAIL", e)
    if errs:
        return 1
    print(f"OK: {len(folders)} component doc(s) match their contracts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
