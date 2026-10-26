#!/usr/bin/env bash
# One command to adopt ShipQuick in a child project (story #68). Run it from the ShipQuick checkout (in a child: knowledge/shipquick_latest):
#   bash knowledge/shipquick_latest/scripts/adopt.sh . [--ref <tag-or-sha>]
# It copies or updates five things in the child repo and prints what it did (created / updated / unchanged / kept). A second run changes nothing.
#   .gitattributes                      adds the merge=union lines for the append-only logs; your own lines stay
#   .github/workflows/roadmap-call.yml  the roadmap caller, pinned to this checkout's commit (or --ref), with your ci.yml's `name:` for workflow_run
#   roadmap.json                        a stub (title, vision) only if you have none; yours is never overwritten
#   .claude/commands/mode.md            the /mode command
#   .pre-commit-config.yaml             the check_local.sh hooks, only if you have none (it prints the hook to add if yours lacks them)
# Needs git and python3. It never commits.
set -eu
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SQ="$(cd "$HERE/.." && pwd -P)"
usage() { echo "usage: adopt.sh <child-path> [--ref <tag-or-sha>]" >&2; exit 2; }
child=""; ref=HEAD
while [ $# -gt 0 ]; do
  case "$1" in
    --ref) [ -n "${2:-}" ] || usage; ref="$2"; shift 2 ;;
    -*) usage ;;
    *) [ -z "$child" ] || usage; child="$1"; shift ;;
  esac
done
[ -n "$child" ] || usage
[ -d "$child" ] || { echo "adopt.sh: no such folder: $child" >&2; exit 2; }
child="$(cd "$child" && pwd -P)"
top="$(git -C "$child" rev-parse --show-toplevel 2>/dev/null)" || { echo "adopt.sh: $child is not a git repository" >&2; exit 2; }
[ "$(cd "$top" && pwd -P)" = "$child" ] || { echo "adopt.sh: run it on the root of the repository ($top)" >&2; exit 2; }
sha="$(git -C "$SQ" rev-parse --verify -q "$ref^{commit}")" || { echo "adopt.sh: ShipQuick has no ref '$ref'" >&2; exit 2; }
tag="$(git -C "$SQ" describe --tags --exact-match "$sha" 2>/dev/null || true)"
[ -n "$tag" ] || echo "note: $sha is not a release tag. Pass --ref vX.Y.Z to pin a release."

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
# put <relative path>: the new content comes on stdin. Writes only when it differs.
put() {
  local rel="$1" dest="$child/$1"
  cat > "$tmp/new"; chmod 644 "$tmp/new"
  if [ ! -e "$dest" ]; then mkdir -p "$(dirname "$dest")"; cp "$tmp/new" "$dest"; echo "created   $rel"
  elif cmp -s "$tmp/new" "$dest"; then echo "unchanged $rel"
  else cp "$tmp/new" "$dest"; echo "updated   $rel"; fi
}

# 1. .gitattributes: keep the child's lines, add ours once
{ [ -f "$child/.gitattributes" ] && cat "$child/.gitattributes"; true; } > "$tmp/attrs"
for line in "docs/process-trace.md merge=union" "docs/LEARNINGS.md merge=union"; do
  grep -qxF "$line" "$tmp/attrs" || {
    [ ! -s "$tmp/attrs" ] || [ -z "$(tail -c1 "$tmp/attrs")" ] || echo >> "$tmp/attrs"
    grep -q "ShipQuick append-only" "$tmp/attrs" || echo "# ShipQuick append-only logs (rule 23): two branches that add rows at the end merge with no conflict." >> "$tmp/attrs"
    echo "$line" >> "$tmp/attrs"
  }
done
put .gitattributes < "$tmp/attrs"

# 2. the roadmap caller: ShipQuick's own caller, pinned, with the child's CI name
ci_name=""
if [ -f "$child/.github/workflows/ci.yml" ]; then
  ci_name="$(sed -n 's/^name: *"\{0,1\}\([^"]*[^" ]\)"\{0,1\} *$/\1/p' "$child/.github/workflows/ci.yml" | head -1)"
