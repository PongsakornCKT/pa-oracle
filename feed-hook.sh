#!/bin/bash
# Claude Code Hook — writes Stop/Notification events to feed.log
# Called by Claude Code when agent stops or sends notification
#
# Environment variables provided by Claude Code:
#   CLAUDE_EVENT_TYPE — "Stop", "Notification", etc.
#   CLAUDE_SESSION_ID — session UUID
#   CLAUDE_PROJECT — project directory name
#   CLAUDE_MESSAGE — the message/question text

# Silence all output — prevents hook output from being fed back to Claude as prompt
exec >/dev/null 2>&1

# Re-entrancy guard — prevents hook loops
[ -f "/tmp/feed-hook.active" ] && exit 0
touch "/tmp/feed-hook.active"
trap 'rm -f /tmp/feed-hook.active' EXIT

FEED_LOG="$HOME/.oracle/feed.log"
MAW_LOG="$HOME/.oracle/maw-log.jsonl"
HOSTNAME=$(hostname)
TS=$(date "+%Y-%m-%d %H:%M:%S")
TS_UTC=$(date -u "+%Y-%m-%dT%H:%M:%S.000Z")

# Resolve oracle name from project dir
ORACLE=$(basename "$CLAUDE_PROJECT" 2>/dev/null | sed 's/^-home-po-ch-agents-//')
[ -z "$ORACLE" ] && ORACLE=$(basename "$(pwd)" 2>/dev/null)
[ -z "$ORACLE" ] && ORACLE="unknown"

EVENT="${CLAUDE_EVENT_TYPE:-Stop}"
SESSION="${CLAUDE_SESSION_ID:0:8}"
MESSAGE=$(echo "$CLAUDE_MESSAGE" | head -1 | cut -c1-200)

# Write to feed.log
echo "$TS | $ORACLE | $HOSTNAME | $EVENT | $ORACLE | $SESSION » $MESSAGE" >> "$FEED_LOG"

# Write to maw-log for chat view (only for Stop with question)
if [ "$EVENT" = "Notification" ] || [ "$EVENT" = "Stop" ]; then
  MSG_ESCAPED=$(echo "$MESSAGE" | sed 's/"/\\"/g' | tr '\n' ' ' | cut -c1-200)
  echo "{\"ts\":\"$TS_UTC\",\"from\":\"$ORACLE\",\"to\":\"po-ch\",\"msg\":\"⚠️ $MSG_ESCAPED\",\"ch\":\"ask\"}" >> "$MAW_LOG"
fi
