#!/usr/bin/env bash
# The only way an agent merges a pull request (story #67, docs/MODES.md).
# It refuses, with exit 1 and `refused: <rule>`, unless all of this holds:
#   the mode is auto; the PR is open, not a draft, and has no conflicts; satvik-jain-iitd approved the latest commit;
#   no review thread is unresolved; every check is SUCCESS (SKIPPED and NEUTRAL count as passed, as on GitHub); the body has `Closes #n` by the same rule as CI (scripts/check_closes.py: release:, chore: and Dependabot pull requests are exempt);
#   and, only when the base branch is main: the PR's own repo's CLAUDE.md (read from GitHub, not the local checkout, which may be a different repo) must be
#   readable or the merge refuses outright; if it has a filled "Dev link:" line (scripts/has_dev_link.sh) the body also needs a followable "## UAT on dev"
#   checklist (scripts/check_uat.py) with every box ticked (story #120, #122).
# Then it merges, using the review account's own token (never switch the active gh account), and closes the story issues
# the PR links (`Closes #n`) with scripts/close_linked_issues.py, because GitHub closes them only for a merge into the default branch. Needs git, gh, jq and python3.
# The merge method (story #87): --method squash|rebase|merge wins; with no flag it squashes when the base branch requires linear history
# (GoServe dev, documents and staging refuse a merge commit), and otherwise makes a merge commit as before.
# usage: review_merge.sh <pr-number> [owner/repo] [--method squash|rebase|merge]
set -u
REVIEWER=satvik-jain-iitd
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

{ [ "$(field .state)" = OPEN ] && [ "$(field .isDraft)" = false ]; } || refuse "pull request is not open, or is a draft"
[ "$(field .mergeable)" != CONFLICTING ] || refuse "pull request has conflicts"

last=$(jq -r --arg u "$REVIEWER" '[.reviews[] | select(.author.login == $u and (.state == "APPROVED" or .state == "CHANGES_REQUESTED" or .state == "DISMISSED"))] | last | "\(.state) \(.commit.oid)"' <<<"$json")
[ "$last" = "APPROVED $(field .headRefOid)" ] || refuse "not approved by $REVIEWER on the latest commit"

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

why=$(field .body | python3 "$HERE/check_closes.py" --title "$(field .title)" --author "$(field .author.login)") || refuse "no \`Closes #n\` in the body (same rule as CI: $why)"

token=$(gh auth token --user "$REVIEWER") || refuse "no token for $REVIEWER on this machine"

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

if [ -z "$method" ]; then   # no flag: read the base branch's own setting (the reviewer's token can; no protection or no answer means merge, as before)
  linear=$(GH_TOKEN="$token" gh api "repos/$repo/branches/$(field .baseRefName)/protection" --jq '.required_linear_history.enabled' 2>/dev/null || true)
  [ "$linear" = true ] && method=squash || method=merge
fi
GH_TOKEN="$token" gh pr merge "$pr" -R "$repo" "--$method" || { echo "merge failed" >&2; exit 1; }
echo "merged #$pr in $repo"
# The merge cannot be undone, so a failure here is not a refusal: say what to run, and exit 4.
GH_TOKEN="$token" GH_REPO="$repo" python3 "$HERE/close_linked_issues.py" "$pr" --yes || { echo "merged #$pr, but closing its issues failed: run  GH_REPO=$repo python3 scripts/close_linked_issues.py $pr --yes" >&2; exit 4; }
