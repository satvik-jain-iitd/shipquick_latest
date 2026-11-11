#!/usr/bin/env python3
"""Story #418 (F1, epic #86): which ShipQuick features are on in this project.

  features.py [--root DIR] get <id>   prints on (exit 0) or off (exit 1); an unknown id exits 2, never "on"
  features.py [--root DIR] list       one line per feature: id on|off
  features.py [--root DIR] set <id> on|off   rewrites the file (features.sh is the owner's front door; refuses locked ids)
  features.py [--root DIR] sync       the file adopt.sh writes, on stdout: every kit id, the owner's values kept; notes on stderr
  features.py [--root DIR] json       the whole map: on, default, locked and the plain words, for CI and the Desk

State lives in `<root>/.shipquick/features.json` (a protected path: only a PR the owner merges changes it).
The kit's list, defaults and plain words live in `scripts/features_default.json`. A missing project file means
every feature at its default. Locked features (adoption, gate) always read on. A file that is not valid JSON, or
holds a non-boolean `on`, exits 2 with the reason and never falls back to defaults. Stdlib only. ADR-016."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


class FeaturesError(Exception):
    pass


def _load(path, what):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise FeaturesError(f"{what} is not valid JSON: line {e.lineno}, column {e.colno}: {e.msg}")
    except UnicodeDecodeError as e:
        raise FeaturesError(f"{what} is not valid UTF-8: byte {e.start}")
    except (OSError, ValueError) as e:
        raise FeaturesError(f"cannot read {what}: {e}")


def _defaults(path):
    data = _load(path, "scripts/features_default.json")
    feats = data.get("features") if isinstance(data, dict) else None
    if not isinstance(feats, dict) or not feats:
        raise FeaturesError("scripts/features_default.json needs a non-empty `features` object")
    for fid, d in feats.items():
        if not isinstance(d, dict) or not isinstance(d.get("default"), bool):
            raise FeaturesError(f"scripts/features_default.json: `{fid}` needs a true or false `default`")
    return feats


def read(root, defaults=None):
    """The merged map {"features": {id: {...}}, "unknown": [ids the kit does not know]}."""
    defaults = _defaults(defaults or HERE / "features_default.json")
    f = Path(root) / ".shipquick" / "features.json"
    mine = {}
    if f.is_file():
        data = _load(f, ".shipquick/features.json")
        mine = data.get("features") if isinstance(data, dict) else None
        if not isinstance(mine, dict):
            raise FeaturesError(".shipquick/features.json needs a `features` object")
    out = {}
    for fid, d in defaults.items():
        row = dict(d)
        entry = mine.get(fid)
        on = d["default"]
        if entry is not None:
            on = entry.get("on", d["default"]) if isinstance(entry, dict) else None
            if not isinstance(on, bool):
                raise FeaturesError(f".shipquick/features.json: `{fid}.on` must be true or false")
        row["on"] = True if d.get("locked") else on
        out[fid] = row
    return {"features": out, "unknown": sorted(k for k in mine if k not in defaults)}


def set_feature(root, fid, word):
    """Write `on` for one feature. Returns None, or (exit code, message) when it refuses."""
    m = read(root)   # a broken file raises here and is never overwritten
    row = m["features"].get(fid)
    if row is None or word not in ("on", "off"):
        return 2, f"usage: features.sh set <id> on|off ({'unknown feature `' + fid + '`' if row is None else 'the word must be on or off'}; known: {', '.join(m['features'])})"
    if row.get("locked"):
        return 1, f"features.sh: `{fid}` is locked: it guards every other feature and always stays on"
    f = Path(root) / ".shipquick" / "features.json"
    data = json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {"version": 1, "features": {}}
    feats = data["features"]
    for k, d in m["features"].items():
        feats.setdefault(k, {"on": d["default"], "default": d["default"]})
    feats[fid]["on"] = word == "on"
    f.parent.mkdir(exist_ok=True)
    f.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return None


def sync_text(root):
    """(file text, notes): every kit id present, the owner's values kept, new ids at their default, dropped ids kept."""
    m = read(root)
    f = Path(root) / ".shipquick" / "features.json"
    data = _load(f, ".shipquick/features.json") if f.is_file() else {"version": 1, "features": {}}
    feats, notes = data["features"], []
    for k, d in m["features"].items():
        if k not in feats:
            feats[k] = {"on": d["default"], "default": d["default"]}
            if f.is_file():
                notes.append(f"added feature {k} ({'on' if d['default'] else 'off'})")
    notes += [f"feature {k}: unknown to this kit, ignored" for k in m["unknown"]]
    return json.dumps(data, indent=2) + "\n", notes


def main(argv=None):
    ap = argparse.ArgumentParser(prog="features.py")
    ap.add_argument("--root")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("get")
    g.add_argument("id")
    sub.add_parser("json")
    sub.add_parser("list")
    sub.add_parser("sync")
    st = sub.add_parser("set")
    st.add_argument("id")
    st.add_argument("word")
    a = ap.parse_args(argv)
    root = a.root
    if not root:
        p = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        root = p.stdout.strip() if p.returncode == 0 else "."
    try:
        if a.cmd == "set":
            bad = set_feature(root, a.id, a.word)
            if bad:
                print(bad[1], file=sys.stderr)
                return bad[0]
            print(f"{a.id} is now {a.word} in .shipquick/features.json. That is a protected path: open a PR, the owner merges it.")
            return 0
        if a.cmd == "sync":
            text, notes = sync_text(root)
            sys.stdout.write(text)
            for n in notes:
                print(n, file=sys.stderr)
            return 0
        m = read(root)
    except FeaturesError as e:
        print(f"features.py: {e}", file=sys.stderr)
        return 2
    except Exception as e:   # exit 1 means "off": no crash may ever leak as 1
        print(f"features.py: unexpected {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    if a.cmd == "list":
        for k, v in m["features"].items():
            print(k, "on" if v["on"] else "off")
        return 0
    if a.cmd == "json":
        print(json.dumps(m, indent=2))
        return 0
    row = m["features"].get(a.id)
    if row is None:
        print(f"features.py: unknown feature `{a.id}`; known: {', '.join(m['features'])}", file=sys.stderr)
        return 2
    print("on" if row["on"] else "off")
    return 0 if row["on"] else 1


if __name__ == "__main__":
    sys.exit(main())
