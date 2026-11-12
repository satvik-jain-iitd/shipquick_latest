#!/usr/bin/env bash
# The CI hygiene checks, run on this Mac before a push (rule 29, story #43). Same rules as .github/workflows/ci.yml.
# Usage: scripts/check_local.sh [check ...]
#   checks: sizes markers md-blocks rule-copies ui-docs ui-registry ui-topics ui-llms ui-proof ui-contracts ui-tokens ui-coverage workflow-security features-wiring commits commit-subjects pr-size frontend-design disable-comments design-tokens story tdd roadmap shortcuts secrets secrets-staged   (no argument = all but secrets-staged)
#   roadmap (story #81): `node --test roadmap/*.test.js`, the same line as ci.yml; skipped when node is missing
#   rule-copies (story #316): the kit CLAUDE.md carries its load-bearing rule phrases; a child is checked with check_rule_copies.py --child
#   design-tokens (story #133): no hex, rgb(), hsl() or font-family literal on an added web style line (check_design_literals.py); then stylelint on changed css per package root (run_stylelint_changed.sh), only when npx and a stylelint config exist
#   story (story #155): every `user-story` issue a commit message since $BASE links (Closes #n) must carry `Who does it:`; needs gh
#   tdd (story #319): the `## Red` section with the test path must be in a commit body before a push; CI reads the real PR body
#   shortcuts (story #327): warn only, prints the count of shortcut:/ponytail: comments; runs after the checks when no argument is given
#   frontend-design (story #121): scans the commit messages since $BASE for "Design board:" / "no screen change" (a PR body is not there yet before a push)
#   BASE=dev   the branch to compare with (origin/$BASE); a check that needs it is skipped when it is missing. Not set: dev, or the caller's kit_branch when the branch descends from it (story #469)
#   secrets    the commits since origin/$BASE (push; the whole history when there is no origin/$BASE); secrets-staged only what is staged (commit, fast). Both need gitleaks: brew install gitleaks
#   markers    checks tracked files; an untracked file with a marker passes here, CI scans the whole checkout
# Wired into .pre-commit-config.yaml: the fast checks on commit, all of them on push.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$(git rev-parse --show-toplevel)" || exit 2
if [ -z "${BASE:-}" ]; then
  BASE=dev
  # story #469: a rule-24 child cuts its bump branch from the kit branch; compare with that branch, not dev. An explicit BASE wins.
  # ponytail: counts commits ahead of each base; a branch whose merge history makes both counts equal keeps dev.
  if [ -f .github/workflows/shipquick-call.yml ]; then
    kit=$(python3 "$HERE/kit_branch.py" parse < .github/workflows/shipquick-call.yml) || { echo "FAIL kit-branch: $kit"; exit 2; }
    # the nearer base wins: the kit branch only when HEAD is fewer commits ahead of it than of origin/dev (a missing origin/dev is far)
    if [ -n "$kit" ] && git merge-base --is-ancestor "origin/$kit" HEAD 2>/dev/null; then
      ahead_kit=$(git rev-list --count "origin/$kit..HEAD"); ahead_dev=$(git rev-list --count "origin/dev..HEAD" 2>/dev/null || echo 999999999)
      if [ "$ahead_kit" -lt "$ahead_dev" ]; then
        BASE="$kit"; echo "base: origin/$kit (the kit branch this branch was cut from; set BASE to override)"
      fi
    fi
  fi
fi
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
check_ui_llms() { [ -d ui/components ] || return 0; python3 "$HERE/ui_mcp.py" llms --check; report ui-llms $?; }   # story #190
check_ui_tokens() { [ -f design/tokens.json ] || return 0; python3 "$HERE/emit_tokens.py" --check; report ui-tokens $?; }   # story #184
check_ui_proof() { [ -d ui/components ] || return 0; python3 "$HERE/ui_proof.py" --check; report ui-proof $?; }   # story #217
check_ui_contracts() { [ -d ui/components ] || return 0; python3 "$HERE/emit_contracts.py" --check; report ui-contracts $?; }   # story #222
check_ui_coverage() { [ -d ui/components ] || return 0; python3 "$HERE/check_ui_coverage.py" --strict-api; report ui-coverage $?; }   # stories #216, #231; web part skips without ui/tool/node_modules
check_features_wiring() { [ -f "$HERE/../.github/workflows/checks.yml" ] || return 0;   # the workflow the script reads sits in the kit, not in the cwd
  python3 "$HERE/check_features_wiring.py"; report features-wiring $?; }   # story #422
