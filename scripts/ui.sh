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
err="$(mktemp)"; trap 'rm -f "$err"' EXIT
out="$(cd "$TOOL" && "$BIN" "$@" 2>"$err")"; code=$?
printf '%s\n' "$out"; cat "$err" >&2
[ "$code" -eq 0 ] || exit "$code"
for stream in "$out" "$(cat "$err")"; do   # the CLI may print its error on either stream
  first="$(printf '%s\n' "$stream" | grep -v '^Warning:' | grep -m1 -v '^[[:space:]]*$' || true)"
  case "$first" in Error:*) echo "ui: the CLI reported an error (exit 0 upstream), failing" >&2; exit 1 ;; esac
done
case " $* " in
  *" --json "*)
    printf '%s' "$out" | python3 -c 'import json, sys
try: d = json.load(sys.stdin)
except ValueError: sys.exit(0)
bad = isinstance(d, dict) and ("error" in d or str(d.get("code", "")).startswith("ERR_"))
sys.exit(1 if bad else 0)' || { echo "ui: the --json envelope carries an error, failing" >&2; exit 1; }
    ;;
esac
exit 0
