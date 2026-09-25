import os
import math
from typing import List, Dict, Any
from src.config import EMBEDDING_MODEL_NAME

try:
    from sentence_transformers import SentenceTransformer
    HAS_ST = True
except ImportError:
    HAS_ST = False

class VectorStore:
    """Local vector database for RAG document retrieval using SentenceTransformers embeddings."""

    def __init__(self):
        self.encoder = None
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: List[List[float]] = []

        if HAS_ST:
            try:
                # Load lightweight sentence transformer model
                self.encoder = SentenceTransformer(EMBEDDING_MODEL_NAME)
            except Exception as e:
                print(f"[VectorStore Warning] Could not load SentenceTransformer ({e}). Fallback to TF-IDF matching.")

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """Indexes text chunks with metadata embeddings."""
        self.chunks = chunks
        texts = [c["text"] for c in chunks]

        if self.encoder:
            try:
                self.embeddings = self.encoder.encode(texts, convert_to_numpy=True).tolist()
            except Exception as e:
                print(f"[VectorStore] Embedding error: {e}")
                self.embeddings = []

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Performs semantic search over indexed document chunks."""
        if not self.chunks:
            return []

        # Vector search if embeddings exist
        if self.encoder and self.embeddings:
            query_vec = self.encoder.encode(query, convert_to_numpy=True).tolist()
            scores = []
            for i, emb in enumerate(self.embeddings):
                sim = self._cosine_similarity(query_vec, emb)
                scores.append((sim, self.chunks[i]))
            
            scores.sort(key=lambda x: x[0], reverse=True)
            results = []
            for sim, chunk in scores[:top_k]:
                item = chunk.copy()
                item["score"] = round(sim, 4)
                results.append(item)
            return results

        # Keyword matching fallback if model isn't available
        query_words = set(query.lower().split())
        keyword_scores = []
        for chunk in self.chunks:
            chunk_words = set(chunk["text"].lower().split())
            overlap = len(query_words.intersection(chunk_words))
            score = overlap / (len(query_words) + 1)
            keyword_scores.append((score, chunk))

        keyword_scores.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, chunk in keyword_scores[:top_k]:
            item = chunk.copy()
            item["score"] = round(score, 4)
            results.append(item)
        return results
