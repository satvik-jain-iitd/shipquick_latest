#!/usr/bin/env bash
# Story #183 (S3, ADR-012): `ui` -- run Meta's Astryx CLI as shipped (pinned in ui/tool/) with the kit's own
# integration (ui/integration/: native topics plus the agent-block text). One-time setup: `npm ci --ignore-scripts`
# in ui/tool/. The CLI prints some errors with exit 0 (spike, 9 Nov 2026), so this wrapper fails on them itself:
# a non-zero exit, a first line "Error: ...", or a --json envelope with an "error" or an ERR_* code.
# Usage: bash scripts/ui.sh <astryx args>   e.g. bash scripts/ui.sh docs android-button --dense
set -uo pipefail
KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOL="$KIT/ui/tool"
BIN="${UI_ASTRYX_BIN:-$TOOL/node_modules/.bin/astryx}"   # UI_ASTRYX_BIN: a stub, for tests only
[ -x "$BIN" ] || { echo "ui: the CLI is not installed. Run once: (cd \"$TOOL\" && npm ci --ignore-scripts)" >&2; exit 2; }
mkdir -p "$TOOL/node_modules"
ln -sfn ../../integration "$TOOL/node_modules/shipquick-ui"   # npm ci removes it; the config names it
outf="$(mktemp)"; errf="$(mktemp)"; trap 'rm -f "$outf" "$errf"' EXIT
(cd "$TOOL" && "$BIN" "$@") >"$outf" 2>"$errf"; code=$?
cat "$outf"; cat "$errf" >&2
[ "$code" -eq 0 ] || exit "$code"
json=0
for a in "$@"; do case "$a" in --json|--json=*) json=1 ;; esac; done
python3 - "$json" "$outf" "$errf" <<'PY'
import json, re, sys
mode, outf, errf = sys.argv[1] == "1", sys.argv[2], sys.argv[3]
out, err = open(outf).read(), open(errf).read()
# an error line anywhere, on either stream, in any case: "Error: ...", "error: ...", "ERROR ..."
said_error = re.compile(r"^\s*error\s*:", re.I | re.M)   # Error: / error: / ERROR:
shouted = re.compile(r"^\s*ERROR\b", re.M)                 # ERROR boom
if any(said_error.search(s) or shouted.search(s) for s in (out, err)):
    sys.exit("ui: the CLI reported an error (it exits 0 for some), failing")
if mode:
    try:
        data = json.loads(out)
    except ValueError:
        sys.exit("ui: --json output is not JSON, failing")
    def walk(v):
        if isinstance(v, dict):
            if v.get("error") is not None or v.get("ok") is False or str(v.get("code", "")).startswith("ERR_"):
                return True
            return any(walk(x) for x in v.values())
        return isinstance(v, list) and any(walk(x) for x in v)
    if walk(data):
        sys.exit("ui: the --json envelope carries an error, failing")
PY
