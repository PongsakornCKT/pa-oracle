# Uncommitted Files Lost in Marathon Sessions

**Date**: 2026-03-22
**Context**: Vault sync + dashboard restoration session

## Pattern

Marathon sessions (8-14h) that create many files but only commit once at the end risk losing work. Files created mid-session but not included in the final commit are silently lost.

## Evidence

- `KnowledgeMap.tsx` — created during Day 2 marathon, listed in handoff as key file, never committed. Completely lost. Had to recreate from scratch.
- `DashboardView.tsx` — created during marathon, never committed to git. Only survived because WSL `/tmp/maw-js-server/` had a source copy from manual deployment.

## Lesson

1. Commit incrementally during long sessions, not just at the end
2. Deploy scripts should also create checkpoint commits
3. `/tmp` is volatile — one reboot and DashboardView would have been gone too
4. The handoff listed files as "created" but didn't verify they were committed

## Connection to Principles

**Nothing is Deleted** applies only to what's committed. Uncommitted work IS deleted by definition. The principle demands frequent commits, not just philosophical agreement.
