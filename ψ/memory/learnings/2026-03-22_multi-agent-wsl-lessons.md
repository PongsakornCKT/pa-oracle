# Multi-Agent Infrastructure on WSL2 — Lessons

**Date**: 2026-03-22
**Source**: rrr: pa-Oracle-v2
**Tags**: multi-agent, wsl2, maw-js, feed-system, bun, tmux

## Key Lessons

### 1. Bun caches statSync aggressively on WSL2
`statSync`, `fstatSync`, and `Bun.file().size` all return stale data when another process writes to the file. Fix: open file with `openSync` then `fstatSync` on the fd each poll cycle. Better: use `fs.watch` or inotify.

### 2. Keep all agents on same OS
Windows↔WSL2 cross-OS development creates friction at every layer: path encoding, filesystem performance (/mnt/c is slow), tmux availability, encoding (cp1252 vs utf-8). Moving everything to Ubuntu eliminated most issues.

### 3. Feed system architecture
Real-time agent status requires 3 components:
- **feed-watcher.py** — tails Claude JSONL sessions, writes `~/.oracle/feed.log` + `maw-log.jsonl`
- **FeedTailer** (Bun) — polls feed.log, broadcasts events via WebSocket
- **Frontend** — receives WebSocket events, updates agent status (idle→busy→ready→idle)

### 4. maw-js dashboard status flow
`recent` message (tmux pane polling) → must update both `recentMap` (FleetGrid) AND `captureData` (DashboardView). Original code only updated recentMap, leaving DashboardView always showing idle.

## Takeaway
Multi-agent orchestration is 80% plumbing (status, communication, shared state) and 20% agent logic.
