#!/usr/bin/env bash
# The only way an agent merges a pull request (story #67, docs/MODES.md).
# It refuses, with exit 1 and `refused: <rule>`, unless all of this holds:
#   the mode is auto; the PR is open, not a draft, and has no conflicts; satvik-jain-iitd approved the latest commit;
#   no review thread is unresolved; every check is SUCCESS (SKIPPED and NEUTRAL count as passed, as on GitHub); the body has `Closes #n`.
# Then it merges with a merge commit, using the review account's own token (never switch the active gh account). Needs git, gh and jq.
# usage: review_merge.sh <pr-number> [owner/repo]
set -u
REVIEWER=satvik-jain-iitd
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
pr="${1:-}"
[[ "$pr" =~ ^[0-9]+$ ]] || { echo "usage: review_merge.sh <pr-number> [owner/repo]" >&2; exit 2; }
refuse() { echo "refused: $1" >&2; exit 1; }

mode=$("$HERE/mode.sh" get 2>/dev/null) || refuse "mode is not set (ask the owner)"
[ "$mode" = auto ] || refuse "mode is $mode (only auto merges)"

repo="${2:-$(gh repo view --json nameWithOwner --jq .nameWithOwner)}"
json=$(gh pr view "$pr" -R "$repo" --json state,isDraft,mergeable,headRefOid,body,reviews,statusCheckRollup) || refuse "cannot read pull request $pr"
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
bad=$(jq -r '.statusCheckRollup[] | select(((.conclusion // .state // "") | ascii_upcase) as $c | $c != "SUCCESS" and $c != "SKIPPED" and $c != "NEUTRAL") | (.name // .context)' <<<"$json" | head -1)
[ -z "$bad" ] || refuse "check $bad is not SUCCESS"

field .body | grep -Eiq '(^|[^[:alnum:]])closes #[0-9]+' || refuse 'no `Closes #n` in the body'

token=$(gh auth token --user "$REVIEWER") || refuse "no token for $REVIEWER on this machine"
GH_TOKEN="$token" gh pr merge "$pr" -R "$repo" --merge || { echo "merge failed" >&2; exit 1; }
echo "merged #$pr in $repo"
