"""
Chat route: POST /api/chat streams answer via Server-Sent Events.
Flow: embed query → ChromaDB search → rerank → Ollama stream → SSE
"""
import json
import time
from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from retrieval.embedder import embed_query
from retrieval.vector_store import query_similar
from retrieval.reranker import rerank
from generation.llm import stream_response, check_llm
from config import settings

router = APIRouter(prefix="/api")


class ChatRequest(BaseModel):
    query: str
    use_reranker: bool = True


async def _event_stream(query: str, use_reranker: bool) -> AsyncGenerator[str, None]:
    t0 = time.perf_counter()

    def send(obj: dict) -> str:
        return f"data: {json.dumps(obj)}\n\n"

    yield send({"type": "status", "message": "Embedding query…"})

    # 1. Embed query
    q_emb = embed_query(query)
    t1 = time.perf_counter()

    yield send({"type": "status", "message": "Searching vector DB…"})

    # 2. ANN search
    hits = query_similar(q_emb, top_k=settings.TOP_K_RETRIEVE)
    if not hits:
        yield send({"type": "error", "message": "No documents in the knowledge base. Please upload PDFs first."})
        return

    t2 = time.perf_counter()
    yield send({"type": "status", "message": f"Retrieved {len(hits)} chunks, reranking…"})

    # 3. Rerank
    if use_reranker:
        ranked = rerank(query, hits, top_k=settings.TOP_K_RERANK)
    else:
        ranked = hits[:settings.TOP_K_RERANK]

    t3 = time.perf_counter()

    # Send chunk metadata to frontend for visualization
    yield send({
        "type": "chunks",
        "chunks": [
            {
                "text": h["text"][:300] + ("…" if len(h["text"]) > 300 else ""),
                "filename": h["metadata"]["filename"],
                "page_start": h["metadata"]["page_start"],
                "page_end": h["metadata"]["page_end"],
                "score": round(h.get("rerank_score", h["score"]), 4),
            }
            for h in ranked
        ],
    })

    yield send({"type": "status", "message": "Generating answer…"})

    # 4. Stream LLM answer
    try:
        async for token in stream_response(query, ranked):
            yield send({"type": "token", "content": token})
    except Exception as exc:
        msg = str(exc)
        yield send({"type": "error", "message": f"❌ {msg}"})
        return

    t4 = time.perf_counter()

    # Latency breakdown
    latency = {
        "embed_ms": round((t1 - t0) * 1000),
        "search_ms": round((t2 - t1) * 1000),
        "rerank_ms": round((t3 - t2) * 1000),
        "llm_ms": round((t4 - t3) * 1000),
        "total_ms": round((t4 - t0) * 1000),
    }

    # Citations
    seen = set()
    citations = []
    for h in ranked:
        key = (h["metadata"]["filename"], h["metadata"]["page_start"])
        if key not in seen:
            seen.add(key)
            citations.append({
                "filename": h["metadata"]["filename"],
                "page_start": h["metadata"]["page_start"],
                "page_end": h["metadata"]["page_end"],
            })

    yield send({"type": "done", "citations": citations, "latency": latency})


@router.post("/chat")
async def chat(req: ChatRequest):
    return StreamingResponse(
        _event_stream(req.query, req.use_reranker),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/health")
async def health():
    llm = await check_llm()
    return {
        "status": "ok",
        "llm": llm,
        "embedding_model": settings.EMBEDDING_MODEL,
        "llm_model": settings.GROQ_MODEL if settings.GROQ_API_KEY else settings.OLLAMA_MODEL,
        "llm_backend": "groq" if settings.GROQ_API_KEY else "ollama",
    }
