#!/usr/bin/env bash
# The only way an agent merges a pull request (story #67, docs/MODES.md).
# It refuses, with exit 1 and `refused: <rule>`, unless all of this holds:
#   the mode is auto; the PR is open, not a draft, and has no conflicts; the PR's own repo's own `.shipquick/roles.yml`
#   (read from GitHub, never the local checkout -- story #122's lesson) says who may author and who may approve: the
#   PR author is a coder account, and a reviewer account other than the author approved the latest commit (story #140,
#   the #114 case: a PR the reviewer account itself opened is never merged through this script);
#   no review thread is unresolved; every check is SUCCESS (SKIPPED and NEUTRAL count as passed, as on GitHub); the body has `Closes #n` by the same rule as CI (scripts/check_closes.py: release:, chore: and Dependabot pull requests are exempt);
#   and, only when the base branch is main: the PR's own repo's CLAUDE.md (read from GitHub, not the local checkout, which may be a different repo) must be
#   readable or the merge refuses outright; if it has a filled "Dev link:" line (scripts/has_dev_link.sh) the body also needs a followable "## UAT on dev"
#   checklist (scripts/check_uat.py) with every box ticked (story #120, #122); and the PR's own repo's own `.shipquick/freeze` on `main` (read the same
#   way, scripts/check_freeze.py) must be absent, expired-but-still-blocking is still blocking (story #126) -- though in practice any PR that touches
#   `.shipquick/freeze` at all, lift included, is already refused by the protected-paths rule below: lifting a freeze is the owner's decision too.
#   Story #131: a check named exactly `gate` (ShipQuick) or `shipquick-checks / gate` (child) must itself be SUCCESS -- the generic "every check SUCCESS
#   or SKIPPED" loop above cannot be trusted alone, since a PR that deletes a job from its own caller never produces a bad result for that job, it simply
#   has none. And no PR may touch a path in scripts/protected_paths.txt (CI config, lint baselines, path lists a check reads its own rules from) -- those
#   are refused outright in auto mode, "protected path, owner merges", so a check's own rules can never be loosened by the PR that check is judging.
# Then it merges, using the review account's own token (never switch the active gh account), and closes the story issues
# the PR links (`Closes #n`) with scripts/close_linked_issues.py, because GitHub closes them only for a merge into the default branch. Needs git, gh, jq and python3.
# The merge method (story #87): --method squash|rebase|merge wins; with no flag it squashes when the base branch requires linear history
# (GoServe dev, documents and staging refuse a merge commit), and otherwise makes a merge commit as before.
# usage: review_merge.sh <pr-number> [owner/repo] [--method squash|rebase|merge]
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
usage() { echo "usage: review_merge.sh <pr-number> [owner/repo] [--method squash|rebase|merge]" >&2; exit 2; }
method=""; args=()
while [ $# -gt 0 ]; do
  case "$1" in
    --method) [ -n "${2:-}" ] || usage; method="$2"; shift 2 ;;
    -*) usage ;;
    *) args+=("$1"); shift ;;
  esac
done
case "$method" in ""|squash|rebase|merge) ;; *) usage ;; esac
set -- "${args[@]+"${args[@]}"}"
pr="${1:-}"
[[ "$pr" =~ ^[0-9]+$ ]] || usage
refuse() { echo "refused: $1" >&2; exit 1; }

mode=$("$HERE/mode.sh" get 2>/dev/null) || refuse "mode is not set (ask the owner)"
[ "$mode" = auto ] || refuse "mode is $mode (only auto merges)"

repo="${2:-$(gh repo view --json nameWithOwner --jq .nameWithOwner)}"
json=$(gh pr view "$pr" -R "$repo" --json state,isDraft,mergeable,baseRefName,headRefOid,title,author,body,reviews,statusCheckRollup) || refuse "cannot read pull request $pr"
field() { jq -r "$1" <<<"$json"; }

# story #425: the `merge-gate` feature, read as committed on the PR's base branch (never this checkout, which a PR could
# change). Off means no agent merges: the owner merges by hand. An unreadable or broken file takes the same safe side.
gate_rc=0; gate_err=$(python3 "$HERE/features.py" remote merge-gate --repo "$repo" --ref "$(field .baseRefName)" 2>&1 >/dev/null) || gate_rc=$?
case "$gate_rc" in
  0) ;;
  1) refuse "merge gate is off: the owner merges by hand" ;;
  *) refuse "the features file on $(field .baseRefName) cannot be read ($gate_err): the owner merges by hand" ;;
