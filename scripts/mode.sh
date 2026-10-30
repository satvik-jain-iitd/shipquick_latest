#!/usr/bin/env bash
# Where the owner's choice of mode is kept (story #67, #140, docs/MODES.md). `get` prefers the
# tracked, protected `.shipquick/mode` file in the repo (one word) when it exists: changing it needs
# a PR touching a protected path (scripts/protected_paths.txt), so no agent's Bash call can flip it
# -- only the owner's own merge can. With no `.shipquick/mode` yet, it falls back to the old
# untracked $(git rev-parse --git-common-dir)/shipquick-mode (every worktree shares it, git does not
# track it): the switch to the new file is live the instant the owner merges one in, nothing else
# has to change first.
#   mode.sh get          prints manual, semi or auto. Exit 3 with "ask the owner" when it is not set.
#   mode.sh set <mode>   manual | semi | auto. Refuses once .shipquick/mode exists in the working
#                        tree: edit that file and open a PR instead (the owner merges it). Refuses
#                        `auto` when .shipquick/roles.yml lists one account as the only coder and the
#                        only reviewer: review_merge.sh would then never find an approver who is not
#                        the author, so auto could never merge anything.
# Agents only run `get`. Before .shipquick/mode exists, only the owner runs `set`, by typing
# `! bash scripts/mode.sh set <word>` himself: a `!` line is his own shell input, never an agent's
# tool call. If an agent could set auto, it could then merge through review_merge.sh and the gate
# would mean nothing.
set -u
top=$(git rev-parse --show-toplevel 2>/dev/null) || { echo "mode.sh: not inside a git repository" >&2; exit 2; }
common=$(git rev-parse --git-common-dir 2>/dev/null) || { echo "mode.sh: not inside a git repository" >&2; exit 2; }
tracked="$top/.shipquick/mode"
file="$common/shipquick-mode"
case "${1:-}" in
  get)
    if [ -f "$tracked" ]; then
      mode=$({ tr -d '[:space:]' < "$tracked"; } 2>/dev/null)
    else
      mode=$({ tr -d '[:space:]' < "$file"; } 2>/dev/null)
    fi
    case "$mode" in
      manual|semi|auto) echo "$mode" ;;
      *) echo "mode is not set: ask the owner (manual, semi or auto), then run: mode.sh set <mode>" >&2; exit 3 ;;
    esac ;;
  set)
    if [ -f "$tracked" ]; then
      echo "mode.sh: .shipquick/mode exists and is a protected path (story #131) -- edit it and open a PR, the owner merges it; mode.sh set no longer writes it" >&2
      exit 1
    fi
    case "${2:-}" in
      manual|semi) echo "$2" > "$file"; echo "mode set to $2" ;;
      auto)
        roles="$top/.shipquick/roles.yml"
        here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        if [ -f "$roles" ]; then
          coders=$(python3 "$here/roles.py" get coder --file "$roles" 2>/dev/null)
          reviewers=$(python3 "$here/roles.py" get reviewer --file "$roles" 2>/dev/null)
          if [ -n "$coders" ] && [ "$coders" = "$reviewers" ] && [ "${coders#*,}" = "$coders" ]; then
            echo "mode.sh: .shipquick/roles.yml lists one account ($coders) as both coder and reviewer (story #140) -- auto can never pass the approver-is-not-the-author check, refusing; use manual or semi" >&2
            exit 1
          fi
        fi
        echo "$2" > "$file"; echo "mode set to $2" ;;
      *) echo "usage: mode.sh set manual|semi|auto" >&2; exit 2 ;;
    esac ;;
  *) echo "usage: mode.sh get | set <manual|semi|auto>" >&2; exit 2 ;;
esac
