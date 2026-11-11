#!/usr/bin/env python3
"""Story #190 (S12): an MCP server over the component registries, and ui/llms.txt. Stdlib only.

Server `shipquick_ui_mcp`, stdio, newline-delimited JSON-RPC 2.0 (MCP tools only). Two read-only tools:
  shipquick_ui_search_components  ranked search over ui/components/*/<Name>.doc.mjs and ui/registry.json, paginated
  shipquick_ui_get_component      one component's doc, contract and registry rows
Data: the same files scripts/check_ui_docs.py guards; nothing is cached on disk. The Astryx CLI's `search`
(scripts/ui.sh) needs Node and ui/tool/node_modules; this server needs only python3.

Usage: python3 scripts/ui_mcp.py                  run the server (an MCP client starts it)
       python3 scripts/ui_mcp.py llms             write ui/llms.txt from the docs and the registry
       python3 scripts/ui_mcp.py llms --check     exit 1 when ui/llms.txt is missing or stale
Client config: {"command": "python3", "args": ["<kit>/scripts/ui_mcp.py"]}
"""
import argparse
import difflib
import functools
import json
import re
import sys
from pathlib import Path

from check_ui_docs import read_doc

KIT = Path(__file__).resolve().parent.parent
UI = KIT / "ui"
COMPONENTS, REGISTRY, LLMS = UI / "components", UI / "registry.json", UI / "llms.txt"
NAME, SEARCH, GET = "shipquick_ui_mcp", "shipquick_ui_search_components", "shipquick_ui_get_component"
PLATFORMS = ("android", "ios", "web")
VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")
MAX_LIMIT = 50


@functools.cache
def load():
    """Every component doc with its contract, plus the custom rows of ui/registry.json."""
    docs = {}
    for d in sorted(p for p in COMPONENTS.iterdir() if p.is_dir()):
        doc_path, contract_path = d / f"{d.name}.doc.mjs", d / f"{d.name}.contract.json"
        if doc_path.exists():
            doc = read_doc(doc_path)
            contract = json.loads(contract_path.read_text(encoding="utf-8")) if contract_path.exists() else None
            docs[doc["name"]] = {"doc": doc, "contract": contract, "path": f"components/{d.name}/{doc_path.name}"}
    rows = json.loads(REGISTRY.read_text(encoding="utf-8")).get("components", []) if REGISTRY.exists() else []
    return docs, rows


def platforms_of(d):
    """Platforms a doc covers: a named base type, or (catch-all iOS docs name none) a platform API list."""
    return [p for p in PLATFORMS if (d.get("platforms") or {}).get(p) or (d.get("platformApi") or {}).get(p)]


def _entries():
    docs, rows = load()
    for name, c in docs.items():
        d = c["doc"]
        api = [x.get("name", "") for p in (d.get("platformApi") or {}).values() if p
               for x in (p.get("variants") or []) + (p.get("supporting") or [])]
        yield {"name": name, "displayName": d.get("displayName", name), "category": d.get("category", ""),
               "platforms": platforms_of(d),
               "description": (d.get("usage") or {}).get("description", ""), "source": "doc",
               "_keywords": [k.lower() for k in d.get("keywords", [])],
               "_more": " ".join([d.get("group", ""), d.get("category", "")] + api).lower()}
    for r in rows:
        yield {"name": r.get("name", ""), "displayName": r.get("name", ""), "category": "Custom",
               "platforms": [r["platform"]] if r.get("platform") else [],
               "description": f"Custom component built on {r.get('base', '?')}.", "source": "registry",
               "_keywords": [], "_more": str(r.get("base", "")).lower()}


def _score(e, query, words):
    # ponytail: token overlap with fixed weights; add BM25 when the library outgrows a few hundred docs
    name, display = e["name"].lower(), e["displayName"].lower()
    score = 100 if query.replace(" ", "") in (name, display.replace(" ", "")) else 0
    for w in words:
        score += (50 if w == name else 20 if w in name or w in display else 0)
        score += 10 if any(w in k for k in e["_keywords"]) else 0
        score += 3 if w in e["_more"] else 0
        score += 2 if w in e["description"].lower() else 0
    return score


