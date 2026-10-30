#!/usr/bin/env bash
# Story #126 (GoServe feedback #126): a release freeze is a mechanism, not a sentence.
#   freeze.sh on "<reason>" --until <date>   # writes .shipquick/freeze on main through a PR
#   freeze.sh off                             # removes it through a PR -- .shipquick/freeze is a
#                                              #   protected path (story #131), so the owner merges this PR too
#   freeze.sh status [--repo <owner/repo>] [--ref <branch>]   # prints what check_freeze.py decides;
#                                              #   no --repo reads the current checkout's .shipquick/freeze
# on/off run inside the repo's own clean git checkout with an `origin` remote; push and the PR use the
# build account ($SHIPQUICK_BUILD_USER, default klickbae8yt-star). FREEZE_NO_PUSH=1 stops right after the
# local commit, used by tests (no network, no PR). A freeze does not lift itself past --until (story #126
# scenario 4): only `freeze.sh off`, or a renewed `on`, changes it. Needs git, gh.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_USER="${SHIPQUICK_BUILD_USER:-klickbae8yt-star}"
usage() { echo 'usage: freeze.sh on "<reason>" --until <date> | freeze.sh off | freeze.sh status [--repo owner/repo] [--ref branch]' >&2; exit 2; }

valid_date() { date -d "$1" >/dev/null 2>&1 || date -j -f "%Y-%m-%d" "$1" >/dev/null 2>&1; }

push_and_pr() {   # push_and_pr <branch> <commit-title> <pr-body>
  branch="$1"; title="$2"; body="$3"
  if [ "${FREEZE_NO_PUSH:-0}" = 1 ]; then
    echo "dry run (FREEZE_NO_PUSH=1): committed on $branch, not pushed"
    return 0
  fi
  token="$(gh auth token --user "$BUILD_USER")" || { echo "freeze.sh: no token for $BUILD_USER on this machine" >&2; return 1; }
  repo="$(GH_TOKEN="$token" gh repo view --json nameWithOwner --jq .nameWithOwner)" || { echo "freeze.sh: cannot resolve owner/repo" >&2; return 1; }
  GH_TOKEN="$token" git push -u origin "$branch" -q || { echo "freeze.sh: push failed" >&2; return 1; }
  GH_TOKEN="$token" gh pr create -R "$repo" --base main --head "$branch" --title "$title" --body "$body"
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
    git fetch origin main -q
    branch="chore/freeze-on-$(date +%s)"
    git checkout -q -B "$branch" origin/main
    mkdir -p .shipquick
    printf 'reason: %s\nuntil: %s\n' "$reason" "$until" > .shipquick/freeze
    git add .shipquick/freeze
    git commit -q -m "chore: freeze release — $reason"
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
    push_and_pr "$branch" "chore: freeze release — $reason" "$body"
    ;;
  off)
    root="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "freeze.sh: not a git repo" >&2; exit 1; }
    cd "$root"
    [ -z "$(git status --porcelain)" ] || { echo "freeze.sh: working tree not clean" >&2; exit 1; }
    git fetch origin main -q
    branch="chore/freeze-off-$(date +%s)"
    git checkout -q -B "$branch" origin/main
    [ -f .shipquick/freeze ] || { echo "freeze.sh: not frozen on main, nothing to lift" >&2; exit 1; }
    git rm -q .shipquick/freeze
    git commit -q -m "chore: lift release freeze"
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
    push_and_pr "$branch" "chore: lift release freeze" "$body"
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
      content="$([ -f "$root/.shipquick/freeze" ] && cat "$root/.shipquick/freeze" || true)"
    fi
    printf '%s' "$content" | python3 "$HERE/check_freeze.py"
    exit $?
    ;;
  *) usage ;;
esac
