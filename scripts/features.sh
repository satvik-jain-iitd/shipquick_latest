#!/usr/bin/env bash
# Story #419 (F2, epic #86): the owner's front door to .shipquick/features.json, like mode.sh. ADR-016.
#   features.sh get            every feature with on or off
#   features.sh get <id>       one feature: prints on (exit 0) or off (exit 1); unknown id exits 2
#   features.sh set <id> on|off  rewrites .shipquick/features.json, then says: open a PR, the owner merges it.
#                              Refuses `adoption` and `gate` (locked: they guard every other feature).
# Agents only run `get`. The file is a protected path, so an agent's own write is harmless: nothing reaches
# the base branch without the owner's merge. The owner types the change himself, for example:
#   ! bash scripts/features.sh set roadmap off
# This script only calls scripts/features.py (one parser, one writer).
set -u
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
py="$here/features.py"
usage() { echo "usage: features.sh get [<id>] | features.sh set <id> on|off" >&2; exit 2; }
case "${1:-}" in
  get)  if [ $# -eq 1 ]; then exec python3 "$py" list; else exec python3 "$py" get "$2"; fi ;;
  set)  [ $# -eq 3 ] || usage; exec python3 "$py" set "$2" "$3" ;;
  *)    usage ;;
esac
