#!/usr/bin/env bash
# One command to adopt ShipQuick in a child project (story #68). Run it from the ShipQuick checkout (in a child: knowledge/shipquick_latest):
#   bash knowledge/shipquick_latest/scripts/adopt.sh . [--ref <tag-or-sha>]
# It copies or updates seven things in the child repo and prints what it did (created / updated / unchanged / kept). A second run changes nothing.
#   .gitattributes                      adds the merge=union lines for the append-only logs; your own lines stay
#   .github/workflows/roadmap-call.yml  the roadmap caller, pinned to this checkout's commit (or --ref), with your ci.yml's `name:` for workflow_run
#   .github/workflows/shipquick-call.yml the PR checks caller (story #124), pinned the same way, triggered on every pull_request
#   roadmap.json                        a stub (title, vision) only if you have none; yours is never overwritten
#   .claude/commands/mode.md            the /mode command
#   .pre-commit-config.yaml             the check_local.sh hooks, only if you have none (it prints the hook to add if yours lacks them)
#   CLAUDE.md                           the one pointer line to the protocol, and the kit rule block between the shipquick-rules markers (rewritten on every run); a new file starts from docs/CLAUDE.project.template.md, yours keeps every line outside the markers
#   .shipquick/roles.yml                 which accounts may code, review, and own this project (story #140), only if you have none
# --coder/--reviewer <acct[,acct]> --owner <acct>: fill .shipquick/roles.yml on first adoption. With none
#   of these and no roles.yml yet, adopt.sh writes nothing for it and tells you to rerun with the flags or
#   fill it by hand -- CI's `roles` job and `scripts/review_merge.sh` both refuse until it exists.
# --check (story #124): prints the adoption verdict and exits 1 when not adopted, instead of writing anything.
#   Adopted means: .github/workflows/shipquick-call.yml is pinned to the exact commit the
#   knowledge/shipquick_latest submodule is at, and .pre-commit-config.yaml carries the ShipQuick hooks,
#   and (story #260) `shipquick-checks / gate` is a required check on the default branch (read with gh).
#   A normal run prints the one command that makes it required; adopt.sh never runs it.
#   Story #326: --check also needs enabledPlugins["ponytail@ponytail"] true in ~/.claude/settings.json (or $SHIPQUICK_CLAUDE_SETTINGS);
#   when it is not, the two install lines are printed and the verdict is not adopted. With CI set it only warns.
# --kit-branch <b> (story #225, rule-24 children): writes `kit_branch: <b>` into shipquick-call.yml. The checks
#   then read the submodule pin, .pre-commit-config.yaml and .shipquick/roles.yml from branch <b>, so `main` can
#   carry only the caller. --check reads `kit_branch:` from the caller and prints one verdict per branch.
# Needs git and python3. It never commits.
set -eu
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SQ="$(cd "$HERE/.." && pwd -P)"
usage() { echo "usage: adopt.sh <child-path> [--ref <tag-or-sha>] [--kit-branch <branch>] [--check] [--platforms android,ios[,web]] [--milestone D0..D6] [--coder <acct[,acct]> --reviewer <acct[,acct]> --owner <acct>]" >&2; exit 2; }
child=""; ref=HEAD; check_mode=""; coder=""; reviewer=""; owner_acct=""; kit=""; platforms=""; milestone=""
while [ $# -gt 0 ]; do
  case "$1" in
    --ref) [ -n "${2:-}" ] || usage; ref="$2"; shift 2 ;;
    --kit-branch) [ -n "${2:-}" ] || usage; kit="$2"; shift 2 ;;
    --check) check_mode=1; shift ;;
    --milestone) [ -n "${2:-}" ] || usage; milestone="$2"; shift 2 ;;
    --platforms) [ -n "${2:-}" ] || usage; platforms="$2"; shift 2 ;;
    --coder) [ -n "${2:-}" ] || usage; coder="$2"; shift 2 ;;
    --reviewer) [ -n "${2:-}" ] || usage; reviewer="$2"; shift 2 ;;
    --owner) [ -n "${2:-}" ] || usage; owner_acct="$2"; shift 2 ;;
    -*) usage ;;
    *) [ -z "$child" ] || usage; child="$1"; shift ;;
  esac
