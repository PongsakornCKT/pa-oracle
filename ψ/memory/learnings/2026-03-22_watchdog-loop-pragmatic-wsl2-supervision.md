# Watchdog Loop — Pragmatic WSL2 Process Supervision

**Date**: 2026-03-22
**Context**: maw-serve and feed-watcher dying silently between deploys

## Pattern

WSL2 lacks reliable systemd. Services started in tmux die when sessions crash or shells exit. The pragmatic fix: a bash watchdog loop that checks every 30s and restarts dead processes.

```bash
# start-services.sh — idempotent, safe to call repeatedly
if ! pgrep -f "bun src/server.ts" > /dev/null; then
  tmux new-session -d -s maw-serve "bun src/server.ts"
fi

# Watchdog: while true; do bash start-services.sh; sleep 30; done
```

## Why Not Alternatives

- **systemd**: WSL2 support inconsistent, requires `wsl.conf` changes, not all distros
- **pm2**: Extra dependency, Node-based, overkill for 2 services
- **supervisor/runit**: Need separate install, config files
- **tmux + bash loop**: Zero dependencies, works everywhere, 5 lines of code

## Trade-offs

- Pro: Dead simple, zero dependencies, idempotent
- Con: Up to 30s downtime before restart detected
- Con: No log rotation, no resource limits
- Acceptable for dev/personal multi-agent setup
