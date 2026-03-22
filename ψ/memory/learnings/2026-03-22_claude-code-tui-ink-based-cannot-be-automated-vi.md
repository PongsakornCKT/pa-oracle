---
title: Claude Code TUI (Ink-based) cannot be automated via tmux send-keys — bypass perm
tags: [claude-code, tmux, automation, tui, wsl2, feed-watcher]
created: 2026-03-22
source: rrr: pa-Oracle-v2
project: github.com/pongsakornckt/pa-oracle-v2
---

# Claude Code TUI (Ink-based) cannot be automated via tmux send-keys — bypass perm

Claude Code TUI (Ink-based) cannot be automated via tmux send-keys — bypass permissions prompt ignores Down/Tab/number keys/ANSI escapes. Workarounds: (1) -p flag to pre-trust folders, (2) skipDangerousModePermissionPrompt in settings.json, (3) manual tmux attach. Also: WSL2 /mnt/c file copy may be stale — always verify content after cp. Feed-watcher Stop detection needs stop_reason == end_turn + question markers (?, ไหม, ครับ).

---
*Added via Oracle Learn*