done
[ -n "$child" ] || usage
[ -d "$child" ] || { echo "adopt.sh: no such folder: $child" >&2; exit 2; }
child="$(cd "$child" && pwd -P)"
top="$(git -C "$child" rev-parse --show-toplevel 2>/dev/null)" || { echo "adopt.sh: $child is not a git repository" >&2; exit 2; }
[ "$(cd "$top" && pwd -P)" = "$child" ] || { echo "adopt.sh: run it on the root of the repository ($top)" >&2; exit 2; }

# story #357: --milestone D0..D6 is written as `milestone:` in the caller; without it the caller's own line is kept. Checked before anything is written.
if [ -n "$milestone" ]; then
  case "$milestone" in D0|D1|D2|D3|D4|D5|D6) ;; *) echo "adopt.sh: unknown milestone '$milestone' (use D0 to D6)" >&2; exit 2 ;; esac
fi

# story #187 (S9): --platforms android,ios[,web] wires the child to the kit's UI libraries (ADR-012). Checked before anything is written.
SNIP="ui/platforms"
rel="$(python3 -c 'import os,sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))' "$SQ" "$child")"
plat_list=""
if [ -n "$platforms" ]; then
  for p in $(printf '%s' "$platforms" | tr ',' ' '); do
    case "$p" in android|ios|web) plat_list="$plat_list $p" ;; *) echo "adopt.sh: unknown platform '$p' (use android, ios or web)" >&2; exit 2 ;; esac
  done
  plat_csv="$(echo $plat_list | tr ' ' ',')"
fi
platform_files() {   # the files one --platforms run writes, one per line
  for p in $plat_list; do case "$p" in
    android) printf '%s\n' "$SNIP/android-settings.snippet.kts" "$SNIP/lint/detekt.yml" "$SNIP/lint/detekt-ci.yml" "$SNIP/lint/UiRulesKonsistTest.kt" ;;
    ios) printf '%s\n' "$SNIP/ios-package.snippet.swift" "$SNIP/lint/swiftlint.yml" ;;
    web) printf '%s\n' "$SNIP/web-astryx.md" ;;
  esac; done
  [ -z "$plat_list" ] || printf '%s\n' "$SNIP/PROTECTED.txt" "$SNIP/KIT_PIN"
}

if [ -n "$kit" ]; then
  why="$(printf 'kit_branch: %s\n' "$kit" | python3 "$HERE/kit_branch.py" parse)" || { echo "adopt.sh: $why" >&2; exit 2; }
fi
call="$child/.github/workflows/shipquick-call.yml"
# story #225: with no --kit-branch, the caller's own kit_branch is kept (one parser: scripts/kit_branch.py)
if [ -z "$kit" ] && [ -f "$call" ]; then
  if ! kit="$(python3 "$HERE/kit_branch.py" parse < "$call")"; then
    if [ -n "$check_mode" ]; then echo "not adopted: shipquick-call.yml: $kit"; exit 1; fi
    echo "adopt.sh: shipquick-call.yml: $kit (fix the line, or pass --kit-branch <branch>)" >&2; exit 2
  fi
fi

gh_repo="$(git -C "$child" remote get-url origin 2>/dev/null | sed -n 's#.*github\.com[:/]\([^/]*/[^/]*\)$#\1#p' | sed 's#\.git$##')"

