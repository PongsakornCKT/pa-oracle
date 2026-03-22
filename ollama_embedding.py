"""
pa Oracle — Ollama Embedding Function for ChromaDB
bge-m3 | 1024 dim | Multilingual (Thai + English) | Local GPU
"""

import json
import urllib.request
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings

OLLAMA_URL = "http://localhost:11434/api/embed"
DEFAULT_MODEL = "nomic-embed-text"


class OllamaEmbeddingFunction(EmbeddingFunction[Documents]):
    def __init__(self, model: str = DEFAULT_MODEL, url: str = OLLAMA_URL):
        self.model = model
        self.url = url

    def __call__(self, input: Documents) -> Embeddings:
        # Ollama supports batch embedding natively
        data = json.dumps({"model": self.model, "input": input}).encode()
        req = urllib.request.Request(self.url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
        return result["embeddings"]


# Single instance for reuse
embed_fn = OllamaEmbeddingFunction()
