from __future__ import annotations
"""
Cross-encoder reranker using ms-marco-MiniLM-L-6-v2.
Scores (query, passage) pairs and re-orders candidates.
"""
from sentence_transformers.cross_encoder import CrossEncoder
from config import settings
from typing import List, Dict, Any

_reranker: CrossEncoder | None = None


def get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(settings.RERANKER_MODEL, max_length=512)
    return _reranker


def rerank(query: str, hits: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
    """Rerank hits using cross-encoder; return top_k with updated scores."""
    if not hits:
        return hits

    reranker = get_reranker()
    pairs = [(query, h["text"]) for h in hits]
    scores = reranker.predict(pairs, show_progress_bar=False)

    for hit, score in zip(hits, scores):
        hit["rerank_score"] = float(score)

    ranked = sorted(hits, key=lambda x: x["rerank_score"], reverse=True)
    return ranked[:top_k]
