#!/usr/bin/env bash
# One line of feedback from a child project, opened as an issue in ShipQuick (story #111), the moment a gap is hit:
#   knowledge/shipquick_latest/scripts/feedback.sh "<one line>" --why "<why>"
# Opens an issue in satvik-jain-iitd/shipquick_latest, label `feedback`, with the project name (the git remote's
# repo name, or the folder name when there is none), the line and the why. No gh login for the build account:
# prints the text to paste and exits 1, so nothing is lost. Needs git and gh.
set -u
REPO="satvik-jain-iitd/shipquick_latest"
usage() { echo "usage: feedback.sh \"<one line>\" --why \"<why>\"" >&2; exit 2; }
line=""; why=""
while [ $# -gt 0 ]; do
  case "$1" in
    --why) [ -n "${2:-}" ] || usage; why="$2"; shift 2 ;;
    -*) usage ;;
    *) [ -z "$line" ] || usage; line="$1"; shift ;;
  esac
done
[ -n "$line" ] && [ -n "$why" ] || usage

root="$(git rev-parse --show-toplevel 2>/dev/null)" || root="$PWD"
remote="$(git -C "$root" remote get-url origin 2>/dev/null || true)"
if [ -n "$remote" ]; then
  project="$(basename "$remote" .git)"
else
  project="$(basename "$root")"
fi

body="Project: $project

$line

Why: $why"

token="$(gh auth token --user klickbae8yt-star 2>/dev/null)" || {
  {
    echo "No gh login for the build account. Paste this as a \`feedback\` issue in $REPO:"
    echo ""
    echo "$body"
  } >&2
  exit 1
}

GH_TOKEN="$token" gh issue create -R "$REPO" --label feedback --title "feedback: $project: $line" --body "$body"