fi
python3 - "$SQ/.github/workflows/roadmap-call.yml" "$sha" "$tag" "$ci_name" > "$tmp/call" <<'PYEOF'
import re, sys
src, sha, tag, ci = sys.argv[1:5]
lines = [l for l in open(src, encoding="utf-8").read().splitlines() if not l.startswith("#")]
out = ["# The live roadmap page of this project (added by ShipQuick scripts/adopt.sh): a call to the reusable workflow, pinned to one commit.",
       "# No pull_request trigger on purpose: on a PR the job would run that PR's own unreviewed script with write rights.",
       "# To move to a newer ShipQuick release, run adopt.sh again with --ref <tag>: it changes `uses:` and `shipquick_ref` together.",
       "# workflow_run matches your CI workflow by its `name:` (adopt.sh read it from .github/workflows/ci.yml)."]
skip = False
for l in lines:
    if l.startswith("  workflow_run:"):
        skip = not ci
    elif skip and not l.startswith("    "):
        skip = False
    if skip:
        continue
    l = l.replace("uses: ./.github/workflows/roadmap.yml", f"uses: satvik-jain-iitd/shipquick_latest/.github/workflows/roadmap.yml@{sha}" + (f" # {tag}" if tag else ""))
    l = l.replace("shipquick_ref: ${{ github.sha }}", f"shipquick_ref: {sha}")
    l = l.replace('workflows: ["shipquick_latest CI"]', f'workflows: ["{ci}"]')
    out.append(l)
print("\n".join(out))
PYEOF
put .github/workflows/roadmap-call.yml < "$tmp/call"
[ -n "$ci_name" ] || echo "note: no name: found in .github/workflows/ci.yml, so the caller has no workflow_run trigger. Add one by hand if you want Review to update when the checks finish."

# 3. roadmap.json: a stub only if there is none
if [ -e "$child/roadmap.json" ]; then echo "kept      roadmap.json (yours)"
else
  python3 -c 'import json,sys; print(json.dumps({"title": sys.argv[1], "vision": "Write one line here: the end goal, in words a stranger understands."}, indent=2))' "$(basename "$child")" | put roadmap.json
  echo "note: roadmap.json is a stub. Write the vision line before the page goes live."
fi

# 4. the /mode command
put .claude/commands/mode.md < "$SQ/.claude/commands/mode.md"

# 5. the pre-commit hooks
rel="$(python3 -c 'import os,sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))' "$SQ" "$child")"
hooks="  - repo: local
    hooks:
      - id: check-local
        name: ShipQuick hygiene checks on this Mac
        entry: bash $rel/scripts/check_local.sh sizes markers md-blocks secrets-staged
        language: system
        pass_filenames: false
        always_run: true
        stages: [pre-commit]
      - id: check-local-push
        name: All ShipQuick hygiene checks before a push
        entry: bash $rel/scripts/check_local.sh
        language: system
        pass_filenames: false
        always_run: true
        stages: [pre-push]"
if [ -e "$child/.pre-commit-config.yaml" ] && grep -q "check_local.sh" "$child/.pre-commit-config.yaml"; then
  echo "unchanged .pre-commit-config.yaml (has the ShipQuick hooks)"
elif [ -e "$child/.pre-commit-config.yaml" ]; then
  echo "kept      .pre-commit-config.yaml (yours). Add this under repos: to run the ShipQuick checks (scripts/check_local.sh):"
  echo "$hooks"
else
  printf 'repos:\n%s\n' "$hooks" | put .pre-commit-config.yaml
fi

echo "Next: look at git status, commit these files, and merge them into the default branch (scheduled and issue runs start only from there)."
echo "If a branch of yours was made before .gitattributes existed, its first merge of the default branch needs the .git/info/attributes step in pm/agile/templates/sprint-lanes.md."
