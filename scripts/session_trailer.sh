#!/usr/bin/env bash
# Story #139 (ADR-011): a prepare-commit-msg hook. Adds `Built-by: <session>` to the commit message,
# once; an amend, rebase or cherry-pick by another session replaces the old name, since it touched
# the commit last. So CI and review_merge.sh can tell which agent session wrote the commit. The session comes
# from $SHIPQUICK_SESSION, else `git config shipquick.session` (role.sh saves it per worktree).
# No session known: writes nothing; CI then names the fix if the project turned sessions on.
# Usage (git calls it): session_trailer.sh <commit-msg-file> [source] [sha]
set -euo pipefail
s="${SHIPQUICK_SESSION:-$(git config --get shipquick.session || true)}"
if [ -z "$s" ]; then   # no session known: drop an old Built-by from the trailer block, so CI names the fix
  python3 - "$1" <<'PY'
import sys
p = sys.argv[1]; lines = open(p).read().split("\n")
# git's own "# ..." comment lines (editor commit, amend) may follow the trailers: skip them to find the trailer block
end = len(lines)
while end and (not lines[end - 1].strip() or lines[end - 1].startswith("#")):
    end -= 1
start = end
while start and lines[start - 1].strip():
    start -= 1
lines[start:end] = [l for l in lines[start:end] if not l.startswith("Built-by:")]
open(p, "w").write("\n".join(lines))
PY
  exit 0
fi
git interpret-trailers --in-place --if-exists replace --trailer "Built-by: $s" "$1"