if [ -n "$check_mode" ]; then
  ok=1
  # story #260: the gate must be a required check on the default branch, or a red gate can still be merged
  if [ -z "$gh_repo" ]; then
    echo "not adopted: gate not required, or unknown: no GitHub origin remote, so the default branch's required checks cannot be read"
    ok=0
  elif ! why="$(python3 "$HERE/kit_branch.py" gate "$gh_repo")"; then
    echo "not adopted: $why"
    ok=0
  fi
  # story #225: the caller sits on this branch; the pin and the hooks sit on its kit branch (HEAD when none).
  if [ -n "$kit" ]; then
    if [ -z "$gh_repo" ]; then
      echo "not adopted: no GitHub origin remote, so the protection of kit branch $kit cannot be checked"
      ok=0
    elif ! why="$(python3 "$HERE/kit_branch.py" protection "$gh_repo" "$kit")"; then
      echo "not adopted: $why"
      ok=0
    fi
  fi
  here="$(git -C "$child" symbolic-ref -q --short HEAD || echo HEAD)"
  kref=HEAD; at="at HEAD"
  if [ -n "$kit" ] && [ "$kit" != "$here" ]; then
    at="on $kit"
    kref="$(git -C "$child" rev-parse -q --verify "refs/heads/$kit^{commit}" || git -C "$child" rev-parse -q --verify "refs/remotes/origin/$kit^{commit}" || true)"
    if [ -z "$kref" ]; then
      echo "not adopted: kit branch $kit not found (run: git fetch origin $kit)"
      exit 1
    fi
  fi
  sub_sha="$(git -C "$child" rev-parse -q --verify "$kref:knowledge/shipquick_latest" 2>/dev/null || true)"
  pinned=""
  if [ ! -f "$call" ]; then
    echo "not adopted: no .github/workflows/shipquick-call.yml (run: bash $HERE/adopt.sh $child)"
    ok=0
  elif [ -z "$sub_sha" ]; then
    echo "not adopted: no knowledge/shipquick_latest submodule found $at"
    ok=0
  else
    pinned="$(sed -n 's/^[[:space:]]*shipquick_ref:[[:space:]]*//p' "$call" | head -1 | tr -d "[:space:]'\"")"
    if [ "$pinned" != "$sub_sha" ]; then
      echo "not adopted: shipquick-call.yml is pinned to $pinned, the submodule $at is at $sub_sha (run: bash $HERE/adopt.sh $child)"
      ok=0
    fi
  fi
  if [ "$kref" = HEAD ]; then hooks="$(cat "$child/.pre-commit-config.yaml" 2>/dev/null || true)"
  else hooks="$(git -C "$child" show "$kref:.pre-commit-config.yaml" 2>/dev/null || true)"; fi
  if ! printf '%s' "$hooks" | grep -q "check_local.sh"; then
    echo "not adopted: .pre-commit-config.yaml$([ "$kref" = HEAD ] || echo " $at") has no ShipQuick hooks (run: bash $HERE/adopt.sh $child)"
    ok=0
  fi
  if [ -n "$plat_list" ]; then
    miss=""
    while read -r f; do [ -f "$child/$f" ] || miss="$miss $f"; done < <(platform_files)
    if [ -n "$miss" ]; then
      echo "platforms: not ready, missing:$miss (run: bash $rel/scripts/adopt.sh $child --platforms $platforms)"; ok=0
    else
      # the pin is the caller's shipquick_ref (no submodule needed for this line)
      call_pin="$(sed -n 's/^[[:space:]]*shipquick_ref:[[:space:]]*//p' "$call" 2>/dev/null | head -1 | tr -d "[:space:]'\"")"
      if [ "$(tr -d '[:space:]' < "$child/$SNIP/KIT_PIN")" != "$call_pin" ] || [ -z "$call_pin" ]; then
        echo "platforms: not ready, $SNIP/KIT_PIN is not the pinned kit commit ${call_pin:-(no pin)} (run: bash $rel/scripts/adopt.sh $child --platforms $platforms)"; ok=0
      else
        echo "platforms: OK $plat_csv"
      fi
    fi
  fi
  # story #326 (A10): the Ponytail plugin must be on in the Claude settings. CI has no settings file, so there it only warns.
  # shortcut: reads only enabledPlugins["ponytail@ponytail"], not the plugin's own install state; upgrade when Claude Code exposes one.
  ponytail_settings="${SHIPQUICK_CLAUDE_SETTINGS:-$HOME/.claude/settings.json}"
  if ! python3 -c 'import json,sys
try:
    on = json.load(open(sys.argv[1], encoding="utf-8")).get("enabledPlugins", {}).get("ponytail@ponytail") is True
except (OSError, ValueError, AttributeError):
    on = False
