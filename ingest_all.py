"""
pa Oracle — Ingest All Sources into ChromaDB
Scans repos, skills, and memory for .md files → Gemini embeddings
"""

import hashlib
import sys
from pathlib import Path
from datetime import datetime
from ollama_embedding import OllamaEmbeddingFunction
import chromadb
import time

CHROMA_PATH = Path(__file__).parent / "ψ" / "memory" / "chroma_db"
EMBED_FN = OllamaEmbeddingFunction()

# Sources to ingest
SOURCES = {
    "nasri-oracle": {
        "paths": [Path("C:/Users/pO-Ch/Nasri-oracle")],
        "color": "#b388ff",  # purple
    },
    "nat-brain": {
        "paths": [Path("C:/Users/pO-Ch/Documents/GitHub/opensource-nat-brain-oracle")],
        "color": "#ffd54f",  # yellow
    },
    "pa-oracle": {
        "paths": [Path("C:/Users/pO-Ch/Documents/GitHub/pa-Oracle v2")],
        "color": "#c9a84c",  # gold
        "exclude": ["node_modules", ".venv", "chroma_db", "maw-js", "dist"],
    },
    "skills": {
        "paths": [Path("C:/Users/pO-Ch/.claude/skills")],
        "color": "#f48fb1",  # pink
    },
    "oracle-skills-cli": {
        "paths": [Path("C:/Users/pO-Ch/Documents/GitHub/oracle-skills-cli")],
        "color": "#ef5350",  # red
    },
    "arra-oracle": {
        "paths": [
            Path("C:/Users/pO-Ch/Documents/GitHub/arra-oracle"),
            Path("C:/Users/pO-Ch/Documents/GitHub/arra-oracle-v3"),
        ],
        "color": "#64b5f6",  # blue
    },
    "maw-js": {
        "paths": [Path("C:/Users/pO-Ch/Documents/GitHub/maw-js")],
        "color": "#66bb6a",  # green
        "exclude": ["node_modules", "dist"],
    },
    "probe-oracle": {
        "paths": [Path("C:/Users/pO-Ch/Documents/GitHub/probe-oracle")],
        "color": "#ffffff",  # white
    },
}

GLOBAL_EXCLUDE = ["node_modules", ".venv", ".git", "__pycache__", "chroma_db", "dist-office", "dist-cf", ".cache"]


def find_md_files(base_path: Path, exclude: list[str] | None = None) -> list[Path]:
    """Find all .md files, excluding specified dirs."""
    excludes = set(GLOBAL_EXCLUDE + (exclude or []))
    results = []
    if not base_path.exists():
        return results
    for md in base_path.rglob("*.md"):
        parts = set(md.parts)
        if not parts.intersection(excludes):
            results.append(md)
    return results


def chunk_text(text: str, max_chars: int = 2000) -> list[str]:
    """Split text into chunks at paragraph boundaries."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    paragraphs = text.split("\n\n")
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 > max_chars:
            if current:
                chunks.append(current.strip())
            current = para
        else:
            current = current + "\n\n" + para if current else para

    if current.strip():
        chunks.append(current.strip())

    return chunks if chunks else [text[:max_chars]]


def ingest_source(source_name: str, config: dict, collection) -> int:
    """Ingest all .md files from a source into ChromaDB."""
    count = 0
    exclude = config.get("exclude", [])

    for base_path in config["paths"]:
        if not base_path.exists():
            print(f"    SKIP {base_path} (not found)")
            continue

        files = find_md_files(base_path, exclude)
        print(f"    {base_path.name}: {len(files)} files")

        ids = []
        docs = []
        metas = []

        for md_file in files:
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            if len(content.strip()) < 20:
                continue

            chunks = chunk_text(content)
            for i, chunk in enumerate(chunks):
                doc_id = hashlib.md5(f"{source_name}:{md_file}:{i}".encode()).hexdigest()[:16]
                rel_path = str(md_file.relative_to(base_path)) if md_file.is_relative_to(base_path) else md_file.name

                ids.append(doc_id)
                docs.append(chunk)
                metas.append({
                    "source": source_name,
                    "file": rel_path,
                    "color": config["color"],
                    "chunk": i,
                    "total_chunks": len(chunks),
                })

        # Batch add (10 at a time — small to prevent HNSW corruption)
        batch_size = 10
        for i in range(0, len(ids), batch_size):
            end = min(i + batch_size, len(ids))
            try:
                # Use add (not upsert) — skip duplicates
                collection.add(
                    ids=ids[i:end],
                    documents=docs[i:end],
                    metadatas=metas[i:end],
                )
                count += end - i
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    count += end - i  # Already there
                else:
                    print(f"      ERROR batch {i//batch_size + 1}: {e}")

            # Rate limit
            if i + batch_size < len(ids):
                time.sleep(0.05)

        print(f"      {count} total docs so far")

    return count


def main():
    print("pa Oracle — Ingest All Sources")
    print("=" * 50)

    client = chromadb.PersistentClient(path=str(CHROMA_PATH))

    print(f"ChromaDB: {CHROMA_PATH}")
    print()

    total = 0
    for source_name, config in SOURCES.items():
        # Each source gets its own collection to avoid HNSW corruption
        col = client.get_or_create_collection(
            name=f"kb_{source_name.replace('-', '_')}",
            embedding_function=EMBED_FN,
            metadata={
                "description": f"Knowledge from {source_name}",
                "source": source_name,
                "color": config["color"],
            },
        )
        print(f"  [{source_name}] → collection kb_{source_name.replace('-', '_')}")
        count = ingest_source(source_name, config, col)
        total += count
        print(f"    → {count} docs ingested (total in col: {col.count()})")
        print()

    print("=" * 50)
    print(f"Total ingested: {total}")
    collections = client.list_collections()
    grand = sum(c.count() for c in collections)
    print(f"Grand total across {len(collections)} collections: {grand}")


if __name__ == "__main__":
    main()
