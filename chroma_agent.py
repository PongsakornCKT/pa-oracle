"""
pa Oracle — ChromaDB Agent Interface
Shared memory layer for all P-Team agents.

Usage:
  python chroma_agent.py remember "lesson text" --tags tag1,tag2 --agent pari
  python chroma_agent.py recall "search query" --n 5
  python chroma_agent.py status
  python chroma_agent.py ingest-learnings    # Bulk import from ψ/memory/learnings/
"""

import chromadb
import hashlib
import sys
import json
from pathlib import Path
from datetime import datetime
from ollama_embedding import OllamaEmbeddingFunction

CHROMA_PATH = Path(__file__).parent / "ψ" / "memory" / "chroma_db"
LEARNINGS_DIR = Path(__file__).parent / "ψ" / "memory" / "learnings"

EMBED_FN = OllamaEmbeddingFunction()


def get_client():
    return chromadb.PersistentClient(path=str(CHROMA_PATH))


def remember(text: str, agent: str = "pa-oracle", tags: list[str] | None = None):
    """Store a memory in ChromaDB."""
    client = get_client()
    memories = client.get_or_create_collection("memories", embedding_function=EMBED_FN)

    doc_id = hashlib.md5(text.encode()).hexdigest()[:12]
    metadata = {
        "agent": agent,
        "timestamp": datetime.utcnow().isoformat(),
        "tags": ",".join(tags) if tags else "",
    }

    memories.upsert(
        documents=[text],
        ids=[doc_id],
        metadatas=[metadata],
    )
    return doc_id


def recall(query: str, n: int = 5, agent: str | None = None):
    """Search across all collections by semantic similarity."""
    client = get_client()
    output = []

    for col_ref in client.list_collections():
        if col_ref.count() == 0:
            continue
        col = client.get_collection(col_ref.name, embedding_function=EMBED_FN)
        where = {"agent": agent} if agent else None
        try:
            results = col.query(
                query_texts=[query],
                n_results=min(n, col.count()),
                where=where,
            )
        except Exception:
            results = col.query(
                query_texts=[query],
                n_results=min(n, col.count()),
            )

        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i] if results["metadatas"] else {}
            dist = results["distances"][0][i] if results["distances"] else 0
            output.append({
                "text": doc,
                "collection": col.name,
                "agent": meta.get("agent", ""),
                "tags": meta.get("tags", ""),
                "source": meta.get("source", ""),
                "distance": round(dist, 4),
            })

    output.sort(key=lambda x: x["distance"])
    return output[:n]


def ingest_learnings():
    """Bulk import all markdown files from ψ/memory/learnings/ into ChromaDB."""
    if not LEARNINGS_DIR.exists():
        print("No learnings directory found")
        return 0

    client = get_client()
    knowledge = client.get_or_create_collection("knowledge", embedding_function=EMBED_FN)
    count = 0

    for md_file in LEARNINGS_DIR.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        doc_id = f"learning_{md_file.stem}"

        # Extract tags from content
        tags = []
        for line in content.split("\n"):
            if line.startswith("**Tags**:") or line.startswith("Tags:"):
                tags = [t.strip() for t in line.split(":", 1)[1].split(",")]
                break

        metadata = {
            "source": md_file.name,
            "type": "learning",
            "agent": "pa-oracle",
            "timestamp": datetime.utcnow().isoformat(),
            "tags": ",".join(tags),
        }

        knowledge.upsert(
            documents=[content],
            ids=[doc_id],
            metadatas=[metadata],
        )
        count += 1
        print(f"  + {md_file.name}")

    return count


def status():
    """Show ChromaDB status with counts."""
    client = get_client()
    collections = client.list_collections()
    total = 0
    for col in collections:
        c = col.count()
        total += c
        print(f"  {col.name}: {c} documents")
    print(f"  Total: {total} documents")
    return total


def main():
    if len(sys.argv) < 2:
        print("Usage: python chroma_agent.py [remember|recall|status|ingest-learnings]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "remember":
        text = sys.argv[2] if len(sys.argv) > 2 else ""
        if not text:
            print("Usage: python chroma_agent.py remember 'text' --tags t1,t2 --agent name")
            sys.exit(1)
        tags = []
        agent = "pa-oracle"
        for i, arg in enumerate(sys.argv):
            if arg == "--tags" and i + 1 < len(sys.argv):
                tags = sys.argv[i + 1].split(",")
            if arg == "--agent" and i + 1 < len(sys.argv):
                agent = sys.argv[i + 1]
        doc_id = remember(text, agent, tags)
        print(f"Remembered: {doc_id} (agent: {agent})")

    elif cmd == "recall":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        if not query:
            print("Usage: python chroma_agent.py recall 'query' --n 5 --agent name")
            sys.exit(1)
        n = 5
        agent = None
        for i, arg in enumerate(sys.argv):
            if arg == "--n" and i + 1 < len(sys.argv):
                n = int(sys.argv[i + 1])
            if arg == "--agent" and i + 1 < len(sys.argv):
                agent = sys.argv[i + 1]
        results = recall(query, n, agent)
        if not results:
            print("No memories found.")
        else:
            for r in results:
                print(f"\n--- [{r['agent']}] (dist: {r['distance']}) ---")
                print(r["text"][:200])

    elif cmd == "status":
        print("ChromaDB Status:")
        status()

    elif cmd == "ingest-learnings":
        print("Ingesting learnings...")
        count = ingest_learnings()
        print(f"\nIngested {count} learnings into ChromaDB")

    elif cmd == "json":
        # JSON output for agent integration
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        results = recall(query, 5)
        print(json.dumps(results, ensure_ascii=False, indent=2))

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
