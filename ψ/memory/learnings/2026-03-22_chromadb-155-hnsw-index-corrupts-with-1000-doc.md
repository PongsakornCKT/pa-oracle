---
title: ChromaDB 1.5.5 HNSW index corrupts with >1,000 docs per collection on Windows — 
tags: [chromadb, hnsw, gemini, embedding, knowledge-map, three-js]
created: 2026-03-22
source: rrr: pa-Oracle-v2
project: github.com/pongsakornckt/pa-oracle-v2
---

# ChromaDB 1.5.5 HNSW index corrupts with >1,000 docs per collection on Windows — 

ChromaDB 1.5.5 HNSW index corrupts with >1,000 docs per collection on Windows — fix by splitting into sub-collections (500 docs/col). Gemini embedding SDK: use google-genai (not google-generativeai), model gemini-embedding-001. Thai search quality: Gemini distance 0.22 vs MiniLM 1.53 = 7x better. Knowledge Map architecture: ingest (Python) → API (HTTP :4001) → Frontend (Three.js particles).

---
*Added via Oracle Learn*
