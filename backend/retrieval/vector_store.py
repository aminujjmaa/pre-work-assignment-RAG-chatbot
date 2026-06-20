"""
ChromaDB vector store wrapper.
Uses persistent HNSW index. One collection: 'rag_documents'.
"""
from __future__ import annotations
import chromadb
from chromadb.config import Settings as ChromaSettings
from config import settings
from typing import List, Dict, Any, Optional
import numpy as np

_client: Optional[chromadb.PersistentClient] = None
_collection = None
COLLECTION_NAME = "rag_documents"


def get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.CHROMA_PATH,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _client


def get_collection():
    global _collection
    if _collection is None:
        client = get_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_chunks(
    doc_id: str,
    filename: str,
    chunks: List[Dict[str, Any]],
    embeddings: np.ndarray,
) -> None:
    col = get_collection()
    ids, docs, metas, embeds = [], [], [], []

    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        chunk_id = f"{doc_id}_{chunk['chunk_idx']}"
        ids.append(chunk_id)
        docs.append(chunk["text"])
        metas.append({
            "doc_id": doc_id,
            "filename": filename,
            "page_start": chunk["page_start"],
            "page_end": chunk["page_end"],
            "chunk_idx": chunk["chunk_idx"],
            "word_count": chunk["word_count"],
        })
        embeds.append(emb.tolist())

    # Upsert in batches of 500
    batch = 500
    for start in range(0, len(ids), batch):
        col.upsert(
            ids=ids[start:start+batch],
            documents=docs[start:start+batch],
            metadatas=metas[start:start+batch],
            embeddings=embeds[start:start+batch],
        )


def query_similar(
    query_embedding: np.ndarray,
    top_k: int = 8,
) -> List[Dict[str, Any]]:
    col = get_collection()
    n_items = col.count()
    if n_items == 0:
        return []

    k = min(top_k, n_items)
    results = col.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({
            "text": doc,
            "metadata": meta,
            "score": float(1 - dist),  # cosine distance → similarity
        })
    return hits


def delete_document(doc_id: str) -> None:
    col = get_collection()
    col.delete(where={"doc_id": doc_id})


def collection_stats() -> Dict[str, int]:
    col = get_collection()
    return {"total_chunks": col.count()}
