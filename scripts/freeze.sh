#!/usr/bin/env bash
# Story #126 (GoServe feedback #126): a release freeze is a mechanism, not a sentence.
#   freeze.sh on "<reason>" --until <date>   # writes .shipquick/freeze on main through a PR
#   freeze.sh off                             # removes it through a PR -- .shipquick/freeze is a
#                                              #   protected path (story #131), so the owner merges this PR too
#   freeze.sh status [--repo <owner/repo>] [--ref <branch>]   # prints what check_freeze.py decides;
#                                              #   no --repo reads origin/main (story #140 bug #142),
#                                              #   never the local checkout
# on/off never touch the caller's own checkout or branch (bug #142): the write happens in a scratch
# `git worktree`, removed on exit via a trap, and a branch is only ever created once the command has
# already decided there is work to do (so a refusal -- not clean, bad date, nothing to lift -- leaves
# no stray chore/freeze-* branch). push and the PR use the build account ($SHIPQUICK_BUILD_USER,
# default: this repo's first coder account from .shipquick/roles.yml; with neither set, on/off refuse
# and say to run adopt.sh -- story #140, no literal account fallback). FREEZE_NO_PUSH=1 stops right
# after the local commit and keeps the scratch branch (nothing was pushed, so it is the only record
# of what would have happened) -- used by tests, no network, no PR. A freeze does not lift itself
# past --until (story #126 scenario 4): only `freeze.sh off`, or a renewed `on`, changes it. Needs git, gh.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
usage() { echo 'usage: freeze.sh on "<reason>" --until <date> | freeze.sh off | freeze.sh status [--repo owner/repo] [--ref branch]' >&2; exit 2; }

valid_date() { date -d "$1" >/dev/null 2>&1 || date -j -f "%Y-%m-%d" "$1" >/dev/null 2>&1; }

# make_worktree <branch-prefix>: creates a scratch worktree off origin/main, sets $wt and $branch,
# and arranges for both to be cleaned up on exit (the branch is kept under FREEZE_NO_PUSH=1, for tests).
make_worktree() {
  branch="$1-$(date +%s)"
  wt="$(mktemp -d)"
  trap 'git worktree remove --force "$wt" 2>/dev/null; [ "${FREEZE_NO_PUSH:-0}" = 1 ] || git branch -D "$branch" 2>/dev/null; true' EXIT
  git worktree add -q -B "$branch" "$wt" origin/main
}

# resolve_build_user: sets $BUILD_USER from $SHIPQUICK_BUILD_USER, else this repo's first coder
# account in .shipquick/roles.yml. Refuses (exit 1, no literal fallback -- story #140) before any
# worktree or branch is created, so a missing account leaves no trace either.
resolve_build_user() {
  BUILD_USER="${SHIPQUICK_BUILD_USER:-}"
  if [ -z "$BUILD_USER" ]; then
    _top="$(git rev-parse --show-toplevel 2>/dev/null)" || _top=""
    [ -n "$_top" ] && BUILD_USER="$(python3 "$HERE/roles.py" get coder --file "$_top/.shipquick/roles.yml" 2>/dev/null | cut -d, -f1)"
  fi
  [ -n "$BUILD_USER" ] || { echo "freeze.sh: no \$SHIPQUICK_BUILD_USER and no coder account in .shipquick/roles.yml -- run adopt.sh <path> --coder <acct> --reviewer <acct> --owner <acct>, or set SHIPQUICK_BUILD_USER" >&2; exit 1; }
}

push_and_pr() {   # push_and_pr <worktree> <branch> <pr-title> <pr-body> -- $BUILD_USER already set
  wt="$1"; branch="$2"; title="$3"; body="$4"
  if [ "${FREEZE_NO_PUSH:-0}" = 1 ]; then
    echo "dry run (FREEZE_NO_PUSH=1): committed on $branch, not pushed (build account: $BUILD_USER)"
    return 0
  fi
  token="$(gh auth token --user "$BUILD_USER")" || { echo "freeze.sh: no token for $BUILD_USER on this machine" >&2; return 1; }
  repo="$(GH_TOKEN="$token" gh -C "$wt" repo view --json nameWithOwner --jq .nameWithOwner)" || { echo "freeze.sh: cannot resolve owner/repo" >&2; return 1; }
  GH_TOKEN="$token" git -C "$wt" push -u origin "$branch" -q || { echo "freeze.sh: push failed" >&2; return 1; }
  GH_TOKEN="$token" gh -C "$wt" pr create -R "$repo" --base main --head "$branch" --title "$title" --body "$body"
}

