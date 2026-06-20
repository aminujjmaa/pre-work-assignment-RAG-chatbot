"""
Ingestion pipeline: PDF → parse → chunk → embed → store in ChromaDB.
Runs as a FastAPI background task and updates job progress in SQLite.
"""
import asyncio
import time
from pathlib import Path
from typing import Callable

from ingestion.pdf_parser import extract_text_from_pdf
from ingestion.chunker import chunk_pages
from retrieval.embedder import embed_texts
from retrieval.vector_store import add_chunks
from config import settings


async def run_ingestion(
    doc_id: str,
    filename: str,
    filepath: str,
    on_progress: Callable[[float, str], None],
    on_done: Callable[[int, int], None],
    on_error: Callable[[str], None],
) -> None:
    """
    Full ingestion pipeline executed as background task.
    Calls progress/done/error callbacks to update DB.
    """
    try:
        # Step 1: Parse PDF
        on_progress(0.05, "Parsing PDF pages…")
        await asyncio.sleep(0)  # yield to event loop

        pages = await asyncio.get_event_loop().run_in_executor(
            None, extract_text_from_pdf, filepath
        )
        total_pages = len(pages)
        on_progress(0.25, f"Parsed {total_pages} pages")

        # Step 2: Chunk
        on_progress(0.30, "Chunking text…")
        chunks = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: chunk_pages(
                pages,
                chunk_size_words=settings.CHUNK_SIZE_WORDS,
                overlap_words=settings.CHUNK_OVERLAP_WORDS,
            ),
        )
        total_chunks = len(chunks)
        on_progress(0.45, f"Created {total_chunks} chunks")

        # Step 3: Embed in batches
        on_progress(0.50, "Embedding chunks…")
        texts = [c["text"] for c in chunks]
        embeddings = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: embed_texts(texts, batch_size=64),
        )
        on_progress(0.80, "Embeddings computed")

        # Step 4: Store in ChromaDB
        on_progress(0.85, "Storing in vector DB…")
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: add_chunks(doc_id, filename, chunks, embeddings),
        )
        on_progress(1.0, "Done")
        on_done(total_pages, total_chunks)

    except Exception as exc:
        on_error(str(exc))
