#!/usr/bin/env bash
# One command to adopt ShipQuick in a child project (story #68). Run it from the ShipQuick checkout (in a child: knowledge/shipquick_latest):
#   bash knowledge/shipquick_latest/scripts/adopt.sh . [--ref <tag-or-sha>]
# It copies or updates seven things in the child repo and prints what it did (created / updated / unchanged / kept). A second run changes nothing.
#   .gitattributes                      adds the merge=union lines for the append-only logs; your own lines stay
#   .github/workflows/roadmap-call.yml  the roadmap caller, pinned to this checkout's commit (or --ref), with your ci.yml's `name:` for workflow_run
#   .github/workflows/shipquick-call.yml the PR checks caller (story #124), pinned the same way, triggered on every pull_request
#   roadmap.json                        a stub (title, vision) only if you have none; yours is never overwritten
#   .claude/commands/mode.md            the /mode command; one you changed on purpose is kept (an older kit copy is updated)
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
#   Story #175: the caller must also grant `issues: read`, or the story job cannot read the linked stories.
#   A normal run prints the one command that makes it required; adopt.sh never runs it.
#   Story #326: --check also needs enabledPlugins["ponytail@ponytail"] true in ~/.claude/settings.json (or $SHIPQUICK_CLAUDE_SETTINGS);
#   when it is not, the two install lines are printed and the verdict is not adopted. With CI set it only warns.
# --kit-branch <b> (story #225, rule-24 children): writes `kit_branch: <b>` into shipquick-call.yml. The checks
#   then read the submodule pin, .pre-commit-config.yaml and .shipquick/roles.yml from branch <b>, so `main` can
#   carry only the caller. --check reads `kit_branch:` from the caller and prints one verdict per branch.
# --gate-files (story #479, ADR-017): on a code branch of a kit-branch child, copies the gate files (scripts/gate_files.txt)
#   from the kit branch and stages them. No document is written. --check on such a branch fails for each gate file that is
#   missing, different from the kit branch copy, or only on this branch. It compares the file on disk and reads the hook
#   config from this branch. A bump branch cut from the kit branch is read at HEAD and not compared.
# Needs git and python3. It never commits.
set -eu
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SQ="$(cd "$HERE/.." && pwd -P)"
usage() { echo "usage: adopt.sh <child-path> [--ref <tag-or-sha>] [--kit-branch <branch>] [--check] [--gate-files] [--platforms android,ios[,web]] [--milestone D0..D6] [--coder <acct[,acct]> --reviewer <acct[,acct]> --owner <acct>]" >&2; exit 2; }
child=""; ref=HEAD; check_mode=""; gate_mode=""; coder=""; reviewer=""; owner_acct=""; kit=""; platforms=""; milestone=""
while [ $# -gt 0 ]; do
  case "$1" in
    --ref) [ -n "${2:-}" ] || usage; ref="$2"; shift 2 ;;
    --kit-branch) [ -n "${2:-}" ] || usage; kit="$2"; shift 2 ;;
    --check) check_mode=1; shift ;;
    --gate-files) gate_mode=1; shift ;;
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
# an existing caller line that is not exactly `  milestone: D0..D6` is refused, never dropped (a dropped line would fall back to the default silently)
existing_call="$child/.github/workflows/shipquick-call.yml"
if [ -z "$milestone" ] && [ -f "$existing_call" ]; then   # with --milestone the flag replaces the line
  badline="$(grep -E '^[[:space:]]+milestone:' "$existing_call" | grep -vE '^[[:space:]]+milestone:[[:space:]]*D[0-6][[:space:]]*$' | head -1 || true)"
  [ -z "$badline" ] || { echo "adopt.sh: shipquick-call.yml: the line '$(printf '%s' "$badline" | sed -E 's/^[[:space:]]+//')' is not 'milestone: D0' to 'milestone: D6' (fix the line, or pass --milestone D<n>)" >&2; exit 2; }
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