sys.exit(0 if on else 1)' "$ponytail_settings"; then
    if [ -n "${CI:-}" ]; then echo "warning: the Ponytail plugin is not enabled in $ponytail_settings (CI has no settings file, so the check still passes)"
    else echo "not adopted: the Ponytail plugin is not enabled in $ponytail_settings"; ok=0; fi
    echo "  /plugin marketplace add dietrichgebert/ponytail"
    echo "  /plugin install ponytail@ponytail"
  fi
  if [ "$ok" = 1 ]; then
    if [ "$kref" = HEAD ]; then echo "adopted: pinned to $sub_sha, pre-commit hooks present"
    else
      echo "$here: adopted, shipquick-call.yml pinned to $pinned, kit_branch $kit"
      echo "$kit: adopted, submodule at $sub_sha, pre-commit hooks present"
    fi
  fi
  exit $((1 - ok))
fi

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

# 0. broken shipquick-rules markers in the child's CLAUDE.md stop the run before anything is written (story #316).
if [ -f "$child/CLAUDE.md" ] && ! python3 - "$child/CLAUDE.md" <<'PYEOF'
import sys
S, E = "<!-- shipquick-rules:start -->", "<!-- shipquick-rules:end -->"
t = open(sys.argv[1], encoding="utf-8").read()
ok = (t.count(S) == 0 and t.count(E) == 0) or (t.count(S) == 1 and t.count(E) == 1 and t.index(S) < t.index(E))
sys.exit(0 if ok else 1)
PYEOF
then echo "adopt.sh: CLAUDE.md has broken shipquick-rules markers (one start line above one end line, or neither). Nothing was written. Fix it by hand and run again." >&2; exit 2; fi

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
  ci_name="$(sed -n "s/^name: *[\"']\{0,1\}\([^\"']*[^\"' ]\)[\"']\{0,1\} *\$/\1/p" "$child/.github/workflows/ci.yml" | head -1)"
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

# 2b. the ShipQuick checks caller (story #124): same pinning, triggered on every pull_request
ms="$milestone"
if [ -z "$ms" ] && [ -f "$child/.github/workflows/shipquick-call.yml" ]; then   # story #357: keep the caller's own milestone
  ms="$(sed -nE 's/^[[:space:]]+milestone:[[:space:]]*(D[0-6])[[:space:]]*$/\1/p' "$child/.github/workflows/shipquick-call.yml" | head -1)"
fi
python3 - "$SQ/.github/workflows/shipquick-call.yml" "$sha" "$tag" "$kit" "$ms" > "$tmp/checkscall" <<'PYEOF'
import sys
src, sha, tag, kit, ms = sys.argv[1:6]
lines = [l for l in open(src, encoding="utf-8").read().splitlines() if not l.startswith("#")]
out = ["# The ShipQuick checks every pull request needs (added by ShipQuick scripts/adopt.sh): a call to the reusable workflow, pinned to one commit.",
       "# To move to a newer ShipQuick release, run adopt.sh again with --ref <tag>: it changes `uses:` and `shipquick_ref` together."]
for l in lines:
    if l.strip() == "workflow_dispatch:":
        out.append("  pull_request:")
        continue
    l = l.replace("uses: ./.github/workflows/checks.yml", f"uses: satvik-jain-iitd/shipquick_latest/.github/workflows/checks.yml@{sha}" + (f" # {tag}" if tag else ""))
    l = l.replace("shipquick_ref: ${{ github.sha }}", f"shipquick_ref: {sha}")
    out.append(l)
    if kit and l.strip().startswith("shipquick_ref:"):   # story #225: pin and hooks live on this branch
        out.append(l[: len(l) - len(l.lstrip())] + f"kit_branch: {kit}")
    if ms and l.strip().startswith("shipquick_ref:"):   # story #357: the child's milestone, read by the environments job
        out.append(l[: len(l) - len(l.lstrip())] + f"milestone: {ms}")
print("\n".join(out))
PYEOF
put .github/workflows/shipquick-call.yml < "$tmp/checkscall"

# 3. roadmap.json: a stub only if there is none
if [ -e "$child/roadmap.json" ]; then echo "kept      roadmap.json (yours)"
else
  python3 -c 'import json,sys; print(json.dumps({"title": sys.argv[1], "vision": "Write one line here: the end goal, in words a stranger understands."}, indent=2))' "$(basename "$child")" | put roadmap.json
  echo "note: roadmap.json is a stub. Write the vision line before the page goes live."
