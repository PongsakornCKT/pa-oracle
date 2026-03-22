# Handoff: Marathon Infrastructure — Multi-Agent + Knowledge Map

**Date**: 2026-03-22 15:16 GMT+7
**Duration**: ~14 hours across 2 days (21 Mar 00:30 → 22 Mar 15:16)

## Context
**Oracle**: pa Oracle (she) | **Human**: พี่พง (PongsakornCKT)
**Mode**: Full Soul Sync | **Memory**: auto
**Team**: P-Team (pari, probe, pixel, patch) + pa-oracle

## What We Did

### Day 1 (21 Mar — marathon 8h)
- ChromaDB v1.5.5 installed + 4 collections
- maw-js cloned, built, deployed on Ubuntu WSL2 (port 4000)
- P-Team created: pari (researcher), probe (deep diver), pixel (data viz), patch (builder)
- All agents: CLAUDE.md, brain structure, shared threads, auto-bypass
- Feed-watcher.py: JSONL → feed.log → dashboard real-time status
- Fixed: Bun statSync cache, dashboard tokens panel, command center, chat "nat"→"พี่พง"
- Moved pa-oracle from Windows → Ubuntu
- Committed + pushed to GitHub (68cc1e4)

### Day 2 (22 Mar — 6h)
- Standup + 3 next actions from standup
- start-agents.sh — one-command startup script
- chroma_agent.py — shared vector memory (remember/recall/search)
- P-Team tested with real research task (WSL2 auto-start) — all agents responded
- Inbox fix — Stop/Notification detection in feed-watcher
- Gemini embedding migration (then reverted)
- Final: Ollama nomic-embed-text (local, 768d, stable)
- Knowledge Map 3D visualization (Three.js) in office #knowledge-map
- 4,872+ docs ingested from 8 repos
- knowledge_indexer.py — auto-index with watch mode
- Re-index button in Knowledge Map sidebar

## Pending
- [ ] Knowledge Map "Re-index" button — path issues with WSL/Windows python
- [ ] Vault sync with oracle-vault-report (plan ready, not implemented)
- [ ] ChromaDB HNSW >1000 docs corruption — using sub-collections workaround
- [ ] Agents probe/pixel/patch still on Opus (need manual tmux accept for Sonnet)
- [ ] Knowledge API (port 4001) keeps dying — consider embedding in maw serve
- [ ] Deploy workflow needs automation (build → copy → restart = 4 manual steps)

## Next Session
- [ ] Implement vault sync: office ↔ oracle-vault-report (generate.mjs → data.json)
- [ ] Fix Knowledge Map Re-index (WSL python path + chromadb install)
- [ ] Consider LanceDB instead of ChromaDB (no HNSW corruption)
- [ ] Create deploy script (one command: build + copy + restart maw serve)
- [ ] Test P-Team with real project work

## Key Files

### New Files Created
- `start-agents.sh` — startup script
- `chroma_agent.py` — ChromaDB agent interface
- `chroma_setup.py` — ChromaDB setup
- `ollama_embedding.py` — Ollama embedding function
- `ingest_all.py` — mass ingest 8 repos
- `knowledge_api.py` — Knowledge Map API
- `knowledge_indexer.py` — auto-indexer
- `feed-hook.sh` — Claude Code Stop/Notification hook
- `maw-js/feed-watcher.py` — JSONL → feed.log bridge
- `maw-js/office/src/components/KnowledgeMap.tsx` — 3D visualization

### Modified in maw-js
- `office/src/App.tsx` — added #knowledge-map route
- `office/src/components/StatusBar.tsx` — added Knowledge nav link
- `office/src/components/DashboardView.tsx` — token panel fix, quick controls
- `office/src/hooks/useSessions.ts` — recent→busy status, feed detection
- `office/src/components/chat/types.ts` — nat→พี่พง
- `src/server.ts` — knowledge-data.json route, /api/exec endpoint
- `src/engine.ts` — busyPollInterval
- `src/feed-tail.ts` — fstatSync fix
- `src/maw-log.ts` — nat→po-ch

### Infrastructure (Ubuntu WSL2)
- `~/.oracle/feed-watcher.py` — feed bridge
- `~/.oracle/feed-hook.sh` — Claude Code hook
- `~/.oracle/feed.log` — real-time agent activity
- `~/.claude/settings.json` — global permissions + hooks
- `~/agents/{pa-oracle,pari,probe,pixel,patch}/` — agent workspaces
- `/tmp/maw-js-server/` — maw serve deployment
