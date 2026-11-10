#!/usr/bin/env bash
# Story #324 (A6): tag a release only when its notes, its gate and its tag all agree.
#   scripts/release.sh vX.Y.Z [--dry-run]
# Reference (MIT, read only): ECC verify-release-gates.js, which reads check runs for the exact sha and
# refuses a tag that already exists. Written here in bash with gh and git, stdlib of this repo only.
set -euo pipefail

refuse() { echo "refused: $1" >&2; exit 1; }

dry=0
tag=""
for arg in "$@"; do
  case "$arg" in
    --dry-run) dry=1 ;;
    v*) tag="$arg" ;;
    *) refuse "unknown argument '$arg' (use: scripts/release.sh vX.Y.Z [--dry-run])" ;;
  esac
done
[[ "$tag" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] || refuse "give a version like vX.Y.Z (got '${tag:-nothing}')"

cd "$(git rev-parse --show-toplevel)"

# shortcut: the notes are read from the working tree, not from HEAD. Add `git show HEAD:<notes>` when a release is cut from a dirty tree.
notes="docs/RELEASE_NOTES_$tag.md"
[ -f "$notes" ] || refuse "$notes does not exist"
version=$(head -1 "$notes" | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' | head -1 || true)
[ "$version" = "$tag" ] || refuse "the version line in $notes says '${version:-nothing}', not $tag"

git rev-parse -q --verify "refs/tags/$tag" >/dev/null && refuse "tag $tag already exists locally"
remote_tag=$(git ls-remote --tags origin "refs/tags/$tag") || refuse "cannot reach origin to check tag $tag"
[ -z "$remote_tag" ] || refuse "tag $tag already exists on origin"

repo=${RELEASE_REPO:-}
if [ -z "$repo" ]; then
  url=$(git remote get-url origin) || refuse "no origin remote"
  repo=$(printf '%s\n' "$url" | sed -E 's#^(https?://([^@/]+@)?github\.com/|git@github\.com:)##; s#\.git$##')
fi
[[ "$repo" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || refuse "cannot read owner/repo from origin ('$repo')"

sha=$(git rev-parse HEAD)
runs=$(gh api "repos/$repo/commits/$sha/check-runs" --paginate) || refuse "cannot read the check runs of $sha on $repo"
# The newest run named gate (or the ShipQuick child name) decides. "missing" when none ran on this sha.
gate=$(printf '%s' "$runs" | jq -rs '[.[].check_runs[]? | select(.name == "gate" or .name == "shipquick-checks / gate")]
  | sort_by(.id) | last | if . == null then "missing" else (.conclusion // .status) end')
[ "$gate" != missing ] || refuse "no check named gate ran on $sha"
[ "$gate" = success ] || refuse "the gate on $sha is $gate, not success"

if [ "$dry" -eq 1 ]; then
  echo "dry run: would tag $tag at $sha (gate success, notes say $tag, tag is new) and push the tag to origin"
  exit 0
fi

git tag -a "$tag" -m "ShipQuick $tag" "$sha"
git push -q origin "refs/tags/$tag"
echo "tagged and pushed $tag at $sha"