fi

# 4. the /mode command
put .claude/commands/mode.md < "$SQ/.claude/commands/mode.md"

# 4b. scripts/screens.sh (story #146, docs/SCREENS.md): generic, always kept in sync like mode.md.
# docs/screens.txt is a stub only if there is none -- its content (which screens, which viewport) is
# always the project's own.
put scripts/screens.sh < "$SQ/scripts/screens.sh"
chmod +x "$child/scripts/screens.sh"
if [ -e "$child/docs/screens.txt" ]; then echo "kept      docs/screens.txt (yours)"
else
  printf '%s\n' \
    "# The screens this project renders and compares on every PR (story #146, docs/SCREENS.md)." \
    "# One screen per line: name | path | viewport (WxH) | setup step. # comments and blanks ignored." \
    "# Empty for now: fill it in once you have a Playwright spec (start from docs/templates/screens.spec.ts)." \
    | put docs/screens.txt
fi

# 5. the pre-commit hooks
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
        stages: [pre-push]
      - id: session-trailer
        name: Add Built-by <session> to the commit message (ADR-011)
        entry: bash $rel/scripts/session_trailer.sh
        language: system
        always_run: true
        stages: [prepare-commit-msg]"
if [ -e "$child/.pre-commit-config.yaml" ] && grep -q "check_local.sh" "$child/.pre-commit-config.yaml"; then
  echo "unchanged .pre-commit-config.yaml (has the ShipQuick hooks)"
elif [ -e "$child/.pre-commit-config.yaml" ]; then
  echo "kept      .pre-commit-config.yaml (yours). Add this line at the top so pre-commit install sets every stage:"
  echo "default_install_hook_types: [pre-commit, commit-msg, pre-push, prepare-commit-msg]"
  echo "and this under repos: to run the ShipQuick checks (scripts/check_local.sh):"
  echo "$hooks"
else
  printf 'default_install_hook_types: [pre-commit, commit-msg, pre-push, prepare-commit-msg]\nrepos:\n%s\n' "$hooks" | put .pre-commit-config.yaml
fi

# 6. CLAUDE.md: one pointer line to the protocol. A new file starts from the template; yours keeps every line.
ptr="follow $rel/CLAUDE.md"
if [ ! -e "$child/CLAUDE.md" ]; then
  sed "s#follow knowledge/shipquick_latest/CLAUDE.md#$ptr#; s#^\# <project>:#\# $(basename "$child"):#" "$SQ/docs/CLAUDE.project.template.md" | put CLAUDE.md
elif grep -qF "$ptr" "$child/CLAUDE.md"; then echo "unchanged CLAUDE.md (has the pointer)"
else
  awk -v ptr="Protocol: $ptr" 'NR==1 && /^#/ {print; print ""; print ptr; next} NR==1 {print ptr; print ""} {print}' "$child/CLAUDE.md" | put CLAUDE.md
fi

# 6b. the kit rule block between the markers (story #316). Written on every run, so a pin bump refreshes the copy.
# What sits outside the markers is the child's own. Broken markers stop the run and change nothing.
if ! python3 - "$SQ/CLAUDE.md" "$child/CLAUDE.md" > "$tmp/claude-rules" <<'PYEOF'
import sys
START, END = "<!-- shipquick-rules:start -->", "<!-- shipquick-rules:end -->"
kit = open(sys.argv[1], encoding="utf-8").read().replace("\r\n", "\n").splitlines()
first = next(i for i, line in enumerate(kit) if line.startswith("0. "))
block = "\n".join(kit[first:]).strip()
text = open(sys.argv[2], encoding="utf-8").read().replace("\r\n", "\n")
if text.count(START) == 0 and text.count(END) == 0:
    sys.stdout.write(text.rstrip("\n") + "\n\n" + START + "\n\n" + block + "\n\n" + END + "\n")
elif text.count(START) == 1 and text.count(END) == 1 and text.index(START) < text.index(END):
    head, rest = text.split(START, 1)
    tail = rest.split(END, 1)[1]
    sys.stdout.write(head + START + "\n\n" + block + "\n\n" + END + tail)
else:
    sys.exit(1)
