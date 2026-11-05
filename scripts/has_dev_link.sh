#!/usr/bin/env bash
# Exit 0 when the given CLAUDE.md has a filled "Dev link:" line (not empty, not a <placeholder>);
# exit 1 otherwise. The UAT checklist gate (story #120) applies only to a project that has one —
# by project, not by PR title, so a release/chore sync PR cannot turn the gate off for every app
# (story #122, PR #122 review blocker).
# usage: has_dev_link.sh <claude-md-path>
set -u
file="${1:-}"
[ -n "$file" ] || { echo "usage: has_dev_link.sh <claude-md-path>" >&2; exit 2; }
[ -f "$file" ] || exit 1
value="$(grep -E '^- Dev link:' "$file" | head -1 | sed -E 's/^- Dev link:[[:space:]]*//; s/[[:space:]]+$//')"
case "$value" in
  "") exit 1 ;;
  "<"*">"*) exit 1 ;;
  *) exit 0 ;;
esac
