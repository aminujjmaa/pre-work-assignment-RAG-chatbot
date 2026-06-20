from __future__ import annotations
"""
Singleton embedder using sentence-transformers all-MiniLM-L6-v2.
Model is loaded once and reused across requests.
"""
from sentence_transformers import SentenceTransformer
from config import settings
from typing import List
import numpy as np

_model: SentenceTransformer | None = None


def get_embedder() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model


def embed_texts(texts: List[str], batch_size: int = 64) -> np.ndarray:
    """Return L2-normalised embeddings for a list of texts."""
    model = get_embedder()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=False,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return embeddings


def embed_query(query: str) -> np.ndarray:
    return embed_texts([query])[0]
