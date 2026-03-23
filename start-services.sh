#!/bin/bash
# start-services.sh — Ensure maw-serve and feed-watcher are running
# Safe to call repeatedly (idempotent). Use as watchdog: while true; do bash start-services.sh; sleep 30; done
export PATH="$HOME/.bun/bin:$PATH"

MAW_DIR="/tmp/maw-js-server"
FEED_WATCHER="$HOME/.oracle/feed-watcher.py"

# --- feed-watcher ---
if ! pgrep -f "feed-watcher.py" > /dev/null 2>&1; then
  echo "$(date '+%H:%M:%S') [restart] feed-watcher"
  if tmux has-session -t feed-watcher 2>/dev/null; then
    tmux send-keys -t feed-watcher "python3 $FEED_WATCHER" Enter
  else
    tmux new-session -d -s feed-watcher "python3 $FEED_WATCHER"
  fi
fi

# --- maw-serve ---
if ! pgrep -f "bun src/server.ts" > /dev/null 2>&1; then
  echo "$(date '+%H:%M:%S') [restart] maw-serve"
  if tmux has-session -t maw-serve 2>/dev/null; then
    tmux send-keys -t maw-serve "cd $MAW_DIR && bun src/server.ts" Enter
  else
    tmux new-session -d -s maw-serve "cd $MAW_DIR && bun src/server.ts"
  fi
fi
