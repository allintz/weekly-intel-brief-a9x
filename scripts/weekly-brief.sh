#!/bin/bash
# Weekly Intelligence Brief — runs via launchd Sunday 7pm ET
# Reads prompt from ../prompts/weekly-brief.md, runs claude non-interactively,
# logs full transcript to ~/logs/weekly-brief/.

set -e
set -o pipefail

REPO_DIR="/Users/alexlintz/code/prediction-tracker"
PROMPT_FILE="$REPO_DIR/prompts/weekly-brief.md"
LOG_DIR="/Users/alexlintz/logs/weekly-brief"
CLAUDE_BIN="/Users/alexlintz/.local/bin/claude"

mkdir -p "$LOG_DIR"
TS=$(date +%Y-%m-%d_%H%M%S)
LOG="$LOG_DIR/run-$TS.log"

echo "=== Weekly brief run started $(date) ===" | tee "$LOG"
echo "Prompt: $PROMPT_FILE ($(wc -c < "$PROMPT_FILE") bytes)" | tee -a "$LOG"

# Load secrets into environment (GH_PAT, METACULUS_TOKEN) — sourced from
# ~/.config/weekly-brief/secrets.env (mode 600, not in repo). The claude
# session inherits these as env vars; bash code in the prompt references
# them as "$GH_PAT" etc. rather than literal tokens.
SECRETS="/Users/alexlintz/.config/weekly-brief/secrets.env"
if [ -f "$SECRETS" ]; then
  set -a
  . "$SECRETS"
  set +a
else
  echo "WARNING: $SECRETS missing — PAT-dependent operations will fail" | tee -a "$LOG"
fi
cd "$REPO_DIR"

"$CLAUDE_BIN" \
  --print \
  --dangerously-skip-permissions \
  --model claude-sonnet-4-6 \
  --permission-mode bypassPermissions \
  "$(cat "$PROMPT_FILE")" \
  >> "$LOG" 2>&1

EXIT=$?
echo "=== Exit $EXIT at $(date) ===" >> "$LOG"
exit $EXIT
