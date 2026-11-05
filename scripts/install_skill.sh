#!/usr/bin/env bash
# Links the shipquick-feedback skill into ~/.claude/skills (story #118). Safe to run twice.
# usage: scripts/install_skill.sh
set -eu
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SQ="$(cd "$HERE/.." && pwd -P)"
SRC="$SQ/skills/shipquick-feedback"
[ -d "$SRC" ] || { echo "install_skill.sh: no such skill: $SRC" >&2; exit 2; }
: "${HOME:?HOME is not set}"
DEST_DIR="$HOME/.claude/skills"
DEST="$DEST_DIR/shipquick-feedback"

mkdir -p "$DEST_DIR"
if [ -L "$DEST" ]; then
  if [ "$(readlink "$DEST")" = "$SRC" ]; then
    echo "unchanged $DEST"
    exit 0
  fi
  rm "$DEST"
elif [ -e "$DEST" ]; then
  echo "install_skill.sh: $DEST already exists and is not our symlink; remove it first" >&2
  exit 2
fi
ln -s "$SRC" "$DEST"
echo "linked $DEST -> $SRC"
