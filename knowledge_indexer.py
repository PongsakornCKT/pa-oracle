"""
pa Oracle — Knowledge Auto-Indexer
Watches for new/changed .md files → auto-ingest into ChromaDB → regenerate knowledge-data.json

Usage:
  python knowledge_indexer.py              # Run once + watch
  python knowledge_indexer.py --once       # Run once only
  python knowledge_indexer.py --rebuild    # Full rebuild
"""

import chromadb
import hashlib
import json
import math
import os
import random
import sys
import time
from pathlib import Path
from datetime import datetime
from ollama_embedding import OllamaEmbeddingFunction

CHROMA_PATH = Path(__file__).parent / "ψ" / "memory" / "chroma_db"
OUTPUT_PATH = Path(__file__).parent / "maw-js" / "dist-office" / "knowledge-data.json"
PUBLIC_PATH = Path(__file__).parent / "maw-js" / "office" / "public" / "knowledge-data.json"
EMBED_FN = OllamaEmbeddingFunction()
POLL_INTERVAL = 60  # seconds
MAX_PER_COLLECTION = 500
GLOBAL_EXCLUDE = ["node_modules", ".venv", ".git", "__pycache__", "chroma_db", "dist-office", "dist-cf", ".cache", "dist"]

SOURCES = {
    "nasri-oracle": {"paths": [Path("C:/Users/pO-Ch/Nasri-oracle")], "color": "#b388ff"},
    "nat-brain": {"paths": [Path("C:/Users/pO-Ch/Documents/GitHub/opensource-nat-brain-oracle")], "color": "#ffd54f"},
    "pa-oracle": {"paths": [Path("C:/Users/pO-Ch/Documents/GitHub/pa-Oracle v2")], "color": "#c9a84c", "exclude": ["maw-js"]},
    "skills": {"paths": [Path("C:/Users/pO-Ch/.claude/skills")], "color": "#f48fb1"},
    "oracle-skills-cli": {"paths": [Path("C:/Users/pO-Ch/Documents/GitHub/oracle-skills-cli")], "color": "#ef5350"},
    "arra-oracle": {"paths": [Path("C:/Users/pO-Ch/Documents/GitHub/arra-oracle"), Path("C:/Users/pO-Ch/Documents/GitHub/arra-oracle-v3")], "color": "#64b5f6"},
    "maw-js": {"paths": [Path("C:/Users/pO-Ch/Documents/GitHub/maw-js")], "color": "#66bb6a", "exclude": ["node_modules", "dist"]},
    "probe-oracle": {"paths": [Path("C:/Users/pO-Ch/Documents/GitHub/probe-oracle")], "color": "#ffffff"},
}

# Track file mtimes for change detection
_file_mtimes: dict[str, float] = {}


def chunk_text(text: str, max_chars: int = 2000) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    chunks, current = [], ""
    for para in text.split("\n\n"):
        if len(current) + len(para) + 2 > max_chars:
            if current:
                chunks.append(current.strip())
            current = para
        else:
            current = current + "\n\n" + para if current else para
    if current.strip():
        chunks.append(current.strip())
    return chunks or [text[:max_chars]]


def find_md_files(base_path: Path, exclude: list[str] | None = None) -> list[Path]:
    excludes = set(GLOBAL_EXCLUDE + (exclude or []))
    if not base_path.exists():
        return []
    return [f for f in base_path.rglob("*.md") if not set(f.parts).intersection(excludes)]


def scan_changes() -> dict[str, list[Path]]:
    """Scan all sources for new/changed files. Returns {source: [changed_files]}."""
    changes: dict[str, list[Path]] = {}

    for source, config in SOURCES.items():
        changed = []
        for base in config["paths"]:
            for f in find_md_files(base, config.get("exclude", [])):
                key = str(f)
                try:
                    mtime = f.stat().st_mtime
                except OSError:
                    continue
                if key not in _file_mtimes or _file_mtimes[key] < mtime:
                    _file_mtimes[key] = mtime
                    changed.append(f)
        if changed:
            changes[source] = changed

    return changes


def ingest_files(source: str, files: list[Path], config: dict):
    """Ingest changed files into ChromaDB."""
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    color = config["color"]

    ids, docs, metas = [], [], []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if len(content.strip()) < 20:
            continue

        base_path = None
        for p in config["paths"]:
            if f.is_relative_to(p):
                base_path = p
                break

        for i, chunk in enumerate(chunk_text(content)):
            doc_id = hashlib.md5(f"{source}:{f}:{i}".encode()).hexdigest()[:16]
            ids.append(doc_id)
            docs.append(chunk)
            metas.append({
                "source": source,
                "file": f.relative_to(base_path).as_posix() if base_path and f.is_relative_to(base_path) else f.name,
                "color": color,
                "chunk": i,
            })

    if not ids:
        return 0

    # Find or create collection with space
    col_idx = 0
    while True:
        col_name = f"kb_{source.replace('-', '_')}_{col_idx}" if col_idx > 0 else f"kb_{source.replace('-', '_')}"
        col = client.get_or_create_collection(
            name=col_name,
            embedding_function=EMBED_FN,
            metadata={"source": source, "color": color},
        )
        try:
            cnt = col.count()
        except Exception:
            col_idx += 1
            continue

        if cnt < MAX_PER_COLLECTION:
            break
        col_idx += 1

    # Batch add
    added = 0
    batch_size = 10
    for i in range(0, len(ids), batch_size):
        end = min(i + batch_size, len(ids))
        try:
            col.upsert(ids=ids[i:end], documents=docs[i:end], metadatas=metas[i:end])
            added += end - i
        except Exception:
            pass
        time.sleep(0.05)

    return added