def search(query="", platform=None, limit=10, offset=0):
    """Ranked matches, best first, then by name. An empty query lists everything."""
    query = query.strip().lower()
    words = re.findall(r"\w+", query)
    hits = []
    for e in _entries():
        if platform and platform not in e["platforms"]:
            continue
        s = _score(e, query, words) if words else 1
        if s:
            hits.append({k: v for k, v in e.items() if not k.startswith("_")} | {"score": s})
    hits.sort(key=lambda h: (-h["score"], h["name"].lower()))
    page = hits[offset:offset + limit]
    more = offset + len(page) < len(hits)
    return {"total": len(hits), "count": len(page), "offset": offset, "items": page,
            "has_more": more, "next_offset": offset + len(page) if more else None}


def get(name):
    """One component by name, any case. LookupError names the closest names and the next step."""
    docs, rows = load()
    names = {n.lower(): n for n in docs} | {r.get("name", "").lower(): r.get("name", "") for r in rows}
    key = names.get(name.strip().lower())
    if not key:
        close = difflib.get_close_matches(name.strip().lower(), names, n=3, cutoff=0.6)
        guess = f" Did you mean: {', '.join(names[c] for c in close)}?" if close else ""
        raise LookupError(f"No component named {name!r}.{guess} Call {SEARCH} with a word for what the control does "
                          f"(for example 'date' or 'toggle') to find the exact name.")
    c = docs.get(key, {})
    return {"name": key, "doc": c.get("doc"), "contract": c.get("contract"), "path": c.get("path"),
            "registry": [r for r in rows if r.get("name", "").lower() == key.lower()]}


# ---- MCP ----

ANNOTATIONS = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
TOOLS = [
    {"name": SEARCH, "title": "Search UI components", "annotations": ANNOTATIONS | {"title": "Search UI components"},
     "description": "Find library components (Android Compose Material 3, iOS SwiftUI, web) by words for what the control "
                    "does. Returns ranked matches with name, platforms and a one-line description; page with offset. "
                    f"Then call {GET} with a name for its props and rules. Build only from these components.",
     "inputSchema": {"type": "object", "additionalProperties": False, "properties": {
         "query": {"type": "string", "maxLength": 200,
                   "description": "Words for the control, e.g. 'button', 'date picker', 'bottom sheet'. Empty lists all."},
         "platform": {"type": "string", "enum": list(PLATFORMS),
                      "description": "Keep only components available on this platform. Omit for all."},
         "limit": {"type": "integer", "minimum": 1, "maximum": MAX_LIMIT, "default": 10,
                   "description": f"Results per page, 1 to {MAX_LIMIT}. Default 10."},
         "offset": {"type": "integer", "minimum": 0, "default": 0,
                    "description": "Results to skip; pass the previous reply's next_offset for the next page."}}}},
    {"name": GET, "title": "Get a UI component", "annotations": ANNOTATIONS | {"title": "Get a UI component"},
     "description": "Get one library component by exact name (case does not matter): the full doc (usage, best practices, "
                    "accessibility, props per platform, platform API list), its prop contract, and any custom registry rows. "
                    f"Use {SEARCH} first when you do not know the name.",
     "inputSchema": {"type": "object", "additionalProperties": False, "required": ["name"], "properties": {
         "name": {"type": "string", "minLength": 1, "description": "Component name from a search result, e.g. 'Button'."}}}},
]


def _args_error(name, a):
    """A plain sentence naming the bad field and the fix, or None."""
    if name == SEARCH:
        if not isinstance(a.get("query", ""), str) or len(a.get("query", "")) > 200:
            return "query must be a string of at most 200 characters."
        if a.get("platform") not in (None, *PLATFORMS):
            return f"platform must be one of {', '.join(PLATFORMS)}, or left out."
        lim, off = a.get("limit", 10), a.get("offset", 0)
        if not isinstance(lim, int) or isinstance(lim, bool) or not 1 <= lim <= MAX_LIMIT:
            return f"limit must be a whole number from 1 to {MAX_LIMIT}; page with offset for more."
        if not isinstance(off, int) or isinstance(off, bool) or off < 0:
            return "offset must be a whole number, 0 or more (use next_offset from the last reply)."
    elif not isinstance(a.get("name"), str) or not a["name"].strip():
        return f"name is required, e.g. 'Button'. Call {SEARCH} to find one."
    return None


