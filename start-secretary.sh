#!/bin/bash
# Start Secretary Room — pa-oracle + nasri-oracle
# Run this script, then attach with: tmux attach -t secretary

export SHELL=/usr/bin/bash

echo "=== Secretary Room — Starting ==="

# Kill old session if exists
tmux kill-session -t secretary 2>/dev/null

# Create session with both agents in one chain
# set exit-empty off keeps server alive
tmux set-option -g exit-empty off 2>/dev/null

tmux new-session -d -s secretary -n pa-oracle \; \
  set-option -t secretary remain-on-exit off \; \
  new-window -t secretary -n nasri-oracle \; \
  send-keys -t secretary:pa-oracle "cd '/c/Users/pO-Ch/Documents/GitHub/pa-Oracle v2' && (claude --continue || claude)" Enter \; \
  send-keys -t secretary:nasri-oracle "cd '/c/Users/pO-Ch/Documents/GitHub/nasri-oracle' && (gemini --yolo --prompt-interactive '/awaken')" Enter \; \
  select-window -t secretary:pa-oracle

echo ""
echo "  Secretary Room is up!"
echo "  pa-oracle    → Claude --continue"
echo "  nasri-oracle → Gemini --yolo (/awaken)"
echo ""
echo "  Attaching now... (Ctrl+B then D to detach)"
echo ""

# Attach to keep the server alive
tmux attach -t secretary
