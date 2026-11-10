"""Codebase map for the SessionStart hook (story #314, A9).

Python twin of ponytail hooks/ponytail-map.js (MIT, DietrichGebert/ponytail, commit 96608e0, read in
the study clone on 10 Nov 2026). It lists the top-level functions and classes of the source files,
one line per folder, inside a character budget. No model, no dependency. Tests, vendored and hidden
folders are skipped; scripts/ and plugin/ are listed first.

shortcut: regex, not a parser; misses nested or dynamic definitions. Upgrade: a tree-sitter index
when the map must be exact.
"""
import os
import re
import subprocess
from pathlib import Path

BUDGET = 2000            # characters for the whole map, header and footer included
RESERVE = 40             # room kept for the "(N more folders not listed)" footer
MAX_FILES = 4000
MAX_READ = 65536         # characters read per file, the top of a file says what it holds
HEADER = "Codebase map (what already exists; reuse it, read a file only when you need its details):"
PRIORITY = ("scripts", "plugin")
SKIP_DIRS = {"tests", "test", "__tests__", "node_modules", "knowledge", "vendor", "dist", "build",
             "venv", "__pycache__", "coverage"}
SKIP_FILE = re.compile(r"(^|/)(test_[^/]*|[^/]*(_test|\.test|\.spec)\.[A-Za-z]+)$")

_PY = re.compile(r"^(?:async\s+)?(?:def|class)\s+([A-Za-z]\w*)", re.M)
_JS = re.compile(r"^export\s+(?:default\s+)?(?:async\s+)?(?:function\*?|class|const|let|var|interface|type|enum)"
                 r"\s+([A-Za-z_$][\w$]*)", re.M)
_SH = re.compile(r"^(?:function\s+)?([A-Za-z]\w*)\s*\(\)", re.M)
_SWIFT = re.compile(r"^(?:(?:public|open|internal|final)\s+)*(?:class|struct|enum|protocol|func|actor)\s+"
                    r"([A-Za-z_]\w*)", re.M)
_KT = re.compile(r"^(?:(?:public|private|internal|protected|data|sealed|abstract|open)\s+)*"
                 r"(?:fun|class|object|interface)\s+(?:<[^>]*>\s*)?(?:\w+\.)?([A-Za-z_]\w*)", re.M)
PATTERNS = {".py": _PY, ".js": _JS, ".mjs": _JS, ".cjs": _JS, ".jsx": _JS, ".ts": _JS, ".tsx": _JS,
            ".sh": _SH, ".swift": _SWIFT, ".kt": _KT}


def _tracked(root):
    """Files git knows, so .gitignore is respected. A folder outside git gives none, and the walk is used."""
    try:
        out = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True, timeout=3).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    return [f for f in out.split("\n") if f][: MAX_FILES * 5]


def _walk(root):
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in SKIP_DIRS]
        for name in filenames:
            found.append(os.path.relpath(os.path.join(dirpath, name), root))
        if len(found) > MAX_FILES * 5:
            break
    return found


def _wanted(rel):
    parts = rel.split("/")
    if any(p.startswith(".") or p in SKIP_DIRS for p in parts[:-1]):
        return False
    return Path(rel).suffix in PATTERNS and not SKIP_FILE.search(rel)


def _names(text, ext):
    names = []
    for m in PATTERNS[ext].finditer(text):
        name = m.group(1)
        if not name.startswith("_") and name not in names:
            names.append(name)
    return names


def build_map(root, budget=BUDGET):
    """The map as one string, or "" when there is nothing to list. Never longer than budget."""
    root = str(root)
    files = [f for f in (_tracked(root) or _walk(root)) if _wanted(f)][:MAX_FILES]
    per_dir = {}
    for rel in files:
        try:
            with open(os.path.join(root, rel), encoding="utf-8", errors="ignore") as fh:
                text = fh.read(MAX_READ)
        except OSError:
            continue
        names = _names(text, Path(rel).suffix)
        if names:
            per_dir.setdefault(os.path.dirname(rel) or ".", []).append(names)

    def order(d):
        top = d.split("/")[0]
        rank = PRIORITY.index(top) if top in PRIORITY else len(PRIORITY)
        return (rank, d)

    used = len(HEADER) + 1
    lines, skipped = [], 0
    for d in sorted(per_dir, key=order):
        per_file = per_dir[d]
        # One name per file in a big folder (a UI kit); the first three in a small one.
        take = 1 if len(per_file) > 8 else 3
        names = list(dict.fromkeys(n for file_names in per_file for n in file_names[:take]))
        shown = ", ".join(names[:30]) + (", ..." if len(names) > 30 else "")
        line = f"{d}/: {shown}"
        if used + len(line) + 1 > budget - RESERVE:
            skipped += 1
            continue
        lines.append(line)
        used += len(line) + 1
    if not lines:
        return ""
    text = HEADER + "\n" + "\n".join(lines)
    if skipped:
        text += f"\n({skipped} more folders not listed)"
    return text
