# RAG Scholar: Interview Preparation Guide

This document contains a comprehensive list of technical interview questions and answers tailored specifically to the RAG (Retrieval-Augmented Generation) Chatbot project you built for Navgurukul. 

Use this guide to understand *why* certain architectural decisions were made, so you can confidently explain your code to interviewers.

---

## 1. Architecture & System Design

### Q: Walk me through the architecture of your RAG application.
**A:** "The system is divided into an ingestion pipeline and a retrieval pipeline. 
1. **Ingestion:** When a user uploads a PDF, the backend extracts the text (using PyMuPDF or Tesseract OCR for scanned pages). The text is split into overlapping chunks of 500 words. Each chunk is converted into a vector embedding using the `all-MiniLM-L6-v2` model and stored in a local ChromaDB database along with metadata (filename, page number).
2. **Retrieval & Chat:** When a user asks a question, the query is embedded using the same model. We perform a cosine similarity search in ChromaDB to find the top 8 most relevant chunks. Because vector search can sometimes miss semantic nuances, those 8 chunks are passed through a Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) which re-scores and re-ranks them, selecting the absolute best 5. These top 5 chunks are injected into a prompt alongside the user's query and sent to the LLM (Groq/Gemini), which streams the answer back to the frontend using Server-Sent Events (SSE)."

### Q: Why did you choose a decoupled approach (FastAPI backend + Vanilla JS frontend) instead of a framework like Streamlit?
**A:** "Streamlit is great for quick prototypes, but it lacks fine-grained control over the UI and asynchronous performance. By decoupling the system, I could use FastAPI’s native async capabilities (`async def`) to handle slow LLM generation without blocking the server. It also allowed me to build a highly custom frontend, including the D3.js visualization for retrieval scores and true Server-Sent Event streaming, which is difficult to optimize in Streamlit."

### Q: How does the system handle a user uploading a massive 1000-page PDF while trying to chat?
**A:** "The FastAPI backend uses `BackgroundTasks`. When a document is uploaded, the heavy processing (text extraction, chunking, embedding) is immediately pushed to a background worker. The API instantly returns a 'Job Created' response to the frontend. The frontend then polls the job status. This means the main thread is never blocked, allowing the user to continue chatting or navigating the app while the heavy lifting happens asynchronously."

---

## 2. Retrieval-Augmented Generation (RAG) Specifics

### Q: Why did you use Chunking? What happens if your chunk size is too large or too small?
**A:** "Chunking is required because embedding models have maximum sequence limits (usually 512 tokens), and LLMs have context window limits. 
*   **Too large:** We lose granularity. The embedding becomes a 'mush' of too many topics, making it hard to match specific queries. It also eats up the LLM's context window quickly.
*   **Too small:** We lose surrounding context. A chunk might just contain a pronoun without the noun it refers to, making the text useless to the LLM."

### Q: I see you used a 'Sliding Window' chunking strategy with an 80-word overlap. Why?
**A:** "If you split text abruptly, you might cut a crucial sentence or paragraph exactly in half. By overlapping chunks by 80 words, I ensure that if an important concept crosses the boundary between two chunks, the full context is safely preserved in both of them."

### Q: You implemented a Cross-Encoder for 'Reranking'. Why wasn't the initial vector search enough?
**A:** "Standard vector search uses a Bi-encoder. It embeds the query and the document separately and calculates the cosine distance. It's incredibly fast but isn't perfect at understanding deep semantic relationships. A Cross-Encoder evaluates the query and the document *together* as a single input, which is highly accurate but computationally expensive. By doing a fast vector search to get the top 8, and then using the Cross-Encoder to rerank those 8 to find the top 5, I get the best of both worlds: high speed and maximum accuracy."

---

## 3. AI & Machine Learning Models

### Q: Why did you choose `all-MiniLM-L6-v2` for embeddings instead of OpenAI's embeddings?
**A:** "The goal was to build a robust, open-source pipeline. `all-MiniLM-L6-v2` is a lightweight sentence-transformer model that runs extremely efficiently on a CPU. It's completely free, doesn't require API calls, and most importantly, it guarantees data privacy because the raw document text never leaves the local machine during the embedding phase."

### Q: How did you force the LLM to output accurate citations and page numbers?
**A:** "This was achieved through strict Prompt Engineering. During the retrieval phase, the metadata (filename, page start, page end) is preserved. When constructing the context window for the LLM, I inject the metadata directly above each chunk like this: `[Source: file.pdf, p.15]`. I then explicitly instruct the LLM in the `SYSTEM_PROMPT` that it *must* cite every factual claim using that exact format, and that it must not hallucinate information outside of those blocks."

---

## 4. Backend & Database

### Q: Why did you use ChromaDB over a database like pgvector or Pinecone?
**A:** "Pinecone is a cloud service, which introduces latency and costs. `pgvector` requires setting up a PostgreSQL server. ChromaDB was the perfect fit because it is an open-source vector database that runs embedded directly inside the Python process. It uses the HNSW (Hierarchical Navigable Small World) algorithm, making similarity searches extremely fast, while keeping the deployment architecture simple and fully local."

### Q: What is Server-Sent Events (SSE) and why did you use it for the chat endpoint?
**A:** "LLMs generate text one token at a time. If I used a standard REST API response, the user would have to stare at a loading spinner for several seconds until the entire response was finished. SSE is a one-way web socket alternative that allows the FastAPI server to push individual tokens to the frontend as soon as they are generated. This drastically lowers the 'Time to First Token' (TTFT) and makes the app feel instantly responsive."

---

## 5. Error Handling & Edge Cases

### Q: What happens if the LLM provider (like Groq) rate-limits your application?
**A:** "I implemented resilient error handling with exponential backoff and auto-failover. If the Groq API returns an HTTP `429 Too Many Requests` error, the system catches it, waits briefly (1s, then 2s, then 4s), and retries. Furthermore, the `config.py` allows configuring multiple providers (Groq, Gemini, NVIDIA). If Groq completely fails, the system is designed to automatically seamlessly failover to the next available provider."

### Q: How do you handle old, scanned PDFs where the text cannot be highlighted?
**A:** "The ingestion pipeline is fault-tolerant. It first attempts native text extraction using `PyMuPDF`. If the extracted text is suspiciously short (indicating a scanned image), the pipeline automatically falls back to an OCR (Optical Character Recognition) approach using `pytesseract`. It converts the PDF pages into images and extracts the text visually, ensuring no document is left unreadable."

### Q: How would you scale this system if we had 10,000 users?
**A:** "To scale this, I would:
1. Move from the embedded SQLite ChromaDB to a client-server vector database setup (like Milvus or Qdrant).
2. Move the `BackgroundTasks` ingestion pipeline to a dedicated message queue worker system like Celery + Redis, so document processing doesn't compete for CPU resources with the web server.
3. Add a caching layer (like Redis) to store the embeddings of frequently asked questions to bypass the LLM entirely."
