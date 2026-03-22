---
title: Multi-agent infrastructure on WSL2: (1) Bun caches statSync/fstatSync aggressive
tags: [multi-agent, wsl2, maw-js, feed-system, bun, tmux, infrastructure]
created: 2026-03-22
source: rrr: pa-Oracle-v2
project: github.com/pongsakornckt/pa-oracle-v2
---

# Multi-agent infrastructure on WSL2: (1) Bun caches statSync/fstatSync aggressive

Multi-agent infrastructure on WSL2: (1) Bun caches statSync/fstatSync aggressively — use openSync+fstatSync per poll cycle to detect file changes. (2) Keep all agents on same OS — Windows↔WSL2 cross-OS creates friction at every layer. (3) Feed system needs 3 components: feed-watcher (JSONL→feed.log), FeedTailer (feed.log→WebSocket), frontend (WebSocket→UI). (4) maw-js dashboard 'recent' message must update both recentMap AND captureData for status to show correctly. (5) Multi-agent orchestration is 80% plumbing (status, communication, shared state) and 20% agent logic.

---
*Added via Oracle Learn*
