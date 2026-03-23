#!/bin/bash
# deploy.sh — Build office + deploy to WSL + restart maw-serve
# Usage: bash deploy.sh
set -e

MAW_SRC="/c/Users/pO-Ch/Documents/GitHub/maw-js"
MAW_DEST="/tmp/maw-js-server"
BUN="$HOME/.bun/bin/bun"

echo "=== Deploy maw-js ==="

# 1. Build office
echo "[1/4] Building office..."
cd "$MAW_SRC"
$BUN run build:office

# 2. Copy dist + src to WSL
echo "[2/4] Syncing files..."
wsl -e bash -c "
  cp -r /mnt/c/Users/pO-Ch/Documents/GitHub/maw-js/dist-office/* $MAW_DEST/dist-office/
  cp /mnt/c/Users/pO-Ch/Documents/GitHub/maw-js/src/*.ts $MAW_DEST/src/
  echo 'files synced'
"

# 3. Copy feed-watcher if exists
if [ -f "/c/Users/pO-Ch/Documents/GitHub/pa-Oracle v2/feed-watcher.py" ]; then
  wsl -e bash -c "cp '/mnt/c/Users/pO-Ch/Documents/GitHub/pa-Oracle v2/feed-watcher.py' ~/.oracle/feed-watcher.py"
  echo "  feed-watcher.py synced"
fi

# 4. Restart maw-serve
echo "[3/4] Restarting maw-serve..."
wsl -e bash -c "
  export PATH=\$HOME/.bun/bin:\$PATH
  if tmux has-session -t maw-serve 2>/dev/null; then
    tmux send-keys -t maw-serve C-c
    sleep 2
    tmux send-keys -t maw-serve 'cd $MAW_DEST && bun src/server.ts' Enter
  else
    tmux new-session -d -s maw-serve \"cd $MAW_DEST && \$HOME/.bun/bin/bun src/server.ts\"
  fi
  echo 'maw-serve restarted'
"

# 5. Verify
echo "[4/4] Verifying..."
sleep 3
STATUS=$(wsl -- curl -s -o /dev/null -w "%{http_code}" http://localhost:4000/ 2>/dev/null || echo "fail")
if [ "$STATUS" = "200" ]; then
  echo "=== Done! http://localhost:4000/#dashboard ==="
else
  echo "=== WARNING: Server returned $STATUS ==="
fi
