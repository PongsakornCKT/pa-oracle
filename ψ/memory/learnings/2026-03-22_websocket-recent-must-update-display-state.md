# WebSocket `recent` Must Update Display State

**Date**: 2026-03-22
**Context**: Dashboard status not updating

## Pattern

When a WebSocket message updates a side store (Zustand `recentMap`) but the UI reads from a different state (`captureData` React state), the display won't reflect the update. Both state paths must write to the same state that drives rendering.

## Evidence

- `recent` message → `markBusy()` → updates `recentMap` in Zustand ✓
- `feed` message → `updateStatusFromFeed()` → updates `captureData` in React state ✓
- Agent cards read `captureData[key]?.status` for display
- `recentMap` was never connected to `captureData` → tmux busy detection never showed in UI

## Fix

Added `setCaptureData` call inside the `recent` message handler to sync both states.

## General Principle

If two state systems track the same concept (agent activity), they must converge to the same display state. Split state = split truth = bugs.
