# ChromaDB HNSW + Gemini Embedding Lessons

**Date**: 2026-03-22
**Source**: rrr: pa-Oracle-v2
**Tags**: chromadb, hnsw, gemini, embedding, scaling

## Lessons

1. **ChromaDB 1.5.5 HNSW corruption** — collections >1,000 docs corrupt on Windows. Fix: split into sub-collections of 500 docs max
2. **Gemini SDK migration** — `google-generativeai` deprecated → use `google-genai`. Model: `gemini-embedding-001` (not `text-embedding-004`)
3. **Gemini vs MiniLM for Thai** — Gemini distance 0.22 vs MiniLM 1.53 for same query = 7x better relevance
4. **Gemini embedding specs** — 768 dim (adjustable), free 1,500 req/min, task_type: RETRIEVAL_DOCUMENT for storing, RETRIEVAL_QUERY for searching
