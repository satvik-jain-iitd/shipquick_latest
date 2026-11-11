#!/usr/bin/env bash
# The CI hygiene checks, run on this Mac before a push (rule 29, story #43). Same rules as .github/workflows/ci.yml.
# Usage: scripts/check_local.sh [check ...]
#   checks: sizes markers md-blocks rule-copies ui-docs ui-registry ui-topics ui-proof ui-contracts ui-tokens ui-coverage workflow-security commits pr-size frontend-design disable-comments design-tokens story tdd roadmap shortcuts secrets secrets-staged   (no argument = all but secrets-staged)
#   roadmap (story #81): `node --test roadmap/*.test.js`, the same line as ci.yml; skipped when node is missing
#   rule-copies (story #316): the kit CLAUDE.md carries its load-bearing rule phrases; a child is checked with check_rule_copies.py --child
#   design-tokens (story #133): no hex, rgb(), hsl() or font-family literal on an added web style line (check_design_literals.py); then stylelint on changed css per package root (run_stylelint_changed.sh), only when npx and a stylelint config exist
#   story (story #155): every `user-story` issue a commit message since $BASE links (Closes #n) must carry `Who does it:`; needs gh
#   tdd (story #319): the `## Red` section with the test path must be in a commit body before a push; CI reads the real PR body
#   shortcuts (story #327): warn only, prints the count of shortcut:/ponytail: comments; runs after the checks when no argument is given
#   frontend-design (story #121): scans the commit messages since $BASE for "Design board:" / "no screen change" (a PR body is not there yet before a push)
#   BASE=dev   the branch to compare with (origin/$BASE); a check that needs it is skipped when it is missing
#   secrets    the whole history (push); secrets-staged only what is staged (commit, fast). Both need gitleaks: brew install gitleaks
#   markers    checks tracked files; an untracked file with a marker passes here, CI scans the whole checkout
# Wired into .pre-commit-config.yaml: the fast checks on commit, all of them on push.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$(git rev-parse --show-toplevel)" || exit 2
BASE="${BASE:-dev}"
MARKERS='^(<<<<<<< |=======$|>>>>>>> )'
CONVENTIONAL='^(feat|fix|docs|design|test|chore|refactor|style|perf|ci|build|release)(\(.+\))?: .+'
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
check_rule_copies() { python3 "$HERE/check_rule_copies.py"; report rule-copies $?; }   # story #316
check_ui_registry() { [ -f ui/registry.json ] || return 0; python3 "$HERE/check_component_request.py"; report ui-registry $?; }   # story #186
check_ui_docs() { [ -d ui/components ] || return 0; python3 "$HERE/check_ui_docs.py" --root ui/components; report ui-docs $?; }   # story #182
check_ui_topics() { [ -d ui/integration ] || return 0; python3 "$HERE/ui_topics.py" --check; report ui-topics $?; }   # story #183
check_ui_tokens() { [ -f design/tokens.json ] || return 0; python3 "$HERE/emit_tokens.py" --check; report ui-tokens $?; }   # story #184
check_ui_proof() { [ -d ui/components ] || return 0; python3 "$HERE/ui_proof.py" --check; report ui-proof $?; }   # story #217
check_ui_contracts() { [ -d ui/components ] || return 0; python3 "$HERE/emit_contracts.py" --check; report ui-contracts $?; }   # story #222
check_ui_coverage() { [ -d ui/components ] || return 0; python3 "$HERE/check_ui_coverage.py" --strict-api; report ui-coverage $?; }   # stories #216, #231; web part skips without ui/tool/node_modules
check_timeouts() { [ -d .github/workflows ] || return 0; python3 "$HERE/check_timeouts.py" .github/workflows; report timeouts $?; }
check_commits() {
  have_base commits || return 0
  local bad
  bad=$(git log "origin/$BASE..HEAD" --pretty=%s | grep -v '^Merge ' | grep -vE "$CONVENTIONAL")
  [ -n "$bad" ] && { echo "Non-conventional commits found:"; echo "$bad"; }
  [ -z "$bad" ]; report commits $?
}
check_pr_size() {
  have_base pr-size || return 0
  local branch n
  branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
  if [ "$BASE" = main ]; then
    case "$branch" in
      release/*) echo "skip pr-size: a release branch into main aggregates already-reviewed dev commits, not new review surface"; report pr-size 0; return 0 ;;
    esac
  fi
  # story #219: recorded reference images in the protected folder ui/ios/ShipQuickUITests/__Snapshots__/ are looked at, not read;
  # anchored to that folder so a __Snapshots__/ folder anywhere else still counts (#375 review)
  n=$(changed | grep -vE '^ui/ios/ShipQuickUITests/__Snapshots__/.*\.png$' | wc -l | tr -d ' ')
  echo "Counted files: $n (max 50, renames and ui/ios/ShipQuickUITests/__Snapshots__/*.png reference images ignored)"
  [ "$n" -le 50 ]; report pr-size $?
}
check_frontend_design() {
  have_base frontend-design || return 0
  local tmp rc
  tmp="$(mktemp)"
  git log "origin/$BASE..HEAD" --format=%B > "$tmp"
  bash "$HERE/check_frontend_design.sh" --body-file "$tmp" --base "origin/$BASE" --repo .
  rc=$?
  rm -f "$tmp"
  report frontend-design "$rc"
}
check_disable_comments() {
  have_base disable-comments || return 0
  local tmp rc
  tmp="$(mktemp)"
  git log "origin/$BASE..HEAD" --format=%B > "$tmp"
  python3 "$HERE/check_disable_comments.py" --base "origin/$BASE" --body-file "$tmp"
  rc=$?
  rm -f "$tmp"
  report disable-comments "$rc"
}
check_story() {
  have_base story || return 0
  command -v gh >/dev/null || { echo "skip story: gh is not installed"; return 0; }
  gh auth status >/dev/null 2>&1 || { echo "skip story: gh is not logged in (gh auth login); CI still checks it"; return 0; }
  local tmp rc
  tmp="$(mktemp)"
  git log "origin/$BASE..HEAD" --format=%B > "$tmp"
  python3 "$HERE/check_story.py" --pr-body-file "$tmp"
  rc=$?
  rm -f "$tmp"
  report story "$rc"
}
check_workflow_security() { python3 "$HERE/check_workflow_security.py"; report workflow-security $?; }   # story #325
check_design_tokens() {   # story #133: the same two steps as the design-tokens CI job
  have_base design-tokens || return 0
  python3 "$HERE/check_design_literals.py" --base "origin/$BASE"
  report design-tokens $?
  bash "$HERE/run_stylelint_changed.sh" "origin/$BASE"
  report stylelint $?
}
check_tdd() {   # story #319 (A15): the commit log stands in for the PR body before a push; CI reads the real body
  have_base tdd || return 0
  local tmp rc
  tmp="$(mktemp)"
  git log "origin/$BASE..HEAD" --format=%B > "$tmp"
  python3 "$HERE/check_tdd.py" --body-file "$tmp" --base "origin/$BASE" --base-branch "$BASE" --head-branch "$(git rev-parse --abbrev-ref HEAD)"
  rc=$?
  rm -f "$tmp"
  report tdd "$rc"
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

check_roadmap() {   # story #81: the roadmap's node:test files, the same command as ci.yml; todo tests (stories #82, #83) do not fail the run
  command -v node >/dev/null || { echo "skip roadmap: node is not installed"; return 0; }
  node --test roadmap/*.test.js
  report roadmap $?
}
check_shortcuts() {   # story #327: warn only, never sets failed
  echo "warn shortcuts: $(python3 "$HERE/check_shortcuts.py" 2>&1 | tail -1)"
}
checks=("$@")
[ $# -eq 0 ] && checks=(sizes markers md-blocks rule-copies ui-docs ui-registry ui-topics ui-proof ui-contracts ui-tokens ui-coverage timeouts commits pr-size frontend-design disable-comments design-tokens story tdd roadmap workflow-security secrets)
for c in "${checks[@]}"; do
  case "$c" in
    sizes|markers|commits|secrets) "check_$c" ;;
    md-blocks) check_md_blocks ;;
    rule-copies) check_rule_copies ;;
    ui-docs) check_ui_docs ;;
    ui-registry) check_ui_registry ;;
    ui-topics) check_ui_topics ;;
    ui-proof) check_ui_proof ;;
    ui-contracts) check_ui_contracts ;;
    ui-tokens) check_ui_tokens ;;
    ui-coverage) check_ui_coverage ;;
    timeouts) check_timeouts ;;
    secrets-staged) check_secrets_staged ;;
    pr-size) check_pr_size ;;
    frontend-design) check_frontend_design ;;
    disable-comments) check_disable_comments ;;
    design-tokens) check_design_tokens ;;
    story) check_story ;;
    shortcuts) check_shortcuts ;;
    workflow-security) check_workflow_security ;;
    tdd) check_tdd ;;
    roadmap) check_roadmap ;;
    *) echo "unknown check: $c (sizes markers md-blocks rule-copies ui-docs ui-registry ui-topics ui-proof ui-contracts ui-tokens ui-coverage workflow-security timeouts commits pr-size frontend-design disable-comments design-tokens story tdd roadmap shortcuts secrets secrets-staged)"; exit 2 ;;
  esac
done
[ $# -eq 0 ] && check_shortcuts
[ "$failed" -eq 0 ] && echo "check_local: all passed"
exit "$failed"