# story #420: one way to ask the features reader. feat_val <id> [ref]: returns 0 on, 1 off, 2 the reader failed (message in $FEAT_MSG).
# With a ref, the file is read from that commit of the child (the kit branch), never from the working tree. A reader error is never "on".
feat_val() {
  local root="$child" d="" out rc
  if [ "${2:-HEAD}" != HEAD ]; then
    d="$(mktemp -d)"; mkdir -p "$d/.shipquick"
    git -C "$child" show "$2:.shipquick/features.json" > "$d/.shipquick/features.json" 2>/dev/null || rm -f "$d/.shipquick/features.json"
    root="$d"
  fi
  out="$(python3 "$HERE/features.py" --root "$root" get "$1" 2>&1)"; rc=$?
  [ -z "$d" ] || rm -rf "$d"
  FEAT_MSG="$out"
  case "$rc" in 0) return 0 ;; 1) return 1 ;; *) return 2 ;; esac
}
feat_on() { local rc=0; feat_val "$1" || rc=$?; case $rc in 0) return 0 ;; 1) return 1 ;; *) echo "adopt.sh: $FEAT_MSG" >&2; exit 2 ;; esac; }

[ -z "$check_mode" ] || [ -z "$gate_mode" ] || usage
here="$(git -C "$child" symbolic-ref -q --short HEAD || echo HEAD)"
SUB=knowledge/shipquick_latest
# the kit branch as origin has it; a local branch only when origin's is not here (a local one can be stale). Sets kref and kit_from.
resolve_kit() {
  kit_from="origin/$kit"
  kref="$(git -C "$child" rev-parse -q --verify "refs/remotes/origin/$kit^{commit}" || true)"
  [ -n "$kref" ] && return 0
  kit_from="the local branch $kit, origin/$kit is not fetched"
  kref="$(git -C "$child" rev-parse -q --verify "refs/heads/$kit^{commit}" || true)"
}
# story #479: the gate files list. A missing or empty list is never "nothing to check".
GATE_LIST="$HERE/gate_files.txt"
gate_files() { grep -vE '^(#|[[:space:]]*$)' "$GATE_LIST"; }
if [ -n "$check_mode$gate_mode" ] && { [ ! -r "$GATE_LIST" ] || [ -z "$(gate_files)" ]; }; then
  echo "adopt.sh: $GATE_LIST is missing or lists no file, so the gate files cannot be checked or copied (restore it: git -C $SQ checkout -- scripts/gate_files.txt)" >&2; exit 2
fi
gate_fix="run: bash $HERE/adopt.sh $child --gate-files"
# gate_ids <path>: K = the kit branch copy, H = the copy here, as ids to compare. H is what the hooks read: the file on
# disk. The submodule pin is the index entry. .gitmodules is only its kit entry, so a branch may list its own submodules too.
# shortcut: the kit entry is found by the section name git gives it (the path); a renamed section reads as missing.
gate_ids() {
  case "$1" in
    "$SUB") K="$(git -C "$child" rev-parse -q --verify "$kref:$1" 2>/dev/null || true)"
            H="$(git -C "$child" ls-files -s -- "$1" | awk '{print $2}')" ;;
    .gitmodules) K="$(git -C "$child" config --blob "$kref:$1" --get-regexp "^submodule\.$SUB\." 2>/dev/null | sort || true)"
            H="$(git config -f "$child/$1" --get-regexp "^submodule\.$SUB\." 2>/dev/null | sort || true)" ;;
    *) K="$(git -C "$child" rev-parse -q --verify "$kref:$1" 2>/dev/null || true)"
       H=""; [ ! -f "$child/$1" ] || H="$(git -C "$child" hash-object -- "$1")" ;;
  esac
}

