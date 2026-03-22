#!/bin/bash
# pa Oracle — Multi-Agent Startup Script
# Starts: tmux sessions, feed-watcher, maw serve
# Usage: wsl.exe -d Ubuntu -e bash /mnt/c/Users/pO-Ch/Documents/GitHub/pa-Oracle\ v2/start-agents.sh

set -e
export PATH="$HOME/.bun/bin:$PATH"

AGENTS_DIR="$HOME/agents"
MAW_DIR="/tmp/maw-js-server"
FEED_WATCHER="$HOME/.oracle/feed-watcher.py"
PORT=4000

echo "𓂀 pa Oracle — Starting Multi-Agent System"
echo "==========================================="

# 1. Kill old processes
echo ""
echo "[1/4] Cleaning up old processes..."
pkill -f "feed-watcher.py" 2>/dev/null || true
pkill -f "bun src/server.ts" 2>/dev/null || true
sleep 1

# 2. Create tmux sessions
echo "[2/4] Starting tmux sessions..."
tmux kill-server 2>/dev/null || true
sleep 1

for AGENT in pa-oracle pari probe pixel patch; do
  tmux new-session -d -s "$AGENT" -n "$AGENT" -c "$AGENTS_DIR/$AGENT"
  echo "  ✓ $AGENT"
done
echo "  $(tmux list-sessions | wc -l) sessions active"

# 3. Start feed-watcher
echo "[3/4] Starting feed-watcher..."
nohup python3 "$FEED_WATCHER" > /tmp/feed-watcher.log 2>&1 &
FEED_PID=$!
echo "  ✓ feed-watcher (PID: $FEED_PID)"

# 4. Start Knowledge Auto-Indexer
echo "[4/5] Starting Knowledge Auto-Indexer..."
ORACLE_ROOT="/mnt/c/Users/pO-Ch/Documents/GitHub/pa-Oracle v2"
cd "$ORACLE_ROOT"
nohup python3 knowledge_indexer.py > /tmp/knowledge-indexer.log 2>&1 &
KI_PID=$!
echo "  ✓ knowledge-indexer (PID: $KI_PID)"

# 5. Start maw serve
echo "[5/5] Starting maw serve on port $PORT..."
cd "$MAW_DIR"
nohup bun src/server.ts -- --port "$PORT" > /tmp/maw-serve.log 2>&1 &
MAW_PID=$!
sleep 2

if grep -q "maw serve" /tmp/maw-serve.log 2>/dev/null; then
  echo "  ✓ maw serve (PID: $MAW_PID)"
else
  echo "  ✗ maw serve failed — check /tmp/maw-serve.log"
fi

# 5. Start Claude in each agent
echo ""
echo "Starting Claude in agents..."
for AGENT in pa-oracle pari probe pixel patch; do
  if [ "$AGENT" = "pa-oracle" ]; then
    tmux send-keys -t "$AGENT:1" "claude --dangerously-skip-permissions" Enter
  else
    tmux send-keys -t "$AGENT:1" "claude --dangerously-skip-permissions --model claude-sonnet-4-6" Enter
  fi
  echo "  ✓ $AGENT — claude started"
  sleep 1
done

echo ""
echo "==========================================="
echo "𓂀 All systems online!"
echo ""
echo "  Dashboard: http://localhost:$PORT/#dashboard"
echo "  Chat:      http://localhost:$PORT/#chat"
echo "  PIN:       8959"
echo ""
echo "  Agents: pa-oracle (Opus), pari, probe, pixel, patch (Sonnet)"
echo "  Logs:   /tmp/maw-serve.log, /tmp/feed-watcher.log"
echo ""
echo "  To stop: pkill -f 'bun src/server.ts'; pkill -f feed-watcher; tmux kill-server"
echo "==========================================="