PYEOF
then echo "adopt.sh: CLAUDE.md has broken shipquick-rules markers (one start line above one end line, or neither). Fix it by hand and run again." >&2; exit 2; fi
put CLAUDE.md < "$tmp/claude-rules"

# 7. .shipquick/roles.yml: which accounts may code, review, and who owns this project (story #140)
if [ -e "$child/.shipquick/roles.yml" ]; then
  echo "kept      .shipquick/roles.yml (yours)"
elif [ -n "$coder" ] && [ -n "$reviewer" ] && [ -n "$owner_acct" ]; then
  sq_remote="$(git -C "$SQ" remote get-url origin 2>/dev/null || true)"
  sq_repo="$(printf '%s\n' "$sq_remote" | sed -n 's#.*[:/]\([^/][^/]*/[^/][^/]*\)\.git$#\1#p' | head -1)"
  [ -n "$sq_repo" ] || sq_repo="satvik-jain-iitd/shipquick_latest"
  {
    echo "coder:"; printf '%s\n' "$coder" | tr ',' '\n' | sed 's/^/  - /'
    echo "reviewer:"; printf '%s\n' "$reviewer" | tr ',' '\n' | sed 's/^/  - /'
    echo "owner: $owner_acct"
    echo "shipquick_repo: $sq_repo"
  } | put .shipquick/roles.yml
else
  echo "note: .shipquick/roles.yml not written -- rerun with --coder <acct[,acct]> --reviewer <acct[,acct]> --owner <acct>, or fill it by hand. CI's roles job and scripts/review_merge.sh both refuse to merge until it exists."
fi

# 8. story #187 (S9): the platform wiring. Snippets point into the kit (no new submodule); the lint configs are copied for the child's CI.
if [ -n "$plat_list" ]; then
  for p in $plat_list; do case "$p" in
    android)
      printf '%s\n' '// ShipQuick (story S9): add this line in settings.gradle.kts, inside the settings block.' 'includeBuild("knowledge/shipquick_latest/ui/android")' | put "$SNIP/android-settings.snippet.kts"
      for f in detekt.yml detekt-ci.yml UiRulesKonsistTest.kt; do cat "$SQ/ui/android/lint/$f" | put "$SNIP/lint/$f"; done ;;
    ios)
      printf '%s\n' '// ShipQuick (story S9): add this line to the dependencies of your Package.swift.' '.package(path: "knowledge/shipquick_latest/ui/ios")' | put "$SNIP/ios-package.snippet.swift"
      cat "$SQ/ui/ios/lint/swiftlint.yml" | put "$SNIP/lint/swiftlint.yml" ;;
    web)
      printf '%s\n' '# Web (Astryx)' '' 'The kit runs Astryx in CI only: a job runs `npm ci --ignore-scripts` in `knowledge/shipquick_latest/ui/tool`, then:' '' '    bash knowledge/shipquick_latest/scripts/ui.sh init' '' 'Nothing installs on a Mac (owner rule 21).' | put "$SNIP/web-astryx.md" ;;
  esac; done
  printf '%s\n' '# Paths a child should protect: a PR may not loosen its own lint (the child adds these to its own protected list).' 'ui/platforms/lint/*' '.swiftlint.yml' 'detekt*.yml' 'ui/platforms/KIT_PIN' | put "$SNIP/PROTECTED.txt"
  printf '%s\n' "$sha" | put "$SNIP/KIT_PIN"
  echo "ui: run once in CI, not on this Mac: bash $rel/scripts/ui.sh init (after npm ci --ignore-scripts in $rel/ui/tool)"
fi

echo "Next: look at git status, commit these files, and merge them into the default branch (scheduled and issue runs start only from there)."
echo "The ShipQuick checks compare with origin/dev. If your default branch is main, run them as: BASE=main bash $rel/scripts/check_local.sh (the base checks are skipped otherwise)."
echo "Then make the gate a required check on your default branch. adopt.sh never runs this; a repo admin runs it once:"
echo "  $(python3 "$HERE/kit_branch.py" gate-command "${gh_repo:-<owner>/<repo>}")"
echo "If a branch of yours was made before .gitattributes existed, its first merge of the default branch needs the .git/info/attributes step in pm/agile/templates/sprint-lanes.md."
