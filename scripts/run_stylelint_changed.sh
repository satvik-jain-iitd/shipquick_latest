#!/usr/bin/env bash
# Story #133, PR #374 review: stylelint on the CSS files a PR changed, run once per package root.
# A child may keep its web app in a subfolder (web/package.json, web/.stylelintrc.json, Android and iOS beside it),
# so each changed .css file walks up to the nearest folder with a package.json or a stylelint config; that folder's
# config, lockfile and node_modules/.bin/stylelint are used, pinned npx as the fallback. Called by the design-tokens
# job in ci.yml and checks.yml and by check_local.sh design-tokens, so the three stay the same.
# Usage: run_stylelint_changed.sh <base-ref> [repo]      e.g. run_stylelint_changed.sh origin/dev project
# Exit 0 with a `skip stylelint: ...` line when nothing applies; otherwise stylelint's own exit code (1 = a hit).
set -u
BASE="${1:?usage: run_stylelint_changed.sh <base-ref> [repo]}"
cd "${2:-.}" || exit 1
CSS=$(git diff --name-only --diff-filter=AMR "$BASE...HEAD" -- '*.css')
[ -z "$CSS" ] && { echo "skip stylelint: no css changed"; exit 0; }
command -v npx >/dev/null || { echo "skip stylelint: npx is not installed; CI still runs it"; exit 0; }

has_config() {   # a .stylelintrc*, a stylelint.config.*, or a "stylelint" key in package.json (an unmatched glob stays literal, so test each)
  local f; for f in "$1"/.stylelintrc* "$1"/stylelint.config.*; do [ -e "$f" ] && return 0; done
  grep -q '"stylelint"' "$1/package.json" 2>/dev/null
}
package_root() {   # nearest folder, from the file's own up to the repo root, holding a package.json or a stylelint config
  local d; d=$(dirname "$1")
  while [ "$d" != "." ]; do
    { [ -f "$d/package.json" ] || has_config "$d"; } && { echo "$d"; return; }
    d=$(dirname "$d")
  done
  echo .
}

# shortcut: paths are split on newlines, so a css path with a space in it breaks the pairing; rename the file.
PAIRS=$(printf '%s\n' "$CSS" | while IFS= read -r f; do printf '%s\t%s\n' "$(package_root "$f")" "$f"; done)
rc=0 ran=0
for root in $(printf '%s\n' "$PAIRS" | cut -f1 | sort -u); do
  has_config "$root" || { echo "skip stylelint: no stylelint config in $root"; continue; }
  ran=1
  files=$(printf '%s\n' "$PAIRS" | awk -F'\t' -v r="$root" '$1 == r { print $2 }' | sed "s|^$root/||")
  (
    cd "$root" || exit 1
    # PR #374 review: stylelint resolves `extends` and `plugins` from the project's node_modules, so install them,
    # but only when the binary is missing: `npm ci` wipes node_modules first, and this also runs on a dev's checkout.
    [ -x node_modules/.bin/stylelint ] || { [ -f package-lock.json ] && npm ci --ignore-scripts --no-audit --no-fund; }
    if [ -x node_modules/.bin/stylelint ]; then SL=node_modules/.bin/stylelint; else SL="npx --yes stylelint@16.26.1"; fi
    printf '%s\n' "$files" | xargs $SL --report-needless-disables
  ) || rc=1
done
[ "$ran" -eq 0 ] && echo "skip stylelint: no stylelint config in the project"
exit $rc
