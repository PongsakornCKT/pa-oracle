---
title: feed-watcher.py defaults new JSONL file offsets to current file size, which skip
tags: [feed-watcher, multi-agent, status-tracking, offset-management, maw-js]
created: 2026-03-22
source: rrr: pa-Oracle-v2
project: github.com/pongsakornckt/pa-oracle-v2
---

# feed-watcher.py defaults new JSONL file offsets to current file size, which skip

feed-watcher.py defaults new JSONL file offsets to current file size, which skips all existing events. When agents start new Claude sessions mid-run, their events are lost until feed-watcher restarts. Fix: track known_files set — new files get offset=0 (process from start), existing files keep their tracked offset. Also: tmux pane command "claude" running does NOT mean agent is busy — idle Claude sessions also show "claude". Only feed events (PreToolUse, UserPromptSubmit) indicate actual work. Don't let busyPollInterval override feed-based status.

---
*Added via Oracle Learn*
