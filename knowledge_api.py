"""
pa Oracle — Knowledge Map API
Serves embeddings + search for the 3D visualization
"""

import json
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import chromadb
from ollama_embedding import OllamaEmbeddingFunction

CHROMA_PATH = Path(__file__).parent / "ψ" / "memory" / "chroma_db"
EMBED_FN = OllamaEmbeddingFunction()
PORT = 4001


def get_client():
    return chromadb.PersistentClient(path=str(CHROMA_PATH))


def get_kb_collections():
    """Get all kb_* collections."""
    client = get_client()
    return [c for c in client.list_collections() if c.name.startswith("kb_")]


class KnowledgeHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send_json(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/api/knowledge/stats":
            self._send_json(self._stats())
        elif parsed.path == "/api/knowledge/embeddings":
            limit = int(params.get("limit", [500])[0])
            offset = int(params.get("offset", [0])[0])
            self._send_json(self._embeddings(limit, offset))
        elif parsed.path == "/api/knowledge/search":
            q = params.get("q", [""])[0]
            n = int(params.get("n", [20])[0])
            self._send_json(self._search(q, n))
        elif parsed.path == "/api/knowledge/sources":
            self._send_json(self._sources())
        else:
            self._send_json({"error": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/knowledge/reindex":
            self._reindex()
        else:
            self._send_json({"error": "not found"})

    def _reindex(self):
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, "knowledge_indexer.py", "--once"],
                capture_output=True, text=True, timeout=300,
                cwd=str(Path(__file__).parent),
            )
            output = result.stdout + result.stderr
            # Read generated JSON to get total
            data_path = Path(__file__).parent / "maw-js" / "dist-office" / "knowledge-data.json"
            total = 0
            if data_path.exists():
                import json as _json
                d = _json.loads(data_path.read_text())
                total = d.get("total", 0)
                # Also copy to maw serve
                dst = Path("/tmp/maw-js-server/dist-office/knowledge-data.json")
                if dst.parent.exists():
                    dst.write_text(data_path.read_text())
            self._send_json({"ok": True, "total": total, "output": output[:500]})
        except Exception as e:
            self._send_json({"error": str(e)})

    def do_OPTIONS(self):
        body = b""
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _stats(self):
        collections = get_kb_collections()
        total = 0
        by_source = {}
        for col in collections:
            try:
                cnt = col.count()
            except Exception:
                continue
            total += cnt
            src = col.metadata.get("source", col.name)
            by_source[src] = by_source.get(src, 0) + cnt

        return {
            "total": total,
            "sources": by_source,
            "embedding": "nomic-embed-text (Ollama)",
            "dimensions": 768,
        }

    def _embeddings(self, limit: int, offset: int):
        collections = get_kb_collections()
        total = 0
        safe_cols = []
        for c in collections:
            try:
                cnt = c.count()
                total += cnt
                safe_cols.append((c, cnt))
            except Exception:
                continue

        points = []
        remaining = limit
        skip = offset

        for col, cnt in safe_cols:
            if skip >= cnt:
                skip -= cnt
                continue

            fetch = min(remaining, cnt - skip)
            if fetch <= 0:
                continue

            try:
                data = col.get(
                    include=["embeddings", "metadatas", "documents"],
                    limit=fetch,
                    offset=skip,
                )
            except Exception:
                skip = 0
                continue
            skip = 0

            src = col.metadata.get("source", col.name)
            color = col.metadata.get("color", "#ffffff")

            for i in range(len(data["ids"])):
                raw_emb = data["embeddings"][i] if data["embeddings"] is not None else None
                emb = raw_emb.tolist() if hasattr(raw_emb, "tolist") else raw_emb
                meta = data["metadatas"][i] if data["metadatas"] is not None else {}
                doc = data["documents"][i] if data["documents"] is not None else ""

                points.append({
                    "id": data["ids"][i],
                    "embedding": emb,
                    "source": meta.get("source", src),
                    "color": meta.get("color", color),
                    "file": meta.get("file", ""),
                    "preview": doc[:150] if doc else "",
                })

            remaining -= len(data["ids"])
            if remaining <= 0:
                break

        return {
            "total": total,
            "offset": offset,
            "count": len(points),
            "points": points,
        }

    def _search(self, query: str, n: int):
        if not query:
            return {"results": []}

        client = get_client()
        collections = get_kb_collections()
        all_items = []

        for col_ref in collections:
            try:
                cnt = col_ref.count()
                if cnt == 0:
                    continue
                col = client.get_collection(col_ref.name, embedding_function=EMBED_FN)
                src = col_ref.metadata.get("source", col_ref.name)
                color = col_ref.metadata.get("color", "#ffffff")

                results = col.query(
                    query_texts=[query],
                    n_results=min(n, cnt),
                    include=["metadatas", "documents", "distances"],
                )

                for i in range(len(results["ids"][0])):
                    meta = results["metadatas"][0][i] if results["metadatas"] else {}
                    all_items.append({
                        "id": results["ids"][0][i],
                        "source": meta.get("source", src),
                        "file": meta.get("file", ""),
                        "color": meta.get("color", color),
                        "preview": results["documents"][0][i][:300],
                        "distance": round(results["distances"][0][i], 4),
                    })
            except Exception:
                continue  # Skip broken collections

        all_items.sort(key=lambda x: x["distance"])
        return {"query": query, "results": all_items[:n]}

    def _sources(self):
        collections = get_kb_collections()
        merged = {}
        for col in collections:
            try:
                cnt = col.count()
            except Exception:
                continue
            src = col.metadata.get("source", col.name)
            color = col.metadata.get("color", "#ffffff")
            if src not in merged:
                merged[src] = {"name": src, "count": 0, "color": color}
            merged[src]["count"] += cnt

        return sorted(merged.values(), key=lambda x: -x["count"])

    def log_message(self, format, *args):
        pass  # Suppress logs


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    server = HTTPServer(("0.0.0.0", port), KnowledgeHandler)
    print(f"Knowledge API -> http://localhost:{port}")
    print(f"  /api/knowledge/stats")
    print(f"  /api/knowledge/embeddings?limit=500&offset=0")
    print(f"  /api/knowledge/search?q=query&n=20")
    print(f"  /api/knowledge/sources")
    server.serve_forever()


if __name__ == "__main__":
    main()