check_timeouts() { [ -d .github/workflows ] || return 0; python3 "$HERE/check_timeouts.py" .github/workflows; report timeouts $?; }
check_commit_subjects() {   # story #446: the same rule as CI's commit-subjects job
  have_base commit-subjects || return 0
  python3 "$HERE/check_commit_subjects.py" --base "origin/$BASE"; report commit-subjects $?
}
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
  # story #454: a push is judged on the commits it adds. History below origin/$BASE was already pushed; an old finding there is not this push's.
  local range=()
  git rev-parse --verify -q "origin/$BASE" >/dev/null && range=(--log-opts "origin/$BASE..HEAD")
  gitleaks git --no-banner --no-color --redact --verbose ${range[@]+"${range[@]}"} .
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
# story #423: the feature flags (scripts/features.py) switch a check off. Off prints `skipped: <id> is off`, the same words CI's
# features job prints. A broken features file fails the run: an error is never read as "on". The file is the project's own, here.
feature_of() {   # feature_of <check> -- the feature id that switches the check, or nothing when it has none
  case "$1" in
    rule-copies) echo rule-copies ;;
    commit-subjects) echo commit-subjects ;;
    disable-comments) echo disable-comments ;;
    design-tokens) echo design-tokens ;;
    frontend-design) echo frontend-design ;;
    story) echo story ;;
    roadmap) echo roadmap ;;
    ui-registry) echo component-registry ;;
  esac
}
feature_skip() {   # feature_skip <check>: returns 0 when the check must be skipped, 1 to run it, 2 when the features file is broken
  local id out rc=0
  id="$(feature_of "$1")"; [ -n "$id" ] || return 1
  out="$(python3 "$HERE/features.py" get "$id" 2>&1)" || rc=$?
  case "$rc" in
    0) return 1 ;;
    1) echo "skipped: $id is off"; return 0 ;;
    *) echo "FAIL features: $out"; failed=1; return 2 ;;
  esac
}
checks=("$@")
[ $# -eq 0 ] && checks=(sizes markers md-blocks rule-copies ui-docs ui-registry ui-topics ui-llms ui-proof ui-contracts ui-tokens ui-coverage timeouts features-wiring commits commit-subjects pr-size frontend-design disable-comments design-tokens story tdd roadmap workflow-security secrets)
for c in "${checks[@]}"; do
  feature_skip "$c" && continue
  [ $? -eq 2 ] && continue
  case "$c" in
    sizes|markers|commits|secrets) "check_$c" ;;
    md-blocks) check_md_blocks ;;
    rule-copies) check_rule_copies ;;
    commit-subjects) check_commit_subjects ;;
    ui-docs) check_ui_docs ;;
    ui-registry) check_ui_registry ;;
    ui-topics) check_ui_topics ;;
    ui-llms) check_ui_llms ;;
    ui-proof) check_ui_proof ;;
    ui-contracts) check_ui_contracts ;;
    ui-tokens) check_ui_tokens ;;
    ui-coverage) check_ui_coverage ;;
    timeouts) check_timeouts ;;
    features-wiring) check_features_wiring ;;
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
    *) echo "unknown check: $c (sizes markers md-blocks rule-copies ui-docs ui-registry ui-topics ui-llms ui-proof ui-contracts ui-tokens ui-coverage workflow-security timeouts features-wiring commits commit-subjects pr-size frontend-design disable-comments design-tokens story tdd roadmap shortcuts secrets secrets-staged)"; exit 2 ;;
  esac
done
[ $# -eq 0 ] && check_shortcuts
[ "$failed" -eq 0 ] && echo "check_local: all passed"
exit "$failed"