# story #479: put the gate files of the kit branch on this code branch. Staged, never committed; no document is written.
if [ -n "$gate_mode" ]; then
  if [ -z "$kit" ] || [ "$kit" = "$here" ]; then
    echo "adopt.sh: --gate-files is for a code branch of a child whose caller names another kit_branch (this branch: $here, kit_branch: ${kit:-none}). Pass --kit-branch <branch> when this branch has no caller yet." >&2; exit 2
  fi
  resolve_kit
  [ -n "$kref" ] || { echo "adopt.sh: kit branch $kit not found (run: git fetch origin $kit)" >&2; exit 2; }
  # first pass: a path with an uncommitted change that the copy would overwrite stops the run; nothing is written
  dirty=""
  while read -r f; do
    gate_ids "$f"
    { [ -n "$K" ] && [ -n "$H" ] && [ "$K" != "$H" ]; } || continue
    # an edit = the copy on disk is not HEAD's copy (git status would miss a gitignored file); for the pin, a staged change
    if [ "$f" = "$SUB" ]; then git -C "$child" diff --cached --quiet -- "$f" || dirty="$dirty $f"
    elif [ "$f" = .gitmodules ]; then [ "$H" = "$(git -C "$child" config --blob "HEAD:$f" --get-regexp "^submodule\.$SUB\." 2>/dev/null | sort || true)" ] || dirty="$dirty $f"
    elif [ "$H" != "$(git -C "$child" rev-parse -q --verify "HEAD:$f" 2>/dev/null || true)" ]; then dirty="$dirty $f"; fi
  done < <(gate_files)
  [ -z "$dirty" ] || { echo "adopt.sh: uncommitted changes in:$dirty. The copy from $kit would overwrite them. Commit them or put them back (git restore --staged --worktree <path>), then run again. Nothing was written." >&2; exit 2; }
  while read -r f; do
    gate_ids "$f"
    if [ -z "$K" ]; then
      if [ -n "$H" ]; then echo "kept      $f (only on $here, not on $kit: --check calls that a drift)"; else echo "skipped   $f (not on $kit)"; fi
      continue
    fi
    [ "$K" != "$H" ] || { echo "unchanged $f"; continue; }
    word=copied; [ -z "$H" ] || word=replaced; note=""
    case "$f" in
      "$SUB") git -C "$child" update-index --add --cacheinfo "160000,$K,$f" ;;   # checkout does not stage a submodule pin
      .gitmodules)
        if [ ! -f "$child/$f" ]; then git -C "$child" checkout -q "$kref" -- "$f"
        else   # keep the branch's own entries; write the kit entry whole (a key only here would differ for ever)
          git config -f "$child/$f" --remove-section "submodule.$SUB" 2>/dev/null || true
          while read -r key val; do git config -f "$child/$f" "$key" "$val"; done <<< "$K"
          git -C "$child" add -- "$f"; note="; only the $SUB entry, your other entries stay"
        fi ;;
      *) git -C "$child" checkout -q "$kref" -- "$f" ;;
    esac
    printf '%-9s %s (from %s%s)\n' "$word" "$f" "$kit_from" "$note"
  done < <(gate_files)
  echo "Next: run git submodule update --init, then commit these files on $here. The git hooks now run on this branch."
  exit 0
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
  kref=HEAD; at="at HEAD"; kit_from=""
  if [ -n "$kit" ] && [ "$kit" != "$here" ]; then
    resolve_kit
    if [ -z "$kref" ]; then
      echo "not adopted: kit branch $kit not found (run: git fetch origin $kit)"
      exit 1
    fi
    # Kit-branch work (a bump, for example) changes the pin on purpose, so it is read at HEAD like the kit branch and not
    # compared with it. It fails closed: a branch is kit-branch work only when the kit tip is an ancestor of HEAD and no
    # commit in <kit>..HEAD is on another remote branch (every origin branch but the kit branch and this branch's own).
    # Anything else is a code branch and is compared. Never by commit counts (second review of PR #483).
    # shortcut: a clone that fetched only one branch cannot see the other remote branches (docs/follow-ups.md).
    kit_work=""
    if git -C "$child" merge-base --is-ancestor "$kref" HEAD 2>/dev/null; then
      others="$(git -C "$child" for-each-ref --format='%(refname)' refs/remotes/origin/ | grep -vxF -e "refs/remotes/origin/$kit" -e "refs/remotes/origin/$here" -e "refs/remotes/origin/HEAD" || true)"
      n_all="$(git -C "$child" rev-list --count "$kref..HEAD")"
      n_own="$(git -C "$child" rev-list --count HEAD --not "$kref" $others)"
      [ "$n_all" != "$n_own" ] || kit_work=1
    fi
    if [ -n "$kit_work" ]; then
      echo "$here: kit-branch work (cut from $kit_from), read at HEAD like the kit branch"
      kref=HEAD
    else
      at="on $kit"
      # story #479: one rule for every gate file (the pin, the callers, the switches, the roles): the copy here equals
      # the kit branch copy. CI and review_merge.sh read some of them from the kit branch, the hooks read them here.
      while read -r f; do
        gate_ids "$f"
        [ "$K" != "$H" ] || continue
        if [ -z "$H" ]; then echo "not adopted: gate file $f is not on $here, so the git hooks cannot run here ($gate_fix)"
        elif [ -z "$K" ]; then echo "not adopted: gate file $f is on $here but not on kit branch $kit (read from $kit_from). Remove it here, or add it on $kit and then $gate_fix"
        else
          pins=""; [ "$f" != "$SUB" ] || pins=" (the pin here is $H, on $kit $K)"
          echo "not adopted: gate file $f on $here differs from kit branch $kit$pins (read from $kit_from; $gate_fix)"
        fi
        ok=0
      done < <(gate_files)
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
  # story #175: the story job reads the linked issues, so the caller must grant issues: read or write (any permissions block counts),
  # or grant everything with `permissions: read-all` / `write-all`; a trailing `# comment` on the line is fine.
  if [ -f "$call" ] && ! grep -qE '^[[:space:]]+(issues:[[:space:]]*(read|write)|permissions:[[:space:]]*(read|write)-all)([[:space:]]+#.*)?[[:space:]]*$' "$call"; then
    echo "not adopted: shipquick-call.yml grants no issues: read, so the story job cannot read the linked stories (run: bash $HERE/adopt.sh $child)"
    ok=0
  fi
  # story #498: one run per PR, so a new push cancels the old run of the child's checks
  if [ -f "$call" ] && ! grep -qE '^concurrency:' "$call"; then
    echo "not adopted: shipquick-call.yml has no concurrency block (one run per PR; a new push cancels the old run) (run: bash $HERE/adopt.sh $child)"
    ok=0
  fi
  # story #479: the hooks and the switches are read from this branch, where git runs them, never from the kit branch
  hooks="$(cat "$child/.pre-commit-config.yaml" 2>/dev/null || true)"
  hooks_skipped=""
  feat_val pre-commit && fv=0 || fv=$?   # not a bare call: set -e would exit on a 1
  if [ "$fv" = 2 ]; then
    echo "not adopted: .shipquick/features.json: $FEAT_MSG"
    ok=0
  elif [ "$fv" = 1 ]; then
    hooks_skipped=1; echo "hooks skipped: pre-commit is off"
  elif ! printf '%s' "$hooks" | grep -q "check_local.sh"; then
    echo "not adopted: .pre-commit-config.yaml has no ShipQuick hooks (run: bash $HERE/adopt.sh $child)"
    ok=0
  elif ! printf '%s' "$hooks" | grep -q "id: shipquick-kit"; then
    echo "not adopted: .pre-commit-config.yaml has no shipquick-kit hook, so a kit folder that is not checked out stops a commit with a bare shell error (run: bash $HERE/adopt.sh $child)"
    ok=0
  fi
  # story #446: the same three things the child's CI will check on a bump PR, found before the push.
  # (a) the hooks are configured: they must also be installed here, or the commit-msg guard never ran
  if [ -z "$hooks_skipped" ]; then
    hs_rc=0; hs="$(python3 "$SQ/plugin/hooks/hooks_state.py" "$child")" || hs_rc=$?
    case "$hs" in
      missing) echo "not adopted: the git hooks are configured but not installed, so the commit checks never ran here (run: pre-commit install, or: bash $HERE/adopt.sh $child)"; ok=0 ;;
      error) echo "not adopted: cannot tell whether the git hooks are installed (hooks_state.py exit $hs_rc)"; ok=0 ;;
    esac
  fi
  # (b) no commit subject over 72 characters since the base branch (the rule of check_commit_msg.py)
  base=""
  for cand in ${kit:+"origin/$kit"} origin/dev origin/main origin/master; do
    base="$(git -C "$child" rev-parse -q --verify "$cand^{commit}" 2>/dev/null || true)"
    [ -z "$base" ] || break
  done
  if [ -n "$base" ]; then
    while IFS=$'\t' read -r h subj; do
      [ -n "$h" ] || continue
      case "$subj" in "Merge "*) continue ;; esac
      if [ "${#subj}" -gt 72 ]; then echo "not adopted: commit subject over 72 characters (${#subj}): $h $subj (reword it before pushing)"; ok=0; fi
    done < <(git -C "$child" log --no-merges --format='%h%x09%s' "$base..HEAD" 2>/dev/null)
  fi
  # (c) environments at the caller's milestone, with the words CI uses
  cms="$(sed -nE 's/^[[:space:]]+milestone:[[:space:]]*(D[0-6])[[:space:]]*$/\1/p' "$call" 2>/dev/null | head -1)"
  cms="${cms:-D1}"   # a caller with no `milestone:` line gets D1 in CI (checks.yml); --check says the same
  if [ ! -f "$child/CLAUDE.md" ]; then   # CI's environments job fails on a missing file, so --check does too
    # ponytail: on a rule-24 branch that carries only the caller (kit branch elsewhere) the file sits on the kit branch; not read there yet
    if [ -z "$kit" ] || [ "$kit" = "$here" ]; then
      echo "not adopted: environments: no CLAUDE.md in the child (CI reads Dev link and Production link from it)"; ok=0
    fi
  elif ! why="$(bash "$HERE/check_environments.sh" --claude-md "$child/CLAUDE.md" --milestone "$cms" 2>&1)"; then
    echo "not adopted: environments: ${why#check_environments.sh: }"; ok=0
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
    hooks_say="pre-commit hooks present"; [ -z "$hooks_skipped" ] || hooks_say="pre-commit hooks skipped (feature off)"
    if [ "$kref" = HEAD ]; then echo "adopted: pinned to $sub_sha, $hooks_say"
    else
      echo "$here: adopted, shipquick-call.yml pinned to $pinned, kit_branch $kit, gate files equal to $kit (read from $kit_from)"
      echo "$kit: adopted, submodule at $sub_sha, $hooks_say"
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

