"""Test-impact selector (ADR-023). Computes the smallest safe test set for a change.

Usage:
  python3 scripts/test_impact.py --base <sha> --head <sha> [--manifest PATH] [--graph PATH]
                                 [--json OUT] [--dry-run] [--full]
  --full: force full suite regardless of change.
Exit 0 on success (prints plan). Exit 1 on error. Fail-closed: any uncertainty -> full suite.
"""
import argparse
import fnmatch
import json
import os
import subprocess
import sys
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path.cwd()
IMPACT_RELATIONS = {"calls", "indirect_call", "references", "imports", "imports_from",
                    "dynamic_import", "re_exports", "inherits", "extends", "implements",
                    "uses", "mixes_in", "embeds", "defines", "requires"}
GLOBAL_IMPACT_NAMES = {"pyproject.toml", "setup.py", "setup.cfg", "package.json",
                       "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "Cargo.toml",
                       "Cargo.lock", "go.mod", "go.sum"}

# paths that, if changed, force full suite (substring match on path)
RISKY_SUBSTRINGS = [".github/workflows/", "scripts/check_", "scripts/test_impact", "conftest.py",
                    "pytest.ini", "tox.ini", ".coveragerc", "migrations/", "schema", "openapi",
                    "graphql", ".proto", "Dockerfile", "Makefile"]


