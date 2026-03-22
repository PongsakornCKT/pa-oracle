---
title: When a WebSocket message updates a side store (Zustand recentMap) but the UI rea
tags: [websocket, state-management, zustand, react, split-state, maw-js]
created: 2026-03-22
source: rrr: pa-Oracle-v2
project: github.com/pongsakornckt/pa-oracle-v2
---

# When a WebSocket message updates a side store (Zustand recentMap) but the UI rea

When a WebSocket message updates a side store (Zustand recentMap) but the UI reads from a different React state (captureData), the display won't reflect the update. Both state paths must write to the same state that drives rendering. In maw-js, the `recent` message from tmux busy polling updated recentMap but not captureData — so agent status cards never showed "busy" from tmux detection. Fix: also call setCaptureData in the `recent` handler. General rule: split state = split truth = bugs.

---
*Added via Oracle Learn*
