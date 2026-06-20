# RAG Scholar — AI-Powered PDF Chatbot

## 🚀 Quick Start (Run These Commands in Order)

### Step 1 — Install Everything
```bash
bash /home/dell/hackathon/install_all.sh
```
This installs: Tesseract OCR, Python venv, CPU PyTorch, all Python packages, and pulls `llama3.2:3b` Ollama model.

### Step 2 — Download 10 Sample PDFs (optional, for demo)
```bash
python3 /home/dell/hackathon/download_pdfs.py
```
Downloads 10 classic public-domain books (200+ pages each) from Project Gutenberg.

### Step 3 — Bulk Ingest PDFs (optional CLI method)
```bash
/home/dell/hackathon/backend/.venv/bin/python3 /home/dell/hackathon/bulk_ingest.py
```

### Step 4 — Start the Server
```bash
bash /home/dell/hackathon/run_all.sh
```
Opens at: **http://localhost:8000**

---

## 📁 Project Structure
```
hackathon/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── static/index.html    # Web UI
│   ├── ingestion/           # PDF parser + chunker + pipeline
│   ├── retrieval/           # Embedder + ChromaDB + reranker
│   ├── generation/          # Ollama LLM streaming
│   ├── routes/              # ingest + chat API endpoints
│   └── db/                  # SQLite models
├── install_all.sh           # One-shot install
├── run_all.sh               # Start server
├── download_pdfs.py         # Download 10 sample PDFs
└── bulk_ingest.py           # CLI bulk ingestion
```

## 🔧 Stack (all free/open-source)

| Component | Technology |
|-----------|-----------|
| PDF parsing | PyMuPDF + pytesseract (OCR) |
| Embeddings | `all-MiniLM-L6-v2` (sentence-transformers) |
| Vector DB | ChromaDB (HNSW, persistent) |
| Reranker | `ms-marco-MiniLM-L-6-v2` (cross-encoder) |
| LLM | Ollama `llama3.2:3b` (local, free) |
| Backend | FastAPI + SSE streaming |
| Frontend | Vanilla JS + D3.js visualization |

## ⚡ Latency Budget
- Query embed + HNSW search: ~50ms
- Cross-encoder rerank: ~150ms  
- Ollama generation (streaming): ~1.5–3.5s
- **Total: 2–4 seconds** ✅

## 🎯 Features
- ✅ Upload PDFs via drag-and-drop UI
- ✅ Background ingestion with live progress
- ✅ Native text extraction + OCR for scanned pages
- ✅ 700-word chunks with 80-word overlap
- ✅ HNSW vector index (ChromaDB)
- ✅ Cross-encoder reranking for precision
- ✅ Streaming answers token-by-token
- ✅ Citations: `[filename.pdf, p.X]` on every answer
- ✅ D3.js retrieval visualization (scored chunks)
- ✅ Latency breakdown per query (embed/search/rerank/llm)
- ✅ Document library with status tracking

## 🔧 Config (.env)
```env
OLLAMA_MODEL=llama3.2:3b      # change to any installed model
CHUNK_SIZE_WORDS=500
CHUNK_OVERLAP_WORDS=80
TOP_K_RETRIEVE=8
TOP_K_RERANK=5
```
