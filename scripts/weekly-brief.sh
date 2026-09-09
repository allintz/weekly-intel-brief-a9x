#!/bin/bash
# Weekly Intelligence Brief — runs via launchd Sunday 7pm ET
# Reads prompt from ../prompts/weekly-brief.md, runs claude non-interactively,
# logs full transcript to ~/logs/weekly-brief/.
#
# 2026-09-08 hardening (after five consecutive silent Sunday failures):
#   1. Auth preflight: a cheap `claude -p` call before the 57KB run. An expired
#      CLI OAuth session now fails in seconds and texts Alex, instead of three
#      silent retries. Sourcing secrets.env also lets a long-lived
#      CLAUDE_CODE_OAUTH_TOKEN (from `claude setup-token`) take over.
#   2. GitHub token fallback: the PAT in secrets.env expired in June; the `gh`
#      keyring token has push rights, so GH_PAT falls back to `gh auth token`.
#   3. caffeinate: the run is multi-hour and the laptop sleeps after 1 min on
#      battery. Sleep mid-run showed up as "Connection closed mid-response".
#      Lid-closed sleep still cannot be prevented from software.
#   4. Real status notifications: macOS banner + iMessage on any non-ok result,
#      and a machine-readable "=== weekly-brief status: X ===" log line. Exit 0
#      without a published edition (Aug 9) now counts as a failure.

set -e
set -o pipefail

REPO_DIR="/Users/alexlintz/code/prediction-tracker"
PROMPT_FILE="$REPO_DIR/prompts/weekly-brief.md"
LOG_DIR="/Users/alexlintz/logs/weekly-brief"
CLAUDE_BIN="/Users/alexlintz/.local/bin/claude"
IMESSAGE="/Users/alexlintz/.config/weekly-brief/send-imessage.sh"
MODEL="claude-sonnet-4-6"

mkdir -p "$LOG_DIR"
TS=$(date +%Y-%m-%d_%H%M%S)
LOG="$LOG_DIR/run-$TS.log"

echo "=== Weekly brief run started $(date) ===" | tee "$LOG"
echo "Prompt: $PROMPT_FILE ($(wc -c < "$PROMPT_FILE") bytes)" | tee -a "$LOG"

# ---------------------------------------------------------------- notify ----
# AppleScript string literals can't contain raw newlines or unescaped quotes.
sanitize() { printf '%s' "$1" | tr '\n\r' '  ' | tr -d '"\\' | cut -c1-900; }

notify() {
  local short long
  short=$(sanitize "$1"); long=$(sanitize "$2")
  osascript -e "display notification \"$short\" with title \"Weekly Brief\" sound name \"Glass\"" >> "$LOG" 2>&1 || true
  if [ -x "$IMESSAGE" ]; then
    "$IMESSAGE" "$long" >> "$LOG" 2>&1 || echo "(iMessage send failed)" >> "$LOG"
  fi
}

finish() {
  # $1 = status (auth|unpublished|fail|ok), $2 = exit code
  local status="$1" code="$2"
  echo "=== weekly-brief status: $status ===" >> "$LOG"
  echo "=== Final exit $code at $(date) ===" >> "$LOG"
  case "$status" in
    auth)
      notify "🔑 Weekly brief FAILED: CLI auth expired" \
        "🔑 Weekly brief FAILED: Claude CLI auth expired, nothing ran. Fix: run 'claude auth login' in a terminal (or 'claude setup-token' and add CLAUDE_CODE_OAUTH_TOKEN to ~/.config/weekly-brief/secrets.env). Log: $LOG" ;;
    unpublished)
      notify "⚠️ Weekly brief ran but did NOT publish" \
        "⚠️ Weekly brief: claude exited 0 but today's edition is not in editions.json. Check /tmp/new.html and the STEP 5 publish block. Log: $LOG" ;;
    fail)
      notify "⚠️ Weekly brief FAILED (exit $code)" \
        "⚠️ Weekly brief FAILED after $MAX_ATTEMPTS attempts (exit $code). Last lines: $(tail -n 3 "$LOG"). Log: $LOG" ;;
    ok)
      # The prompt's STEP 5.5d already texts Alex on success; banner only.
      osascript -e 'display notification "Weekly brief published" with title "Weekly Brief"' >/dev/null 2>&1 || true ;;
  esac
  exit "$code"
}