def _result(data=None, error=None):
    if error:
        return {"content": [{"type": "text", "text": error}], "isError": True}
    return {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}], "structuredContent": data}


def handle(msg):
    """One JSON-RPC message in, one reply out (None for a notification)."""
    mid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or {}
    if mid is None:
        return None
    ok = lambda r: {"jsonrpc": "2.0", "id": mid, "result": r}
    fail = lambda code, m: {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": m}}
    if method == "initialize":
        v = params.get("protocolVersion")
        return ok({"protocolVersion": v if v in VERSIONS else VERSIONS[0], "capabilities": {"tools": {}},
                   "serverInfo": {"name": NAME, "version": "1.0.0"},
                   "instructions": f"Before you write any UI, call {SEARCH}, then {GET}. Build only from library components."})
    if method == "ping":
        return ok({})
    if method == "tools/list":
        return ok({"tools": TOOLS})
    if method == "tools/call":
        name, a = params.get("name"), params.get("arguments") or {}
        if name not in (SEARCH, GET):
            return fail(-32602, f"Unknown tool {name!r}. Tools: {SEARCH}, {GET}.")
        err = _args_error(name, a)
        if err:
            return ok(_result(error=err))
        try:
            data = search(a.get("query", ""), a.get("platform"), a.get("limit", 10), a.get("offset", 0)) if name == SEARCH \
                else get(a["name"])
        except LookupError as e:
            return ok(_result(error=str(e)))
        return ok(_result(data))
    return fail(-32601, f"Method {method!r} not found. This server has initialize, ping, tools/list and tools/call.")


def serve(stdin=sys.stdin, stdout=sys.stdout):
    for line in stdin:
        if not line.strip():
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error: one JSON object per line."}}
        else:
            reply = handle(msg) if isinstance(msg, dict) else None
        if reply:
            stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
            stdout.flush()


# ---- llms.txt ----

def llms_text():
    docs, rows = load()
    out = ["# ShipQuick UI component library", "",
           "> Library components for Android (Compose Material 3), iOS (SwiftUI) and web. Build every screen from these "
           "components only; read a component's doc before you use it. Search and get them through the MCP server "
           f"`{NAME}` (`python3 scripts/ui_mcp.py`). Generated by `python3 scripts/ui_mcp.py llms`; do not edit.", ""]
    by_cat = {}
    for name, c in docs.items():
        by_cat.setdefault(c["doc"].get("category") or "Other", []).append((name, c))
    for cat in sorted(by_cat):
        out += [f"## {cat}", ""]
        for name, c in sorted(by_cat[cat], key=lambda x: x[0].lower()):
            d = c["doc"]
            plats = ", ".join(platforms_of(d))
            desc = " ".join((d.get("usage") or {}).get("description", "").split())
            out.append(f"- [{name}]({c['path']}): {desc} ({plats})")
        out.append("")
    out += ["## Custom components", ""]
    out += [f"- {r.get('name')} ({r.get('platform')}, on {r.get('base')}){': ' + r['doc'] if r.get('doc') else ''}"
            for r in sorted(rows, key=lambda r: (str(r.get("name")), str(r.get("platform"))))] or ["- None yet."]
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")
    lp = sub.add_parser("llms", help="write or check ui/llms.txt")
    lp.add_argument("--check", action="store_true", help="exit 1 when the file is missing or stale")
    lp.add_argument("--out", type=Path, default=LLMS, help="the file to write or check")
    a = ap.parse_args(argv)
    if a.cmd != "llms":
        serve()
        return 0
    text = llms_text()
    if a.check:
        if not a.out.exists() or a.out.read_text(encoding="utf-8") != text:
            print(f"STALE {a.out}: the component docs or the registry changed. Run: python3 scripts/ui_mcp.py llms")
            return 1
        print(f"ok {a.out}")
        return 0
    a.out.write_text(text, encoding="utf-8")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
