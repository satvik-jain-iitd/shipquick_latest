#!/usr/bin/env bash
# The ShipQuick inbox: a child project's feedback tells the whole story (story #118):
#   knowledge/shipquick_latest/scripts/feedback.sh --title "<t>" --body-file <f> [--new]
# <f> must hold all nine sections below, each non-empty (docs/templates/feedback.md is the template);
# section 5 (Root cause) needs at least three "Why" lines (a five-whys chain):
#   ## Situation / ## Expected vs seen / ## Steps to reproduce / ## Impact / ## Root cause /
#   ## Why ShipQuick did not catch it / ## How big teams avoid it / ## Generic fix for ShipQuick / ## Stop the repeat
# A missing, empty, or (for Root cause) too-short section exits 2, naming it; nothing opens.
# The script fills the header itself (project, ShipQuick commit, date) — the caller never writes it.
# An open `feedback` issue with a similar title gets a comment instead of a new issue; --new forces a new one.
# Opens/comments in $SHIPQUICK_REPO (default satvik-jain-iitd/shipquick_latest), label `feedback`, using
# the build account's token ($SHIPQUICK_BUILD_USER, default klickbae8yt-star). No gh login: prints the
# title and the full body and exits 1, nothing lost. Needs git, gh and jq.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="${SHIPQUICK_REPO:-satvik-jain-iitd/shipquick_latest}"
BUILD_USER="${SHIPQUICK_BUILD_USER:-klickbae8yt-star}"
SECTIONS=("Situation" "Expected vs seen" "Steps to reproduce" "Impact" "Root cause" "Why ShipQuick did not catch it" "How big teams avoid it" "Generic fix for ShipQuick" "Stop the repeat")
usage() { echo 'usage: feedback.sh --title "<t>" --body-file <f> [--new]' >&2; exit 2; }
title=""; file=""; force_new=""
while [ $# -gt 0 ]; do
  case "$1" in
    --title) [ -n "${2:-}" ] || usage; title="$2"; shift 2 ;;
    --body-file) [ -n "${2:-}" ] || usage; file="$2"; shift 2 ;;
    --new) force_new=1; shift ;;
    *) usage ;;
  esac
done
[ -n "$title" ] && [ -n "$file" ] || usage
[ -f "$file" ] || { echo "feedback.sh: no such file: $file" >&2; exit 2; }

section_text() {
  awk -v h="## $1" 'index($0, h) == 1 {f = 1; next} /^## / {f = 0} f' "$file" | sed '/^[[:space:]]*$/d'
}

for s in "${SECTIONS[@]}"; do
  text="$(section_text "$s")"
  [ -n "$text" ] || { echo "feedback.sh: missing or empty section: $s" >&2; exit 2; }
  if [ "$s" = "Root cause" ]; then
    whys=$(printf '%s\n' "$text" | grep -ci '^Why')
    [ "$whys" -ge 3 ] || { echo "feedback.sh: missing or empty section: Root cause (needs at least three \"Why\" lines, a five-whys chain; found $whys)" >&2; exit 2; }
  fi
done

body="$(cat "$file")"
root="$(git rev-parse --show-toplevel 2>/dev/null)" || root="$PWD"
remote="$(git -C "$root" remote get-url origin 2>/dev/null || true)"
if [ -n "$remote" ]; then
  project="$(basename "$remote" .git)"
else
  project="$(basename "$root")"
fi
sq_commit="$(git -C "$HERE/.." rev-parse HEAD 2>/dev/null || echo unknown)"
date_utc="$(date -u +%Y-%m-%d)"
session_line=""
[ -n "${SHIPQUICK_SESSION_URL:-}" ] && session_line="
- Session: $SHIPQUICK_SESSION_URL"

header="## Header
- Project: $project
- ShipQuick commit: ${sq_commit:0:7}
- Date: $date_utc$session_line"

full_body="$header

$body"

token="$(gh auth token --user "$BUILD_USER" 2>/dev/null)" || {
  {
    echo "No gh login for $BUILD_USER. Paste this as a \`feedback\` issue in $REPO:"
    echo ""
    echo "Title: $title"
    echo ""
    echo "$full_body"
  } >&2
  exit 1
}

dupe=""
if [ -z "$force_new" ]; then
  open_titles="$(GH_TOKEN="$token" gh issue list -R "$REPO" --label feedback --state open --json number,title 2>/dev/null \
    | jq -r '.[] | "\(.number)\t\(.title)"' 2>/dev/null || true)"
  low_title="$(printf '%s' "$title" | tr '[:upper:]' '[:lower:]')"
  while IFS=$'\t' read -r num etitle; do
    [ -n "$num" ] || continue
    low_e="$(printf '%s' "$etitle" | tr '[:upper:]' '[:lower:]')"
    case "$low_e" in *"$low_title"*) dupe="$num" ;; esac
    [ -n "$dupe" ] && break
    case "$low_title" in *"$low_e"*) dupe="$num" ;; esac
    [ -n "$dupe" ] && break
  done <<<"$open_titles"
fi

if [ -n "$dupe" ]; then
  echo "similar open issue #$dupe, commenting there instead"
  GH_TOKEN="$token" gh issue comment "$dupe" -R "$REPO" --body "$full_body"
  exit 0
fi

GH_TOKEN="$token" gh issue create -R "$REPO" --label feedback --title "feedback: $project: $title" --body "$full_body"
