#!/usr/bin/env bash
# Story #139 (ADR-011): a prepare-commit-msg hook. Adds `Built-by: <session>` to the commit message,
# once; an amend, rebase or cherry-pick by another session replaces the old name, since it touched
# the commit last. So CI and review_merge.sh can tell which agent session wrote the commit. The session comes
# from $SHIPQUICK_SESSION, else `git config shipquick.session` (role.sh saves it per worktree).
# No session known: writes nothing; CI then names the fix if the project turned sessions on.
# Usage (git calls it): session_trailer.sh <commit-msg-file> [source] [sha]
set -euo pipefail
s="${SHIPQUICK_SESSION:-$(git config --get shipquick.session || true)}"
[ -n "$s" ] || exit 0
git interpret-trailers --in-place --if-exists replace --trailer "Built-by: $s" "$1"
