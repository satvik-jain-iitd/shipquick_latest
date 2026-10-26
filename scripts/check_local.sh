#!/usr/bin/env bash
# The CI hygiene checks, run on this Mac before a push (rule 29, story #43). Same rules as .github/workflows/ci.yml.
# Usage: scripts/check_local.sh [check ...]
#   checks: sizes markers md-blocks commits pr-size secrets secrets-staged   (no argument = all but secrets-staged)
#   BASE=dev   the branch to compare with (origin/$BASE); a check that needs it is skipped when it is missing
#   secrets    the whole history (push); secrets-staged only what is staged (commit, fast). Both need gitleaks: brew install gitleaks
#   markers    checks tracked files; an untracked file with a marker passes here, CI scans the whole checkout
# Wired into .pre-commit-config.yaml: the fast checks on commit, all of them on push.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$(git rev-parse --show-toplevel)" || exit 2
BASE="${BASE:-dev}"
MARKERS='^(<<<<<<< |=======$|>>>>>>> )'
CONVENTIONAL='^(feat|fix|docs|design|test|chore|refactor|style|perf|ci|build)(\(.+\))?: .+'
failed=0

have_base() { git rev-parse --verify -q "origin/$BASE" >/dev/null || { echo "skip $1: no origin/$BASE here"; return 1; }; }
# Files changed since the branch left $BASE (committed, staged or edited). Renames do not count.
changed() { git diff --name-status -M "$(git merge-base "origin/$BASE" HEAD)" | awk -F'\t' '$1 !~ /^R/ {print $2}'; }
report() { if [ "$2" -eq 0 ]; then echo "ok   $1"; else echo "FAIL $1"; failed=1; fi; }

check_sizes() {
  have_base sizes || return 0
  local f large=""
  while IFS= read -r f; do
    [ -f "$f" ] && [ "$(wc -c < "$f")" -gt 512000 ] && large="$large $f"
  done < <(changed)
  [ -n "$large" ] && echo "Changed files over 500KB:$large"
  [ -z "$large" ]; report sizes $?
}
check_markers() {
  if git grep -nE "$MARKERS" -- '*.py' '*.ts' '*.tsx' '*.md'; then
    echo "Merge conflict markers found"; report markers 1
  else
    report markers 0
  fi
}
check_md_blocks() { python3 "$HERE/check_md_blocks.py"; report md-blocks $?; }
check_commits() {
  have_base commits || return 0
  local bad
  bad=$(git log "origin/$BASE..HEAD" --pretty=%s | grep -v '^Merge ' | grep -vE "$CONVENTIONAL")
  [ -n "$bad" ] && { echo "Non-conventional commits found:"; echo "$bad"; }
  [ -z "$bad" ]; report commits $?
}
check_pr_size() {
  have_base pr-size || return 0
  local n
  n=$(changed | wc -l | tr -d ' ')
  echo "Counted files: $n (max 50, renames ignored)"
  [ "$n" -le 50 ]; report pr-size $?
}
check_secrets() {
  command -v gitleaks >/dev/null || { echo "skip secrets: gitleaks is not installed (brew install gitleaks)"; return 0; }
  gitleaks git --no-banner --no-color --redact --verbose .
  report secrets $?
}
check_secrets_staged() {
  command -v gitleaks >/dev/null || { echo "skip secrets-staged: gitleaks is not installed (brew install gitleaks)"; return 0; }
  gitleaks git --pre-commit --staged --no-banner --no-color --redact --verbose .
  report secrets-staged $?
}

checks=("$@")
[ $# -eq 0 ] && checks=(sizes markers md-blocks commits pr-size secrets)
for c in "${checks[@]}"; do
  case "$c" in
    sizes|markers|commits|secrets) "check_$c" ;;
    md-blocks) check_md_blocks ;;
    secrets-staged) check_secrets_staged ;;
    pr-size) check_pr_size ;;
    *) echo "unknown check: $c (sizes markers md-blocks commits pr-size secrets secrets-staged)"; exit 2 ;;
  esac
done
[ "$failed" -eq 0 ] && echo "check_local: all passed"
exit "$failed"
