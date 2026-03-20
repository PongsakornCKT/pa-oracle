---
title: ChromaDB v1.5.5 API change: list_collections() returns Collection objects direct
tags: [chromadb, python, api-change, vector-db, windows-encoding]
created: 2026-03-20
source: rrr: pa-Oracle-v2
project: github.com/pongsakornckt/pa-oracle-v2
---

# ChromaDB v1.5.5 API change: list_collections() returns Collection objects direct

ChromaDB v1.5.5 API change: list_collections() returns Collection objects directly, not strings. Iterate with `for col in collections: col.name, col.count()` instead of passing to get_collection(). Windows Python scripts with unicode (hieroglyphics 𓂀) need PYTHONIOENCODING=utf-8 to avoid cp1252 encoding errors.

---
*Added via Oracle Learn*
