#!/usr/bin/env bash
# Story #140: one role, one GitHub account, per session. SOURCE this, do not run it, so GH_TOKEN
# reaches your own shell:
#   source scripts/role.sh coder|reviewer [account]
# Reads .shipquick/roles.yml (scripts/roles.py) -- no account name lives in this script. With no
# [account] given, the first account listed for that role is used. A second call with a DIFFERENT
# role in the same shell refuses; the same role again is a no-op (fine to re-run). Needs `gh auth
# login` already done on this machine for the chosen account.
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  echo "role.sh must be sourced, not run: source scripts/role.sh coder|reviewer [account]" >&2
  exit 2
fi
_role_here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_role="${1:-}"
case "$_role" in
  coder|reviewer) ;;
  *) echo "usage: source role.sh coder|reviewer [account]" >&2; return 2 ;;
esac
if [ -n "${SHIPQUICK_ROLE:-}" ] && [ "${SHIPQUICK_ROLE}" != "$_role" ]; then
  echo "role.sh: this session is already '$SHIPQUICK_ROLE' (as $SHIPQUICK_ACCOUNT) -- one role per session, refusing to also become '$_role'" >&2
  return 1
fi
_root="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "role.sh: not inside a git repository" >&2; return 2; }
_accounts="$(python3 "$_role_here/roles.py" get "$_role" --file "$_root/.shipquick/roles.yml" 2>&1)" || { echo "role.sh: $_accounts" >&2; return 1; }
_account="${2:-}"
if [ -z "$_account" ]; then
  _account="${_accounts%%,*}"
elif ! printf ',%s,' "$_accounts" | grep -qF ",$_account,"; then
  echo "role.sh: $_account is not a $_role account in .shipquick/roles.yml (have: $_accounts)" >&2
  return 1
fi
_token="$(gh auth token --user "$_account" 2>&1)" || { echo "role.sh: no token for $_account on this machine ($_token)" >&2; return 1; }
export GH_TOKEN="$_token"
export SHIPQUICK_ROLE="$_role"
export SHIPQUICK_ACCOUNT="$_account"
echo "role: $_role ($_account)"
unset _role _accounts _account _token _role_here _root