def run_git(args, cwd=None):
    r = subprocess.run(["git", *args], cwd=cwd or ROOT, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def merge_base(base_hint, head):
    if base_hint:
        return base_hint
    for cand in ("origin/dev", "origin/main", "HEAD~1"):
        rc, out, _ = run_git(["merge-base", cand, head])
        if rc == 0 and out.strip():
            return out.strip()
    # fallback: parent of head
    rc, out, _ = run_git(["rev-parse", f"{head}^"])
    if rc == 0 and out.strip():
        return out.strip()
    return None


def changed_files(base, head):
    """Return list of (status, path) using NUL-safe format."""
    rc, out, err = run_git(["diff", "--name-status", "-z", f"{base}..{head}"])
    if rc != 0:
        return None, err
    items = out.split("\0")
    result = []
    i = 0
    while i < len(items):
        if items[i] == "":
            i += 1
            continue
        status = items[i]
        path = items[i + 1] if i + 1 < len(items) else ""
        # rename/copy: status R100, old path, new path
        if status.startswith("R") or status.startswith("C"):
            old = path
            new = items[i + 2] if i + 2 < len(items) else path
            result.append((status, new, old))
            i += 3
        else:
            result.append((status, path, None))
            i += 2
    return result, None


import re as _re

def _seg_match(seg, pat):
    # fnmatch within a single path segment
    return fnmatch.fnmatch(seg, pat)

def is_glob_match(path, pattern):
    # glob match where ** matches zero or more path segments
    pparts = path.split("/")
    gparts = pattern.split("/")
    from functools import lru_cache
    # recursive
    def match(i, j):
        if j == len(gparts):
            return i == len(pparts)
        if gparts[j] == "**":
            # try consuming 0..remaining segments
            for k in range(i, len(pparts) + 1):
                if match(k, j + 1):
                    return True
            return False
        if i >= len(pparts):
            return False
        if not _seg_match(pparts[i], gparts[j]):
            return False
        return match(i + 1, j + 1)
    return match(0, 0)


def classify(path, manifest):
    """Return (language_id, is_source, is_test, is_global) or None if unclassified."""
    langs = manifest.get("languages", []) or []
    # global impact
    for g in (manifest.get("global_impact") or []):
        if is_glob_match(path, g):
            return None, False, False, True
    # risky substrings
    for sub in RISKY_SUBSTRINGS:
        if sub in path:
            return None, False, False, True
    # test file?
    for lang in langs:
        for tg in (lang.get("tests") or []):
            if is_glob_match(path, tg):
                return lang["id"], False, True, False
    # source file?
    for lang in langs:
        for sg in (lang.get("source") or []):
            if is_glob_match(path, sg):
                # check exclude
                excluded = False
                for ex in (lang.get("exclude") or []):
                    if is_glob_match(path, ex):
                        excluded = True
                        break
                if not excluded:
                    return lang["id"], True, False, False
    return None, False, False, False


def load_manifest(path):
    import yaml
    if not path.exists():
        return None, "manifest missing"
    try:
        data = yaml.safe_load(path.read_text())
    except Exception as e:
        return None, f"manifest unreadable: {e}"
    if data is None:
        data = {}
    # basic validation
    if not isinstance(data, dict):
        return None, "manifest must be a mapping"
    if data.get("version") != 1:
        return None, f"manifest version must be 1, got {data.get('version')!r}"
    return data, None


def load_graph(path):
    if not path.exists():
        return None, "graph missing"
    try:
        data = json.loads(path.read_text())
    except Exception as e:
        return None, f"graph unreadable: {e}"
    if not isinstance(data.get("nodes"), list) or not isinstance(data.get("edges"), list):
        return None, "graph has no nodes/edges"
    return data, None


def graph_fresh(graph, head_sha):
    # check .source_sha sidecar
    sidecar = Path(graph and "x").parent / ".source_sha" if False else None
    return True  # freshness checked separately by check_graph_fresh; here we trust caller


def nodes_for_file(graph, filepath):
    return [n for n in graph["nodes"] if n.get("source_file") == filepath]


def reverse_closure(graph, start_nodes, depth=2):
    # build reverse adjacency
    rev = {}
    for e in graph["edges"]:
        if e.get("relation") not in IMPACT_RELATIONS:
            continue
        rev.setdefault(e.get("target"), []).append(e.get("source"))
    visited = set()
    queue = deque()
    for n in start_nodes:
        nid = n.get("id")
        if nid not in visited:
            visited.add(nid)
            queue.append((nid, 0))
    result_ids = set(n["id"] for n in start_nodes)
    while queue:
        nid, d = queue.popleft()
        if d >= depth:
            continue
        for dep in rev.get(nid, []):
            if dep not in visited:
                visited.add(dep)
                result_ids.add(dep)
                queue.append((dep, d + 1))
    # map ids back to nodes
    by_id = {n["id"]: n for n in graph["nodes"]}
    return [by_id[i] for i in result_ids if i in by_id]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=None)
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--manifest", default=".shipquick/test-impact.yml")
    ap.add_argument("--graph", default="graphify-out/graph.json")
    ap.add_argument("--json", default=None, help="write JSON report to this path")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--full", action="store_true", help="force full suite")
    args = ap.parse_args()

    report = {
        "base": None, "head": args.head, "changed": [], "selected_tests": [],
        "selected_commands": [], "fallback": False, "fallback_reason": None,
        "manifest": args.manifest, "graph": args.graph,
    }

    # resolve head sha
    rc, head_out, _ = run_git(["rev-parse", args.head])
    if rc != 0:
        print(f"cannot resolve head: {args.head}")
        return 1
    head_sha = head_out.strip()
    report["head"] = head_sha

    base_sha = merge_base(args.base, head_sha)
    if base_sha is None:
        report["fallback"] = True
        report["fallback_reason"] = "no merge base found"
        _emit(report, args)
        return 0
    report["base"] = base_sha

    files, diff_err = changed_files(base_sha, head_sha)
    if diff_err:
        report['fallback'] = True
        report['fallback_reason'] = diff_err
        _emit(report, args)
        return 0
    if files is None:
        report["fallback"] = True
        report["fallback_reason"] = "git diff failed"
        _emit(report, args)
        return 0
    report["changed"] = [{"status": s, "path": p} for (s, p, *_) in files]

    # --full forces full suite
    if args.full:
        report["fallback"] = True
        report["fallback_reason"] = "--full requested"
        _emit(report, args)
        return 0

    # load manifest
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = (ROOT / manifest_path).resolve() if not Path(args.manifest).is_absolute() else Path(args.manifest)
    # resolve relative to cwd
    if not manifest_path.exists():
        manifest_path = (Path.cwd() / args.manifest).resolve()
    manifest, merr = load_manifest(manifest_path)
    if merr:
        report["fallback"] = True
        report["fallback_reason"] = merr
        _emit(report, args)
        return 0

    # load graph
    graph_path = Path(args.graph)
    if not graph_path.is_absolute():
        graph_path = (Path.cwd() / args.graph).resolve()
    graph, gerr = load_graph(graph_path)
    if gerr:
        report["fallback"] = True
        report["fallback_reason"] = gerr
        _emit(report, args)
        return 0

    # check freshness sidecar
    sidecar = graph_path.parent / ".source_sha"
    if sidecar.exists():
        stored = sidecar.read_text().strip()
        if stored and stored != head_sha:
            report["fallback"] = True
            report["fallback_reason"] = f"graph stale: stored={stored[:8]}, HEAD={head_sha[:8]}"
            _emit(report, args)
            return 0

    # classify changed files
    fallback_reason = None
    selected = set()
    source_files = []
    has_source_change = False
    for status, path, *rest in files:
        if status == "D":
            # deleted source -> uncertain dependents
            lang, is_src, is_test, is_global = classify(path, manifest)
            if is_src or is_global:
                fallback_reason = f"deleted source with uncertain dependents: {path}"
                break
            continue
        lang, is_src, is_test, is_global = classify(path, manifest)
        if is_global:
            fallback_reason = f"global-impact change: {path}"
            break
        if is_test:
            selected.add(path)
            continue
        if is_src:
            has_source_change = True
            source_files.append(path)
        else:
            # unclassified
            # docs-only allowed to skip
            if not path.endswith((".md", ".txt", ".rst", ".png", ".jpg", ".svg")):
                fallback_reason = f"unclassified path: {path}"
                break

    if fallback_reason:
        report["fallback"] = True
        report["fallback_reason"] = fallback_reason
        _emit(report, args)
        return 0

    # map source files to tests
    # explicit mappings
    mappings = {m["source"]: m["tests"] for m in (manifest.get("mappings") or []) if isinstance(m, dict)}
    langs_by_id = {l["id"]: l for l in (manifest.get("languages") or [])}

    affected_sources = set(source_files)
    # reverse closure via graph
    for sf in source_files:
        nodes = nodes_for_file(graph, sf)
        if not nodes:
            # no graph node -> uncertain
            report["fallback"] = True
            report["fallback_reason"] = f"no graph node for source: {sf}"
            _emit(report, args)
            return 0
        reached = reverse_closure(graph, nodes, depth=2)
        for n in reached:
            sf2 = n.get("source_file")
            if sf2:
                affected_sources.add(sf2)

    # now map affected sources to tests
    for sf in affected_sources:
        if sf in mappings:
            for t in mappings[sf]:
                selected.add(t)
        else:
            # find language whose source glob matches
            for lang in (manifest.get("languages") or []):
                for sg in (lang.get("source") or []):
                    if is_glob_match(sf, sg):
                        # add all tests for that language? No — only if mapping exists.
                        # Without explicit mapping, fall back to full suite for that language.
                        report["fallback"] = True
                        report["fallback_reason"] = f"no test mapping for affected source: {sf}"
                        _emit(report, args)
                        return 0

    # also handle changed test files already added above

    if has_source_change and not selected:
        report["fallback"] = True
        report["fallback_reason"] = "selector returned no tests for a source change"
        _emit(report, args)
        return 0

    report["selected_tests"] = sorted(selected)

    # build commands per language
    cmds = []
    for lang in (manifest.get("languages") or []):
        lang_tests = [t for t in selected if any(is_glob_match(t, tg) for tg in (lang.get("tests") or []))]
        if lang_tests:
            cmd = lang.get("command", "").replace("{tests}", " ".join(lang_tests))
            if cmd.strip():
                cmds.append({"runner": lang.get("runner"), "command": cmd, "tests": lang_tests})
    report["selected_commands"] = cmds

    # full suite commands (for reference)
    report["full_suite_commands"] = manifest.get("full_suite_commands") or {}

    _emit(report, args)
    return 0


def _emit(report, args):
    if args.json:
        out_path = Path(args.json)
        out_path.write_text(json.dumps(report, indent=2))
        print(f"wrote {out_path}")
    # human-readable summary
    print(f"base: {report['base']}")
    print(f"head: {report['head']}")
    print(f"changed: {len(report['changed'])} files")
    if report["fallback"]:
        print(f"FALLBACK (full suite): {report['fallback_reason']}")
        # print full suite commands
        for k, v in (report.get("full_suite_commands") or {}).items():
            print(f"  full[{k}]: {v}")
    else:
        print(f"selected tests: {len(report['selected_tests'])}")
        for t in report["selected_tests"]:
            print(f"  - {t}")
        for c in report["selected_commands"]:
            print(f"  cmd[{c['runner']}]: {c['command']}")


if __name__ == "__main__":
    sys.exit(main())