def generate_json():
    """Generate knowledge-data.json from ChromaDB."""
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    collections = [c for c in client.list_collections() if c.name.startswith("kb_")]

    sources = {}
    all_emb, all_meta = [], []

    for col in collections:
        try:
            cnt = col.count()
        except Exception:
            continue
        src = col.metadata.get("source", col.name)
        color = col.metadata.get("color", "#fff")
        sources[src] = sources.get(src, 0) + cnt

        for off in range(0, cnt, 200):
            try:
                d = col.get(include=["embeddings", "metadatas", "documents"], limit=200, offset=off)
                for i in range(len(d["ids"])):
                    e = d["embeddings"][i] if d["embeddings"] is not None else None
                    if e is None:
                        continue
                    m = d["metadatas"][i] if d["metadatas"] is not None else {}
                    doc = d["documents"][i] if d["documents"] is not None else ""
                    el = e.tolist() if hasattr(e, "tolist") else list(e)
                    all_emb.append(el)
                    all_meta.append({
                        "id": d["ids"][i],
                        "s": m.get("source", src),
                        "c": m.get("color", color),
                        "f": m.get("file", ""),
                        "p": doc[:120],
                    })
            except Exception:
                continue

    # Random projection 768→3D
    dim = 768
    random.seed(42)
    axes = []
    for _ in range(3):
        a = [random.gauss(0, 1) for _ in range(dim)]
        n = math.sqrt(sum(x * x for x in a))
        axes.append([x / n for x in a])

    coords = []
    for e in all_emb:
        coords.append(tuple(sum(e[j] * axes[k][j] for j in range(min(len(e), dim))) for k in range(3)))

    def norm(vals):
        mn, mx = min(vals) if vals else 0, max(vals) if vals else 1
        r = mx - mn or 1
        return [(v - mn) / r * 4 - 2 for v in vals]

    if coords:
        nx, ny, nz = norm([c[0] for c in coords]), norm([c[1] for c in coords]), norm([c[2] for c in coords])
    else:
        nx, ny, nz = [], [], []

    pts = []
    for i, m in enumerate(all_meta):
        f = m["f"].lower()
        preview = m["p"].lower()
        if "learning" in f:
            cat = "learning"
        elif "retrospective" in f or "retro" in f:
            cat = "retro"
        elif "principle" in preview or "philosophy" in f or "claude.md" == m["f"].lower() or "nothing is deleted" in preview:
            cat = "principle"
        elif "skill" in f or m["s"] == "skills":
            cat = "skill"
        else:
            cat = "doc"

        pts.append({**m, "x": round(nx[i], 4), "y": round(ny[i], 4), "z": round(nz[i], 4), "cat": cat})

    cats = {}
    for p in pts:
        cats[p["cat"]] = cats.get(p["cat"], 0) + 1

    result = {
        "total": len(pts),
        "sources": sources,
        "embedding": "nomic-embed-text",
        "documentsMappped": len(set(p["f"] for p in pts)),
        "categories": {
            "learnings": cats.get("learning", 0),
            "retros": cats.get("retro", 0),
            "principles": cats.get("principle", 0),
            "skills": cats.get("skill", 0),
            "docs": cats.get("doc", 0),
        },
        "points": pts,
        "updatedAt": datetime.utcnow().isoformat(),
    }

    for path in [OUTPUT_PATH, PUBLIC_PATH]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result), encoding="utf-8")

    return result


def run_once():
    """Scan for changes, ingest, regenerate JSON."""
    changes = scan_changes()
    if not changes:
        return False

    total_new = 0
    for source, files in changes.items():
        n = ingest_files(source, files, SOURCES[source])
        total_new += n
        if n > 0:
            print(f"  +{n} docs from {source} ({len(files)} files)")

    if total_new > 0:
        result = generate_json()
        print(f"  Regenerated: {result['total']} points, {result['documentsMappped']} docs")
        return True

    return False


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--watch"

    if mode == "--rebuild":
        print("Full rebuild...")
        # Clear file cache to force re-scan
        _file_mtimes.clear()
        run_once()
        return

    if mode == "--once":
        print("Single scan...")
        if not run_once():
            print("  No changes found")
            # Still generate if no JSON exists
            if not OUTPUT_PATH.exists():
                result = generate_json()
                print(f"  Generated: {result['total']} points")
        return

    # Watch mode
    print(f"Knowledge Auto-Indexer started (poll every {POLL_INTERVAL}s)")
    print(f"  Sources: {list(SOURCES.keys())}")
    print(f"  Output: {OUTPUT_PATH}")

    # Initial scan
    run_once()

    while True:
        time.sleep(POLL_INTERVAL)
        try:
            if run_once():
                ts = datetime.now().strftime("%H:%M:%S")
                print(f"  [{ts}] Index updated")
        except Exception as e:
            print(f"  ERROR: {e}")


if __name__ == "__main__":
    main()
