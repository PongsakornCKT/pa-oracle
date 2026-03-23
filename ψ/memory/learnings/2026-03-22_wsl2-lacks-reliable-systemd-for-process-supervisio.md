---
title: WSL2 lacks reliable systemd for process supervision. Pragmatic fix: bash watchdo
tags: [watchdog, process-supervision, wsl2, deploy-automation, multi-agent, infrastructure]
created: 2026-03-22
source: rrr: pa-Oracle-v2
project: github.com/pongsakornckt/pa-oracle-v2
---

# WSL2 lacks reliable systemd for process supervision. Pragmatic fix: bash watchdo

WSL2 lacks reliable systemd for process supervision. Pragmatic fix: bash watchdog loop in tmux that checks every 30s if services (maw-serve, feed-watcher) are alive via pgrep, restarts if dead. Zero dependencies, idempotent (safe to call repeatedly), 5 lines of code. Trade-off: up to 30s downtime before detection. Also: deploy.sh compresses 4 manual steps (vite build, cp to WSL, restart server, verify) into one command. Combined with feed-watcher known_files fix (offset=0 for new JSONL files) and removing busyPollInterval (feed events = single source of truth for agent status), this creates a stable multi-agent infrastructure.

---
*Added via Oracle Learn*