# --------------------------------------------------------------- secrets ----
# Load secrets into environment (GH_PAT, METACULUS_TOKEN, optionally
# CLAUDE_CODE_OAUTH_TOKEN) from ~/.config/weekly-brief/secrets.env (mode 600,
# not in repo). The claude session inherits these as env vars; bash code in
# the prompt references them as "$GH_PAT" etc. rather than literal tokens.
SECRETS="/Users/alexlintz/.config/weekly-brief/secrets.env"
if [ -f "$SECRETS" ]; then
  set -a
  . "$SECRETS"
  set +a
else
  echo "WARNING: $SECRETS missing — PAT-dependent operations will fail" | tee -a "$LOG"
fi
cd "$REPO_DIR"

# GH_PAT fallback: if the stored PAT is rejected, use the gh CLI keyring token
# (account allintz, scope repo). Same Bearer usage, so the prompt needs no change.
gh_code=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer ${GH_PAT:-none}" https://api.github.com/user || echo 000)
if [ "$gh_code" != "200" ]; then
  echo "GH_PAT from secrets.env rejected (HTTP $gh_code); falling back to gh auth token" >> "$LOG"
  if GH_FALLBACK=$(gh auth token 2>/dev/null) && [ -n "$GH_FALLBACK" ]; then
    export GH_PAT="$GH_FALLBACK"
    echo "GH_PAT now sourced from gh keyring" >> "$LOG"
  else
    echo "WARNING: no working GitHub token; publish step will fail" >> "$LOG"
  fi
fi

# -------------------------------------------------------- auth preflight ----
# Cheap call so an expired OAuth session fails in seconds, not after 3 tries.
# perl alarm because macOS has no coreutils `timeout`.
echo "=== Auth preflight at $(date) ===" >> "$LOG"
set +e
PREFLIGHT=$(perl -e 'alarm 120; exec @ARGV' "$CLAUDE_BIN" -p "reply with the single word OK" --model claude-haiku-4-5-20251001 2>&1)
PRE_EXIT=$?
set -e
echo "$PREFLIGHT" | tail -n 3 >> "$LOG"
if echo "$PREFLIGHT" | grep -qE "Failed to authenticate|OAuth (session|access token) (has )?expired|API Error: 401"; then
  MAX_ATTEMPTS=0
  finish auth 1
fi
if [ "$PRE_EXIT" -ne 0 ]; then
  echo "Preflight exit $PRE_EXIT (not an auth error); continuing to main run" >> "$LOG"
fi

# ------------------------------------------------------------- main run ----
# True if today's UTC edition is already live in editions.json on main.
# Guards retries so we never regenerate after a run that actually published
# before its CLI session dropped the socket.
edition_published() {
  local today
  today=$(date -u +%Y-%m-%d)
  curl -s "https://raw.githubusercontent.com/allintz/weekly-intel-brief-a9x/main/editions.json" \
    | grep -q "\"$today\""
}

# Retry the claude run on transient failures (e.g. "socket connection closed
# unexpectedly"), which otherwise leave the brief unpublished until a manual
# rerun. set -e is disabled around the call so a non-zero exit is handled here.
# caffeinate -i -s keeps the Mac from idle-sleeping for the life of the call.
MAX_ATTEMPTS=3
RETRY_DELAY=120
EXIT=1
for ATTEMPT in $(seq 1 "$MAX_ATTEMPTS"); do
  echo "=== Attempt $ATTEMPT/$MAX_ATTEMPTS at $(date) ===" >> "$LOG"
  set +e
  /usr/bin/caffeinate -i -s "$CLAUDE_BIN" \
    --print \
    --dangerously-skip-permissions \
    --model "$MODEL" \
    --permission-mode bypassPermissions \
    "$(cat "$PROMPT_FILE")" \
    >> "$LOG" 2>&1
  EXIT=$?
  set -e

  if grep -qE "Failed to authenticate|OAuth (session|access token) (has )?expired" "$LOG"; then
    finish auth 1
  fi

  if [ "$EXIT" -eq 0 ]; then
    echo "=== Attempt $ATTEMPT succeeded ===" >> "$LOG"
    break
  fi

  echo "=== Attempt $ATTEMPT failed (exit $EXIT) ===" >> "$LOG"

  # If the failed attempt nonetheless published today's edition, treat as done.
  if edition_published; then
    echo "=== Today's edition already published; treating as success ===" >> "$LOG"
    EXIT=0
    break
  fi

  if [ "$ATTEMPT" -lt "$MAX_ATTEMPTS" ]; then
    echo "=== Retrying in ${RETRY_DELAY}s ===" >> "$LOG"
    /usr/bin/caffeinate -i -s sleep "$RETRY_DELAY"
  fi
done

if [ "$EXIT" -ne 0 ]; then
  finish fail "$EXIT"
fi
if edition_published; then
  finish ok 0
else
  finish unpublished 1
fi
