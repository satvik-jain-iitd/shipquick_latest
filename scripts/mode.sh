#!/usr/bin/env bash
# Where the owner's choice of mode is kept (story #67, docs/MODES.md). One word in $(git rev-parse --git-common-dir)/shipquick-mode:
# every worktree of the repo shares it, and git does not track it.
#   mode.sh get          prints manual, semi or auto. Exit 3 with "ask the owner" when it is not set.
#   mode.sh set <mode>   manual | semi | auto
# Agents only run `get`. Only the owner runs `set`, by typing `! bash scripts/mode.sh set <word>` himself: a `!` line is his own shell input,
# never an agent's tool call. If an agent could set auto, it could then merge through review_merge.sh and the gate would mean nothing.
set -u
common=$(git rev-parse --git-common-dir 2>/dev/null) || { echo "mode.sh: not inside a git repository" >&2; exit 2; }
file="$common/shipquick-mode"
case "${1:-}" in
  get)
    mode=$(tr -d '[:space:]' < "$file" 2>/dev/null)
    case "$mode" in
      manual|semi|auto) echo "$mode" ;;
      *) echo "mode is not set: ask the owner (manual, semi or auto), then run: mode.sh set <mode>" >&2; exit 3 ;;
    esac ;;
  set)
    case "${2:-}" in
      manual|semi|auto) echo "$2" > "$file"; echo "mode set to $2" ;;
      *) echo "usage: mode.sh set manual|semi|auto" >&2; exit 2 ;;
    esac ;;
  *) echo "usage: mode.sh get | set <manual|semi|auto>" >&2; exit 2 ;;
esac