esac

{ [ "$(field .state)" = OPEN ] && [ "$(field .isDraft)" = false ]; } || refuse "pull request is not open, or is a draft"
[ "$(field .mergeable)" != CONFLICTING ] || refuse "pull request has conflicts"

# story #140: who may author and who may approve come from the PR's OWN repo's .shipquick/roles.yml,
# read from GitHub (never the local checkout -- story #122's lesson), not a name hardcoded here.
# Story #225: a rule-24 child names a kit branch in its caller; roles.yml lives there, the same as in the CI roles job.
roles_ref=$(field .baseRefName); roles_where="$roles_ref"
caller_raw=$(gh api "repos/$repo/contents/.github/workflows/shipquick-call.yml?ref=$roles_ref" --jq '.content' 2>/dev/null) || caller_raw=""
if [ -n "$caller_raw" ]; then
  kit=$(printf '%s' "$caller_raw" | base64 -d 2>/dev/null | python3 "$HERE/kit_branch.py" parse) || refuse "$repo's shipquick-call.yml on $roles_ref: $kit"
  if [ -n "$kit" ] && [ "$kit" != "$roles_ref" ]; then roles_ref="$kit"; roles_where="kit branch $kit"; fi
fi
roles_raw=$(gh api "repos/$repo/contents/.shipquick/roles.yml?ref=$roles_ref" --jq '.content' 2>/dev/null)
roles_rc=$?
[ "$roles_rc" -eq 0 ] && [ -n "$roles_raw" ] || refuse "cannot read $repo's .shipquick/roles.yml on $roles_where to check roles"
roles_tmp="$(mktemp)"
printf '%s' "$roles_raw" | base64 -d > "$roles_tmp" 2>/dev/null
coders=$(python3 "$HERE/roles.py" get coder --file "$roles_tmp") || refuse "cannot read coder accounts from $repo's .shipquick/roles.yml"
reviewers=$(python3 "$HERE/roles.py" get reviewer --file "$roles_tmp") || refuse "cannot read reviewer accounts from $repo's .shipquick/roles.yml"
reviewer_sessions=$(python3 "$HERE/roles.py" get reviewer_sessions --file "$roles_tmp") || refuse "cannot read reviewer sessions from $repo's .shipquick/roles.yml"
rm -f "$roles_tmp"

author=$(field .author.login)
case "$author" in
  dependabot\[bot\]|app/dependabot) ;;   # exempt, same as check_closes.py and team-block
  *) printf ',%s,' "$coders" | grep -qF ",$author," || refuse "PR author $author is not a coder account" ;;
esac

