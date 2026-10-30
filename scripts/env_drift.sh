#!/usr/bin/env bash
# Drift check: after a dev -> main promotion, main and dev should point at the same app code (story #120).
# Prints what is only on dev, and the files that differ. Informational — always exits 0 on a clean read.
# usage: env_drift.sh [--dev <branch>] [--main <branch>] [--repo <path>]
set -u
usage() { echo "usage: env_drift.sh [--dev <branch>] [--main <branch>] [--repo <path>]" >&2; exit 2; }
dev=dev; main=main; repo=.
while [ $# -gt 0 ]; do
  case "$1" in
    --dev) [ -n "${2:-}" ] || usage; dev="$2"; shift 2 ;;
    --main) [ -n "${2:-}" ] || usage; main="$2"; shift 2 ;;
    --repo) [ -n "${2:-}" ] || usage; repo="$2"; shift 2 ;;
    *) usage ;;
  esac
done
git -C "$repo" rev-parse --verify -q "$dev" >/dev/null 2>&1 || { echo "env_drift.sh: no such branch: $dev" >&2; exit 2; }
git -C "$repo" rev-parse --verify -q "$main" >/dev/null 2>&1 || { echo "env_drift.sh: no such branch: $main" >&2; exit 2; }

commits="$(git -C "$repo" log "$main..$dev" --oneline)"
if [ -z "$commits" ]; then
  echo "no drift: $main and $dev point to the same code"
  exit 0
fi
echo "only on $dev (not yet promoted to $main):"
echo "$commits"
echo
echo "files changed:"
git -C "$repo" diff --name-status "$main...$dev"
