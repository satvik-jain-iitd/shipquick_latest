#!/usr/bin/env bash
# ui/tool/ios_lint.sh (story #218, rule 38): the two-tier iOS UI lint for a child.
#   bash ui/tool/ios_lint.sh [file.swift ...]      lint these files; with no file, the Swift files changed against LINT_BASE
# Tiers: CI=1 (or true, as GitHub sets it) runs `swiftlint --strict` and `swiftformat --lint`, so a finding fails.
# Anything else warns only: swiftlint reports and exits 0, swiftformat gets --lenient.
# Env: LINT_BASE (default origin/dev), SWIFTLINT_CONFIG, SWIFTLINT_BASELINE, SWIFTFORMAT_CONFIG (a child's root copy
# wins over the kit's file), SWIFTLINT_BIN, SWIFTFORMAT_BIN (default: the name on PATH). CI pins SwiftLint 0.65.1 and
# SwiftFormat 0.64.6 by SHA-256 (.github/workflows/ci.yml, job ui-ios-lint); nothing is installed on a dev Mac by this script.
set -euo pipefail
kit_ios="$(cd "$(dirname "$0")/../ios" && pwd)"   # the kit's own files, wherever the kit sits (in a child: its submodule)
cd "$(git rev-parse --show-toplevel)"

# A child's own copy wins (adopt.sh writes ui/platforms/lint/swiftlint.yml), then the kit's file. Empty: none exists.
first_existing() { for p in "$@"; do [ -f "$p" ] && { echo "$p"; return; }; done; echo ""; }
config=${SWIFTLINT_CONFIG:-$(first_existing .swiftlint.yml ui/platforms/lint/swiftlint.yml ui/ios/lint/swiftlint.yml "$kit_ios/lint/swiftlint.yml")}
baseline=${SWIFTLINT_BASELINE:-$(first_existing .swiftlint-baseline.json ui/platforms/lint/swiftlint-baseline.json ui/ios/lint/swiftlint-baseline.json "$kit_ios/lint/swiftlint-baseline.json")}
format=${SWIFTFORMAT_CONFIG:-$(first_existing .swiftformat ui/platforms/lint/.swiftformat ui/ios/.swiftformat "$kit_ios/.swiftformat")}
swiftlint=${SWIFTLINT_BIN:-swiftlint}
swiftformat=${SWIFTFORMAT_BIN:-swiftformat}
base=${LINT_BASE:-origin/dev}
strict=0; [ "${CI:-}" = 1 ] || [ "${CI:-}" = true ] && strict=1

files=()
if [ $# -gt 0 ]; then
  files=("$@")
else
  # Changed against the merge base (committed or not) plus new untracked files. Deleted files are left out.
  # The merge base is its own statement: inside the process substitution a failure would pass as "nothing changed".
  if ! mb=$(git merge-base "$base" HEAD 2>/dev/null); then
    echo "ios lint: no merge base with $base (check out with fetch-depth: 0, or set LINT_BASE)"
    [ $strict -eq 1 ] && exit 1 || exit 0
  fi
  while IFS= read -r f; do [ -n "$f" ] && [ -f "$f" ] && files+=("$f"); done < <(
    { git diff --name-only --diff-filter=ACMR "$mb" -- '*.swift'
      git ls-files --others --exclude-standard -- '*.swift'; } | sort -u)
fi
if [ ${#files[@]} -eq 0 ]; then echo "ios lint: no Swift file changed against $base"; exit 0; fi

if ! command -v "$swiftlint" >/dev/null 2>&1; then
  echo "ios lint: swiftlint is not installed (CI pins 0.65.1; brew install swiftlint for a local run)"
  [ $strict -eq 1 ] && exit 1 || exit 0
fi
rc=0
args=(lint --no-cache --config "$config")
[ -n "$baseline" ] && args+=(--baseline "$baseline")
[ $strict -eq 1 ] && args+=(--strict)
"$swiftlint" "${args[@]}" "${files[@]}" || rc=$?

if command -v "$swiftformat" >/dev/null 2>&1; then
  fargs=(--lint --config "$format")
  [ $strict -eq 1 ] || fargs+=(--lenient)
  "$swiftformat" "${fargs[@]}" "${files[@]}" || rc=$?
else
  echo "ios lint: swiftformat is not installed (CI pins 0.64.6; brew install swiftformat for a local run)"
  [ $strict -eq 1 ] && exit 1
fi
[ $strict -eq 1 ] && exit $rc
exit 0   # the local tier never fails: it only reports