# 0a. story #420 (F3): the features file. A broken one stops the run before anything is written. Flags read here steer steps 2 and 5.
python3 "$HERE/features.py" --root "$child" sync > "$tmp/features" 2> "$tmp/features.notes" || { echo "adopt.sh: $(cat "$tmp/features.notes")" >&2; exit 2; }

# 0. broken shipquick-rules markers in the child's CLAUDE.md stop the run before anything is written (story #316).
if [ -f "$child/CLAUDE.md" ] && ! python3 - "$child/CLAUDE.md" <<'PYEOF'
import sys
S, E = "<!-- shipquick-rules:start -->", "<!-- shipquick-rules:end -->"
t = open(sys.argv[1], encoding="utf-8").read()
ok = (t.count(S) == 0 and t.count(E) == 0) or (t.count(S) == 1 and t.count(E) == 1 and t.index(S) < t.index(E))
sys.exit(0 if ok else 1)
PYEOF
then echo "adopt.sh: CLAUDE.md has broken shipquick-rules markers (one start line above one end line, or neither). Nothing was written. Fix it by hand and run again." >&2; exit 2; fi

# 0b. the features file itself (computed in 0a)
put .shipquick/features.json < "$tmp/features"
sed 's/^/note      /' "$tmp/features.notes"

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