cmd="${1:-}"; [ -n "$cmd" ] && shift
case "$cmd" in
  on)
    reason="${1:-}"; [ -n "$reason" ] && shift || usage
    until=""
    while [ $# -gt 0 ]; do
      case "$1" in
        --until) [ -n "${2:-}" ] || usage; until="$2"; shift 2 ;;
        *) usage ;;
      esac
    done
    [ -n "$until" ] || usage
    valid_date "$until" || { echo "freeze.sh: bad --until date: $until" >&2; exit 2; }
    root="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "freeze.sh: not a git repo" >&2; exit 1; }
    cd "$root"
    [ -z "$(git status --porcelain)" ] || { echo "freeze.sh: working tree not clean" >&2; exit 1; }
    resolve_build_user
    git fetch origin main -q
    make_worktree chore/freeze-on
    mkdir -p "$wt/.shipquick"
    printf 'reason: %s\nuntil: %s\n' "$reason" "$until" > "$wt/.shipquick/freeze"
    git -C "$wt" add .shipquick/freeze
    git -C "$wt" commit -q -m "chore: freeze release — $reason"
    body=$(cat <<EOF
Freeze on until $until: $reason

## For the reviewer
\`\`\`
To reviewer, from coder, re freeze on ($until):
1. .shipquick/freeze now blocks every merge into main until $until, or freeze.sh off.
Need from you: review and merge.
\`\`\`
EOF
)
    push_and_pr "$wt" "$branch" "chore: freeze release — $reason" "$body"
    ;;
  off)
    root="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "freeze.sh: not a git repo" >&2; exit 1; }
    cd "$root"
    [ -z "$(git status --porcelain)" ] || { echo "freeze.sh: working tree not clean" >&2; exit 1; }
    resolve_build_user
    git fetch origin main -q
    git cat-file -e origin/main:.shipquick/freeze 2>/dev/null || { echo "freeze.sh: not frozen on main, nothing to lift" >&2; exit 1; }
    make_worktree chore/freeze-off
    git -C "$wt" rm -q .shipquick/freeze
    git -C "$wt" commit -q -m "chore: lift release freeze"
    body=$(cat <<EOF
Lifts the current release freeze.

## For the reviewer
\`\`\`
To reviewer, from coder, re freeze off:
1. .shipquick/freeze is a protected path, story #131: this PR needs the owner to merge it directly, auto mode refuses it.
Need from you: review, then the owner merges.
\`\`\`
EOF
)
    push_and_pr "$wt" "$branch" "chore: lift release freeze" "$body"
    ;;
  status)
    repo=""; ref="main"
    while [ $# -gt 0 ]; do
      case "$1" in
        --repo) [ -n "${2:-}" ] || usage; repo="$2"; shift 2 ;;
        --ref) [ -n "${2:-}" ] || usage; ref="$2"; shift 2 ;;
        *) usage ;;
      esac
    done
    if [ -n "$repo" ]; then
      content="$(gh api "repos/$repo/contents/.shipquick/freeze?ref=$ref" --jq '.content' 2>/dev/null | base64 -d 2>/dev/null)" || content=""
    else
      root="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "freeze.sh: not a git repo" >&2; exit 1; }
      git -C "$root" fetch origin main -q 2>/dev/null
      content="$(git -C "$root" show origin/main:.shipquick/freeze 2>/dev/null || true)"
    fi
    printf '%s' "$content" | python3 "$HERE/check_freeze.py"
    exit $?
    ;;
  *) usage ;;
esac
