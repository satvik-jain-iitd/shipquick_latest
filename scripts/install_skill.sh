#!/usr/bin/env bash
# Links the kit's skills into ~/.claude/skills: shipquick-feedback (story #118) and qa-loop (story #162).
# Safe to run twice. A real file or folder already at a skill's place is never touched: that skill is
# skipped and named, the others still install, and the script exits 2 at the end.
# usage: scripts/install_skill.sh
set -eu
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SQ="$(cd "$HERE/.." && pwd -P)"
: "${HOME:?HOME is not set}"
DEST_DIR="$HOME/.claude/skills"
mkdir -p "$DEST_DIR"
rc=0
for name in shipquick-feedback qa-loop; do
  SRC="$SQ/skills/$name"
  DEST="$DEST_DIR/$name"
  [ -d "$SRC" ] || { echo "install_skill.sh: no such skill: $SRC" >&2; rc=2; continue; }
  if [ -L "$DEST" ]; then
    if [ "$(readlink "$DEST")" = "$SRC" ]; then
      echo "unchanged $DEST"
      continue
    fi
    rm "$DEST"
  elif [ -e "$DEST" ]; then
    echo "install_skill.sh: $DEST already exists and is not our symlink; move it aside, then run this again ($name skipped)" >&2
    rc=2
    continue
  fi
  ln -s "$SRC" "$DEST"
  echo "linked $DEST -> $SRC"
done
exit "$rc"
