# Local Embedding (Ollama) vs API Embedding (Gemini)

**Date**: 2026-03-22
**Tags**: ollama, gemini, embedding, infrastructure, local-first

## Lesson

Local embedding (Ollama nomic-embed-text) beats API embedding (Gemini) for infrastructure:
- **Speed**: 4,872 docs in ~3 min (Ollama) vs ~30 min (Gemini)
- **Stability**: Never crashes vs API timeout/crash during large fetches
- **Offline**: Works without internet
- **Cost**: Free unlimited vs free rate-limited

bge-m3 (1.2GB) OOM on RTX 2060 (6GB VRAM). nomic-embed-text (274MB) is the sweet spot.

Also: `taskkill //IM python.exe` kills ALL python processes — use PID-specific kill instead.
