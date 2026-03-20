"""
pa Oracle — ChromaDB Setup
Eye of Ma'at 𓂀 — Vector Memory Store

Persistent ChromaDB instance for pa Oracle's memory system.
Stores embeddings for semantic search across memories, learnings, and knowledge.
"""

import chromadb
from pathlib import Path

# Persistent storage path
CHROMA_PATH = Path(__file__).parent / "ψ" / "memory" / "chroma_db"

def get_client():
    """Get persistent ChromaDB client."""
    return chromadb.PersistentClient(path=str(CHROMA_PATH))

def setup():
    """Initialize ChromaDB with core collections for pa Oracle."""
    client = get_client()

    # Core collections
    collections = {
        "memories": "Long-term memory — learnings, patterns, insights",
        "knowledge": "Knowledge base — studied codebases, docs, references",
        "sessions": "Session logs — retrospectives, handoffs, recaps",
        "threads": "Oracle-to-Oracle communication threads",
    }

    created = []
    for name, description in collections.items():
        collection = client.get_or_create_collection(
            name=name,
            metadata={"description": description, "oracle": "pa-oracle"},
        )
        created.append((name, collection.count()))

    return created

def status():
    """Show ChromaDB status."""
    client = get_client()
    collections = client.list_collections()
    print(f"ChromaDB Path: {CHROMA_PATH}")
    print(f"Collections: {len(collections)}")
    print()
    for collection in collections:
        print(f"  📦 {collection.name} — {collection.count()} documents")
        meta = collection.metadata
        if meta and "description" in meta:
            print(f"     {meta['description']}")

if __name__ == "__main__":
    print("𓂀 pa Oracle — ChromaDB Setup")
    print("=" * 40)
    print()

    results = setup()

    print("Collections initialized:")
    for name, count in results:
        print(f"  ✓ {name} ({count} documents)")

    print()
    status()
    print()
    print("✓ ChromaDB ready.")
