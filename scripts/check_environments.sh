#!/usr/bin/env bash
# A child project's own CI check: `Dev link:` and `Production link:` in its CLAUDE.md must both be
# filled once the project is past milestone D0 (story #120). At D0 nothing is deployed yet, so it
# always passes. A placeholder value (`<...>`) counts as empty.
# usage: check_environments.sh --claude-md <path> --milestone <D0..D6>
set -u
usage() { echo "usage: check_environments.sh --claude-md <path> --milestone <D0..D6>" >&2; exit 2; }
file=""; milestone=""
while [ $# -gt 0 ]; do
  case "$1" in
    --claude-md) [ -n "${2:-}" ] || usage; file="$2"; shift 2 ;;
    --milestone) [ -n "${2:-}" ] || usage; milestone="$2"; shift 2 ;;
    *) usage ;;
  esac
done
[ -n "$file" ] && [ -n "$milestone" ] || usage
case "$milestone" in D0|D1|D2|D3|D4|D5|D6) ;; *) usage ;; esac
[ -f "$file" ] || { echo "check_environments.sh: no such file: $file" >&2; exit 1; }
[ "$milestone" = D0 ] && exit 0

link_value() {   # link_value <label> — text after "- <label>:" on its own line, trimmed
  grep -E "^- $1:" "$file" | head -1 | sed -E "s/^- $1:[[:space:]]*//; s/[[:space:]]+\$//"
}

bad=""
for label in "Dev link" "Production link"; do
  v="$(link_value "$label")"
  case "$v" in ""|"<"*">"*) bad="$bad $label" ;; esac
done
[ -z "$bad" ] || { echo "check_environments.sh: empty or placeholder:$bad (past $milestone, both must be filled)" >&2; exit 1; }
echo "environments OK"
