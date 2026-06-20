#!/usr/bin/env python3
"""
Bulk-ingest all PDFs from the uploads/ folder directly (no web UI needed).
Run after download_pdfs.py.
"""
import sys, os, asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
os.chdir(os.path.join(os.path.dirname(__file__), "backend"))

from pathlib import Path
from config import settings
from db.database import init_db, SessionLocal
from db.models import Document, IngestJob
from ingestion.pipeline import run_ingestion
import uuid

UPLOAD_DIR = Path(__file__).parent / "uploads"

def make_callbacks(doc_id, job_id, name):
    def on_progress(pct, step):
        bar = "█" * int(pct * 20) + "░" * (20 - int(pct * 20))
        print(f"\r  [{bar}] {int(pct*100):3d}%  {step[:40]:<40}", end="", flush=True)

    def on_done(pages, chunks):
        s = SessionLocal()
        try:
            d = s.get(Document, doc_id)
            j = s.get(IngestJob, job_id)
            if d: d.total_pages=pages; d.total_chunks=chunks; d.status="done"
            if j: j.status="done"; j.progress=1.0
            s.commit()
        finally: s.close()
        print(f"\r  ✅ {name}: {pages} pages, {chunks} chunks{' '*30}")

    def on_error(msg):
        s = SessionLocal()
        try:
            d = s.get(Document, doc_id)
            j = s.get(IngestJob, job_id)
            if d: d.status="error"; d.error_msg=msg
            if j: j.status="error"
            s.commit()
        finally: s.close()
        print(f"\r  ❌ {name}: {msg}")

    return on_progress, on_done, on_error


async def main():
    init_db()
    pdfs = sorted(UPLOAD_DIR.glob("*.pdf"))
    if not pdfs:
        print("No PDFs found in uploads/. Run download_pdfs.py first.")
        return

    print(f"Found {len(pdfs)} PDFs to ingest.\n")

    for pdf in pdfs:
        doc_id = str(uuid.uuid4())
        job_id = str(uuid.uuid4())
        name = pdf.name

        s = SessionLocal()
        # Skip if already ingested
        existing = s.query(Document).filter_by(filename=name, status="done").first()
        if existing:
            print(f"  ⏭  {name} already ingested, skipping.")
            s.close()
            continue

        doc = Document(id=doc_id, filename=name, filepath=str(pdf),
                       file_size=pdf.stat().st_size, status="ingesting")
        job = IngestJob(id=job_id, document_id=doc_id, status="running")
        s.add(doc); s.add(job); s.commit(); s.close()

        print(f"  ⏳ {name}")
        on_progress, on_done, on_error = make_callbacks(doc_id, job_id, name)
        await run_ingestion(doc_id, name, str(pdf), on_progress, on_done, on_error)

    print("\n✅ Bulk ingestion complete! Start the server with ./run.sh")

if __name__ == "__main__":
    asyncio.run(main())
