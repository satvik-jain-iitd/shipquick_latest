#!/usr/bin/env bash
# Design first (story #121): a PR that touches a project's own frontend paths must name the
# approved design board in its body, or fail. A PR that says "no screen change" but still touches
# those paths also fails. The paths file (one shell glob per line, # comments and blanks ignored)
# is the project's own config; nothing configured means nothing is checked.
# usage: check_frontend_design.sh --body-file <f> --base <ref> [--repo <path>] [--paths-file <path>] [--head <branch-name>]
set -u
usage() { echo "usage: check_frontend_design.sh --body-file <f> --base <ref> [--repo <path>] [--paths-file <path>] [--head <branch-name>]" >&2; exit 2; }
body_file=""; base=""; repo="."; paths_file="docs/frontend-paths.txt"; head=""
while [ $# -gt 0 ]; do
  case "$1" in
    --body-file) [ -n "${2:-}" ] || usage; body_file="$2"; shift 2 ;;
    --base) [ -n "${2:-}" ] || usage; base="$2"; shift 2 ;;
    --repo) [ -n "${2:-}" ] || usage; repo="$2"; shift 2 ;;
    --paths-file) [ -n "${2:-}" ] || usage; paths_file="$2"; shift 2 ;;
    --head) [ -n "${2:-}" ] || usage; head="$2"; shift 2 ;;
    *) usage ;;
  esac
done
[ -n "$body_file" ] && [ -n "$base" ] || usage
[ -f "$body_file" ] || { echo "check_frontend_design.sh: no such file: $body_file" >&2; exit 2; }

base_name="${base##*/}"   # strip a leading "origin/" if present
head_name="${head:-$(git -C "$repo" rev-parse --abbrev-ref HEAD 2>/dev/null || true)}"
if [ "$base_name" = main ] || [ "$head_name" = main ]; then
  echo "base or head is main (a dev -> main promotion or a main -> dev back-merge, not a frontend story): check skipped"
  exit 0
fi

globs_path="$repo/$paths_file"
globs=()
if [ -f "$globs_path" ]; then
  while IFS= read -r line; do
    line="${line%%#*}"
    line="$(printf '%s' "$line" | sed -E 's/^[[:space:]]+|[[:space:]]+$//g')"
    [ -n "$line" ] && globs+=("$line")
  done < "$globs_path"
fi
if [ "${#globs[@]}" -eq 0 ]; then
  echo "no frontend paths configured ($paths_file): check skipped"
  exit 0
fi

merge_base="$(git -C "$repo" merge-base "$base" HEAD)" || { echo "check_frontend_design.sh: no merge-base with $base" >&2; exit 2; }
touched=()
while IFS= read -r f; do
  [ -n "$f" ] || continue
  for g in "${globs[@]}"; do
    case "$f" in $g) touched+=("$f"); break ;; esac
  done
done < <(git -C "$repo" diff --name-only "$merge_base" HEAD)

if [ "${#touched[@]}" -eq 0 ]; then
  echo "no frontend path touched: check skipped"
  exit 0
fi

if grep -qi 'no screen change' "$body_file"; then
  echo "says \"no screen change\" but touches frontend paths:"
  printf '  %s\n' "${touched[@]}"
  exit 1
fi

board="$(grep -E '^Design board:' "$body_file" | head -1 | sed -E 's/^Design board:[[:space:]]*//; s/[[:space:]]+$//')"
case "$board" in
  "" | "<"*">"*)
    echo "touches frontend paths with no approved board named (\"Design board: <name>\" in the PR body):"
    printf '  %s\n' "${touched[@]}"
    exit 1
    ;;
esac
approved="$(grep -E '^Approved:' "$body_file" | head -1 | sed -E 's/^Approved:[[:space:]]*//; s/[[:space:]]+$//')"
case "$approved" in
  "" | "<"*">"*)
    echo "touches frontend paths with a board but no approved date (\"Approved: <date>\" in the PR body):"
    printf '  %s\n' "${touched[@]}"
    exit 1
    ;;
esac
echo "design board named: $board (approved $approved)"
