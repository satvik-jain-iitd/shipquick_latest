#!/usr/bin/env bash
# List every model call site in this repo (docs/MODEL_LOAD.md rule 8), or check them against the table.
# Usage: scripts/model_calls.sh              prints file:line: text for each call site, tests and vendored code left out
#        scripts/model_calls.sh --check docs/data/model-calls.md
#                                           exit 1 and the missing files when a call-site file is not named in the table
set -u
PATTERN='ollama|/api/generate|/api/chat|/api/embeddings|chat/completions|openrouter\.ai|api\.groq\.com|api\.openai\.com|api\.anthropic\.com|num_predict|max_tokens'
EXCLUDE='(^|/)(tests?|node_modules|\.venv|venv|knowledge|dist|build)/|(^|/)test_[^/]*\.(py|ts|js)$|\.test\.(ts|js)$|\.spec\.(ts|js)$'
sites() { grep -rnE --include='*.py' --include='*.ts' --include='*.js' --include='*.sh' "$PATTERN" . 2>/dev/null | sed 's|^\./||' | grep -vE "$EXCLUDE" | grep -v "scripts/model_calls.sh"; }
if [ "${1:-}" = "--check" ]; then
  table="${2:-docs/data/model-calls.md}"
  [ -f "$table" ] || { echo "no table at $table"; exit 1; }
  missing=0
  for f in $(sites | cut -d: -f1 | sort -u); do
    grep -qF "$f" "$table" || { echo "$f"; missing=1; }
  done
  [ "$missing" -eq 0 ] && echo "ok   every call-site file is in $table"
  exit $missing
fi
sites