reviewer_account=$(jq -r --arg revs "$reviewers" --arg author "$author" --arg head "$(field .headRefOid)" '
  ($revs | split(",")) as $rs
  | [.reviews[] | select(.author.login as $a | ($rs | index($a)) != null and $a != $author and (.state == "APPROVED" or .state == "CHANGES_REQUESTED" or .state == "DISMISSED"))]
  | group_by(.author.login) | map(last)
  | map(select(.state == "APPROVED" and .commit.oid == $head))
  | if length > 0 then .[0].author.login else "" end
' <<<"$json")
[ -n "$reviewer_account" ] || refuse "not approved by a reviewer account (other than the author, $author) on the latest commit"

# story #318 (A4b): the approving review must say what it decided and what it did not check. Both are whole lines.
approval_body=$(jq -r --arg r "$reviewer_account" --arg head "$(field .headRefOid)" \
  '[.reviews[] | select(.author.login == $r and .state == "APPROVED" and .commit.oid == $head)] | last | .body // ""' <<<"$json" | tr -d '\r')
grep -q '^Verdict:' <<<"$approval_body" || refuse "the approving review has no \`Verdict:\` line"
grep -q '^Not checked:' <<<"$approval_body" || refuse "the approving review has no \`Not checked:\` line"

# story #139 (ADR-011): maker and checker are different SESSIONS, not only different accounts. Opt-in:
# only when roles.yml lists reviewer_sessions. The approving review names its session; that session must
# not appear in any non-merge commit's Built-by: trailer (merge commits are exempt, ADR-011).
if [ -n "$reviewer_sessions" ]; then
  commits=$(gh api "repos/$repo/pulls/$pr/commits" --paginate) || refuse "cannot read the commits of pull request $pr"
  built_by=$(jq -rs '[.[][] | select((.parents | length) < 2) | .commit.message | capture("(?m)^Built-by:\\s*(?<s>\\S+)"; "g").s] | unique | join(",")' <<<"$commits")
  review_body="$(mktemp)"
  jq -r --arg r "$reviewer_account" --arg head "$(field .headRefOid)" \
    '[.reviews[] | select(.author.login == $r and .state == "APPROVED" and .commit.oid == $head)] | last | .body // ""' <<<"$json" > "$review_body"
  why=$(python3 "$HERE/check_roles.py" --review-body-file "$review_body" --built-by "$built_by" --reviewer-sessions "$reviewer_sessions") \
    || { rm -f "$review_body"; refuse "$why"; }
  rm -f "$review_body"
fi

# story #153: when the PR's own repo has configured docs/screens.txt (read from GitHub, 404 = not configured),
# the approving review's body must say the render was compared with the PR's named board.
if field .body | grep -qE '^Design board:'; then
  err_tmp="$(mktemp)"
  screens_raw=$(gh api "repos/$repo/contents/docs/screens.txt?ref=$(field .baseRefName)" --jq '.content' 2>"$err_tmp")
  screens_rc=$?
  [ "$screens_rc" -eq 0 ] || grep -q "404" "$err_tmp" || refuse "cannot read $repo's docs/screens.txt on $(field .baseRefName) to check the design review"
  rm -f "$err_tmp"
  if [ "$screens_rc" -eq 0 ] && printf '%s' "$screens_raw" | base64 -d 2>/dev/null | grep -qvE '^[[:space:]]*(#|$)'; then
    pr_body_tmp="$(mktemp)"; review_tmp="$(mktemp)"
    field .body > "$pr_body_tmp"
    # each reviewer account's latest verdict, kept when it approves the head commit: any one may carry the matches line
    jq -r --arg revs "$reviewers" --arg author "$author" --arg head "$(field .headRefOid)" '($revs | split(",")) as $rs
      | [.reviews[] | select(.author.login as $a | ($rs | index($a)) != null and $a != $author and (.state == "APPROVED" or .state == "CHANGES_REQUESTED" or .state == "DISMISSED"))]
      | group_by(.author.login) | map(last) | .[] | select(.state == "APPROVED" and .commit.oid == $head) | .body // ""' <<<"$json" > "$review_tmp"
    why=$(python3 "$HERE/check_design_reviewed.py" --pr-body-file "$pr_body_tmp" --review-body-file "$review_tmp")
    design_rc=$?
    rm -f "$pr_body_tmp" "$review_tmp"
    [ "$design_rc" -eq 0 ] || refuse "$why"
  fi
fi

threads=$(gh api graphql -f query='query($owner: String!, $name: String!, $n: Int!) { repository(owner: $owner, name: $name) { pullRequest(number: $n) { reviewThreads(first: 100) { pageInfo { hasNextPage } nodes { isResolved } } } } }' \
  -f owner="${repo%/*}" -f name="${repo#*/}" -F n="$pr") || refuse "cannot read the review threads"
[ "$(jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.hasNextPage // false' <<<"$threads")" = false ] || refuse "more than 100 review threads (resolve some first)"
open=$(jq '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false)] | length' <<<"$threads")
[ "$open" = 0 ] || refuse "$open unresolved review threads"

[ "$(field '.statusCheckRollup | length')" -gt 0 ] || refuse "no checks ran"
# A check name can carry more than one run (a rerun, a close/reopen, a stale suite from an earlier commit): only its latest run by startedAt counts.
bad=$(jq -r '
  .statusCheckRollup
  | sort_by(.name // .context)
  | group_by(.name // .context)
  | map(max_by(.startedAt // .completedAt // ""))
  | .[]
  | select(((.conclusion // .state // "") | ascii_upcase) as $c | $c != "SUCCESS" and $c != "SKIPPED" and $c != "NEUTRAL")
  | (.name // .context)
' <<<"$json" | head -1)
[ -z "$bad" ] || refuse "check $bad is not SUCCESS"

# story #131: the generic loop above cannot be trusted alone (a deleted job leaves no bad result at all),
# so a check literally named `gate` or `shipquick-checks / gate` must exist and itself be SUCCESS.
gate_name=$(jq -r '.statusCheckRollup[] | (.name // .context)' <<<"$json" | grep -xE 'gate|shipquick-checks / gate' | head -1)
[ -n "$gate_name" ] || refuse "no required check named exactly gate or shipquick-checks / gate ran"
gate_concl=$(jq -r --arg n "$gate_name" '
  .statusCheckRollup
  | sort_by(.name // .context)
  | group_by(.name // .context)
  | map(max_by(.startedAt // .completedAt // ""))
  | .[]
  | select((.name // .context) == $n)
  | ((.conclusion // .state // "") | ascii_upcase)
' <<<"$json" | head -1)
[ "$gate_concl" = SUCCESS ] || refuse "required check $gate_name is $gate_concl, not SUCCESS"

# story #424: the `close-on-merge` flag is read as committed on the PR's base branch, never from this checkout; any error refuses.
base_ref=$(field .baseRefName); cm_rc=0
python3 "$HERE/features.py" remote close-on-merge --repo "$repo" --ref "$base_ref" >/dev/null 2>"${TMPDIR:-/tmp}/rm_feat.$$" || cm_rc=$?
case "$cm_rc" in
  0) cm=on ;;
  1) cm=off ;;
  *) why=$(cat "${TMPDIR:-/tmp}/rm_feat.$$"); rm -f "${TMPDIR:-/tmp}/rm_feat.$$"; refuse "the features file on $base_ref cannot be read, so close-on-merge is unknown: $why" ;;
esac
rm -f "${TMPDIR:-/tmp}/rm_feat.$$"
why=$(field .body | python3 "$HERE/check_closes.py" --close-on-merge "$cm" --title "$(field .title)" --author "$(field .author.login)") || refuse "no \`Closes #n\` in the body (same rule as CI: $why)"

token=$(gh auth token --user "$reviewer_account") || refuse "no token for $reviewer_account on this machine"

# story #131: a PR touching any protected path (CI config, lint baselines, path lists a check reads
# its own rules from) is never merged in auto mode -- the owner merges it by hand.
protected_match() {   # protected_match <changed-file> -- true if it matches a line of protected_paths.txt
  local f="$1" pat
  while IFS= read -r pat; do
    pat="${pat%%#*}"; pat="$(printf '%s' "$pat" | sed -E 's/^[[:space:]]+|[[:space:]]+$//g')"
    [ -z "$pat" ] && continue
    [[ "$f" == $pat ]] && return 0
  done < "$HERE/protected_paths.txt"
  return 1
}
files_json=$(GH_TOKEN="$token" gh api "repos/$repo/pulls/$pr/files" --paginate) || refuse "cannot read changed files"
# story #126's lift-the-freeze exemption lives only in the freeze check below, never here: lifting a
# freeze is the owner's decision too, so .shipquick/* (including .shipquick/freeze) is protected with
# no exception -- a lift-only PR still needs the owner's own merge (review blocker on PR #141).
only_lifts_freeze=$(jq -r 'if length == 1 and .[0].filename == ".shipquick/freeze" and .[0].status == "removed" then "yes" else "no" end' <<<"$files_json")
bad_path=""
while IFS= read -r f; do
  [ -z "$f" ] && continue
  if protected_match "$f"; then bad_path="$f"; break; fi
done < <(jq -r '.[] | .filename, (.previous_filename // empty)' <<<"$files_json")   # a rename away from a protected path is still protected
# story #180 (S0, ADR-013): a protected PR may merge here only when the approving review on the head
# records a second review and the owner's own yes. `.shipquick/*` (mode, roles, freeze) never: the owner merges it.
if [ -n "$bad_path" ]; then
  shipquick_file=$(jq -r '.[] | .filename, (.previous_filename // empty) | select(startswith(".shipquick/"))' <<<"$files_json" | head -1)
  [ -z "$shipquick_file" ] || refuse "protected path, owner merges ($shipquick_file: mode, roles and freeze are the owner's own merge)"
  approval=$(jq -r --arg r "$reviewer_account" --arg head "$(field .headRefOid)" \
    '[.reviews[] | select(.author.login == $r and .state == "APPROVED" and .commit.oid == $head)] | last | .body // ""' <<<"$json" | tr -d '\r')
  # a placeholder (<...>) or a few letters is not a second review; the yes is a real date, today or up to 14 days back
  grep -E '^Second review: ' <<<"$approval" | grep -vE '<[^>]*>' | grep -qE '^Second review: .{10,}' \
    && grep -E '^Second review: ' <<<"$approval" | sed 's/^Second review: //' | grep -qE '[[:alnum:]]{2,}([^[:alnum:]]+[[:alnum:]]{2,}){2,}' \
    || refuse "protected path, owner merges ($bad_path) -- or the approving review records 'Second review: <who, findings>'"
  python3 -c 'import datetime as d, re, sys
m = [re.fullmatch(r"Owner yes: (\d{4}-\d{2}-\d{2}) \"(?=[^\"]*[^\W\d_])([^\"<>]{2,})\"\s*", l) for l in sys.stdin.read().splitlines()]
m = next((x for x in m if x), None)
try: age = (d.date.today() - d.date.fromisoformat(m[1])).days if m else -1
except ValueError: age = -1
sys.exit(0 if 0 <= age <= 14 else 1)' <<<"$approval" \
    || refuse "protected path, owner merges ($bad_path) -- or the approving review records 'Owner yes: <YYYY-MM-DD> \"<his words>\"' (a real date, at most 14 days old)"
fi

uat_exempt=0
if [ "$(field .baseRefName)" = main ]; then   # read the PR's OWN repo's CLAUDE.md on its base branch (never the local checkout's: it may be a different repo, story #122)
  raw_b64=$(GH_TOKEN="$token" gh api "repos/$repo/contents/CLAUDE.md?ref=$(field .baseRefName)" --jq '.content' 2>/dev/null)
  api_rc=$?
  [ "$api_rc" -eq 0 ] && [ -n "$raw_b64" ] || refuse "cannot read $repo's CLAUDE.md on $(field .baseRefName) to check the UAT gate"
  claude_md_tmp="$(mktemp)"
  printf '%s' "$raw_b64" | base64 -d > "$claude_md_tmp" 2>/dev/null
  "$HERE/has_dev_link.sh" "$claude_md_tmp" || uat_exempt=1
  rm -f "$claude_md_tmp"
fi
if [ "$(field .baseRefName)" = main ] && [ "$uat_exempt" = 0 ]; then   # a dev -> main app promotion is gated on the owner's UAT checklist, story #120
  uat=$(field .body | awk '/^## UAT on dev/{f=1;next} /^## /{f=0} f')
  [ -n "$uat" ] || refuse "a promotion to main needs a \"## UAT on dev (<link>)\" section in the body"
  why=$(printf '%s\n' "$uat" | python3 "$HERE/check_uat.py") || refuse "the UAT checklist is not followable: $why"
  unticked=$(printf '%s\n' "$uat" | grep -c '^- \[ \]' || true)
  [ "$unticked" = 0 ] || refuse "$unticked unticked box(es) in the UAT checklist"
fi

if [ "$(field .baseRefName)" = main ]; then   # story #126: a release freeze blocks every merge into main except a PR that only lifts it
  err_tmp="$(mktemp)"
  freeze_raw=$(GH_TOKEN="$token" gh api "repos/$repo/contents/.shipquick/freeze?ref=$(field .baseRefName)" --jq '.content' 2>"$err_tmp")
  freeze_rc=$?
  [ "$freeze_rc" -eq 0 ] || grep -q "404" "$err_tmp" || refuse "cannot read $repo's .shipquick/freeze on $(field .baseRefName) to check the freeze gate"
  rm -f "$err_tmp"
  if [ "$freeze_rc" -eq 0 ] && [ -n "$freeze_raw" ]; then
    freeze_msg=$(printf '%s' "$freeze_raw" | base64 -d 2>/dev/null | python3 "$HERE/check_freeze.py")
    freeze_blocked=$?
    if [ "$freeze_blocked" = 1 ]; then
      [ "$only_lifts_freeze" = yes ] || refuse "$freeze_msg"
    fi
  fi
fi

if [ -z "$method" ]; then   # no flag: read the base branch's own setting (the reviewer's token can; no protection or no answer means merge, as before)
  linear=$(GH_TOKEN="$token" gh api "repos/$repo/branches/$(field .baseRefName)/protection" --jq '.required_linear_history.enabled' 2>/dev/null || true)
  [ "$linear" = true ] && method=squash || method=merge
fi
GH_TOKEN="$token" gh pr merge "$pr" -R "$repo" "--$method" || { echo "merge failed" >&2; exit 1; }
echo "merged #$pr in $repo"
# The merge cannot be undone, so a failure here is not a refusal: say what to run, and exit 4.
GH_TOKEN="$token" GH_REPO="$repo" python3 "$HERE/close_linked_issues.py" "$pr" --yes || { echo "merged #$pr, but closing its issues failed: run  GH_REPO=$repo python3 scripts/close_linked_issues.py $pr --yes" >&2; exit 4; }