# 2. the roadmap caller (story #420: only when the `roadmap` feature is on)
if feat_on roadmap; then
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
else echo "skipped: roadmap is off (no roadmap-call.yml written)"; fi

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
        out.append("    types: [opened, synchronize, reopened, edited]")   # story #92: an edited body re-runs the body-reading checks
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

# 4. the /mode command (story #470): written when missing or equal to any older kit copy; a file the child changed on purpose is kept.
# shortcut: the older copies come from the kit's own git history; a kit with no history (a shallow clone) keeps every differing file.
mode=.claude/commands/mode.md
if [ -e "$child/$mode" ] && ! cmp -s "$child/$mode" "$SQ/$mode"; then
  older=0
  for h in $(git -C "$SQ" log --format=%H -- "$mode" 2>/dev/null); do
    git -C "$SQ" show "$h:$mode" 2>/dev/null | cmp -s - "$child/$mode" && { older=1; break; }
  done
  if [ "$older" = 0 ]; then echo "kept      $mode (yours; differs from the kit copy)"; else put "$mode" < "$SQ/$mode"; fi
else
  put "$mode" < "$SQ/$mode"
fi

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
if ! feat_on pre-commit; then echo "skipped: pre-commit is off (no hooks written)"; else
kit_guard="      - id: shipquick-kit
        name: The ShipQuick kit folder is checked out
        entry: bash -c 'test -f $rel/scripts/check_local.sh || { echo \"ShipQuick, the kit folder $rel is not checked out here. Run this, then try again -- git submodule update --init\"; exit 1; }'
        language: system
        pass_filenames: false
        always_run: true
        fail_fast: true
        stages: [pre-commit, pre-push, prepare-commit-msg]"
