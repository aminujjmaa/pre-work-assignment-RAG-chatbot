"""
FastAPI application entry point.
Serves REST API + static frontend from /static.
"""
import sys
import os
import logging

# Silence noisy telemetry from ChromaDB
logging.getLogger("chromadb.telemetry").setLevel(logging.ERROR)
logging.getLogger("chromadb").setLevel(logging.WARNING)
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from db.database import init_db
from routes.ingest import router as ingest_router
from routes.chat import router as chat_router
from config import settings

app = FastAPI(
    title="RAG Scholar",
    description="Retrieval-Augmented Generation chatbot over private PDF corpus",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest_router)
app.include_router(chat_router)

# Serve frontend
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
def serve_frontend():
    index = static_dir / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"message": "RAG Scholar API running. Frontend not found."}


@app.on_event("startup")
def startup():
    init_db()
    # Warm up embedding model in background
    import threading
    def _warm():
        try:
            from retrieval.embedder import embed_query
            embed_query("warm up")
        except Exception:
            pass
    threading.Thread(target=_warm, daemon=True).start()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
