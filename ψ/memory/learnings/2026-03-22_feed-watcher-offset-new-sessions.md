# Feed-Watcher Loses New Agent Sessions

**Date**: 2026-03-22
**Context**: probe/pixel/patch events missing from feed.log and chat

## Pattern

When Claude Code agents start new sessions (new JSONL files), the feed-watcher.py discovers them but sets offset to current file size — missing all events already written. Only events AFTER discovery get processed.

## Root Cause

```python
offsets.get(key, size)  # Default to current size for new files
```

This is correct at startup (avoid replaying history) but wrong for mid-run discovery. A file with 62KB already written gets offset=62KB, so all 62KB of events are skipped.

## Symptoms

- Agent responds in tmux but no events in feed.log
- Agent not showing in Chat view (maw-log.jsonl)
- Status stays "idle" despite agent being active

## Fix (immediate)

Restart feed-watcher.py. All files get fresh offsets.

## Fix (proper)

Track `known_files` set. On each scan cycle, if a file is NOT in `known_files`, set offset=0 (process from start) instead of `size`. Add to `known_files` after first scan.