hooks="  - repo: local
    hooks:
$kit_guard
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
  if grep -q "id: shipquick-kit" "$child/.pre-commit-config.yaml"; then
    echo "unchanged .pre-commit-config.yaml (has the ShipQuick hooks)"
  elif grep -qxF "      - id: check-local" "$child/.pre-commit-config.yaml"; then   # story #479: a config written by an older kit gets the guard, first
    KIT_GUARD="$kit_guard" python3 -c 'import os,sys; t=open(sys.argv[1],encoding="utf-8").read(); open(sys.argv[1],"w",encoding="utf-8").write(t.replace("      - id: check-local\n", os.environ["KIT_GUARD"]+"\n      - id: check-local\n", 1))' "$child/.pre-commit-config.yaml"
    echo "updated   .pre-commit-config.yaml (added the shipquick-kit hook)"
  else
    echo "kept      .pre-commit-config.yaml (yours). Add this hook first under the ShipQuick hooks, so an empty kit folder says how to fix it:"
    echo "$kit_guard"
  fi
elif [ -e "$child/.pre-commit-config.yaml" ]; then
  echo "kept      .pre-commit-config.yaml (yours). Add this line at the top so pre-commit install sets every stage:"
  echo "default_install_hook_types: [pre-commit, commit-msg, pre-push, prepare-commit-msg]"
  echo "and this under repos: to run the ShipQuick checks (scripts/check_local.sh):"
  echo "$hooks"
else
  printf 'default_install_hook_types: [pre-commit, commit-msg, pre-push, prepare-commit-msg]\nrepos:\n%s\n' "$hooks" | put .pre-commit-config.yaml
fi
fi

# 5b. story #446: install the git hooks themselves when they are configured and not installed (it only writes the hooks folder).
# Without them the commit-msg guard never runs here and a bad subject first shows up in CI.
hs_rc=0; hs="$(python3 "$SQ/plugin/hooks/hooks_state.py" "$child")" || hs_rc=$?
case "$hs" in
  installed) echo "unchanged git hooks (pre-commit and commit-msg are installed)" ;;
  missing)
    if ! command -v pre-commit > /dev/null 2>&1; then
      echo "note: the git hooks are not installed and pre-commit is not on this machine. Install it (pip install pre-commit), then run in $child: pre-commit install"
    elif hs_err="$(cd "$child" && pre-commit install 2>&1)"; then
      echo "installed  git hooks (pre-commit install)"
    else
      echo "note: could not install the git hooks ($(printf '%s' "$hs_err" | tail -1)). Run in $child: pre-commit install"
    fi ;;
  error) echo "note: could not tell whether the git hooks are installed (hooks_state.py exit $hs_rc)" ;;
esac
# the config must also ask for the commit-msg hook type, or `pre-commit install` leaves the subject guard out
if [ "$hs" != not-configured ] && [ "$hs" != off ] && ! grep -qE '^default_install_hook_types:.*commit-msg' "$child/.pre-commit-config.yaml" 2>/dev/null; then
  echo "note: .pre-commit-config.yaml has no commit-msg hook type, so the commit subject guard will not run. Add this line at the top: default_install_hook_types: [pre-commit, commit-msg, pre-push, prepare-commit-msg]"
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
