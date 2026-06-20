"""
Routes: PDF upload and ingestion job tracking.
POST /api/ingest        → upload PDF, start background ingestion
GET  /api/jobs/{job_id} → poll job progress
GET  /api/documents     → list all ingested documents
DELETE /api/documents/{doc_id} → remove document
"""
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, Depends
from sqlalchemy.orm import Session

from config import settings
from db.database import get_db
from db.models import Document, IngestJob
from ingestion.pipeline import run_ingestion
from retrieval.vector_store import delete_document, collection_stats

router = APIRouter(prefix="/api")


@router.post("/ingest")
async def ingest_pdf(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported.")

    doc_id = str(uuid.uuid4())
    safe_name = Path(file.filename).name
    dest = Path(settings.UPLOAD_PATH) / f"{doc_id}_{safe_name}"

    # Save upload
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    file_size = dest.stat().st_size

    # Create DB records
    doc = Document(
        id=doc_id, filename=safe_name,
        filepath=str(dest), file_size=file_size, status="ingesting"
    )
    job = IngestJob(id=str(uuid.uuid4()), document_id=doc_id, status="running")
    db.add(doc); db.add(job); db.commit()
    job_id = job.id

    # Callbacks to update DB
    def on_progress(pct: float, step: str):
        s = SessionLocal_local()
        try:
            j = s.get(IngestJob, job_id)
            if j:
                j.progress = pct; j.current_step = step
                s.commit()
        finally:
            s.close()

    def on_done(total_pages: int, total_chunks: int):
        s = SessionLocal_local()
        try:
            d = s.get(Document, doc_id)
            j = s.get(IngestJob, job_id)
            if d:
                d.total_pages = total_pages
                d.total_chunks = total_chunks
                d.status = "done"
            if j:
                j.status = "done"; j.progress = 1.0
            s.commit()
        finally:
            s.close()

    def on_error(msg: str):
        s = SessionLocal_local()
        try:
            d = s.get(Document, doc_id)
            j = s.get(IngestJob, job_id)
            if d:
                d.status = "error"; d.error_msg = msg
            if j:
                j.status = "error"; j.current_step = msg
            s.commit()
        finally:
            s.close()

    background_tasks.add_task(
        run_ingestion, doc_id, safe_name, str(dest),
        on_progress, on_done, on_error,
    )

    return {"doc_id": doc_id, "job_id": job_id, "filename": safe_name}


@router.get("/jobs/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.get(IngestJob, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return {
        "job_id": job.id,
        "document_id": job.document_id,
        "status": job.status,
        "progress": job.progress,
        "current_step": job.current_step,
    }


@router.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    stats = collection_stats()
    return {
        "documents": [
            {
                "id": d.id,
                "filename": d.filename,
                "status": d.status,
                "total_pages": d.total_pages,
                "total_chunks": d.total_chunks,
                "file_size": d.file_size,
                "error_msg": d.error_msg,
            }
            for d in docs
        ],
        "total_chunks": stats["total_chunks"],
    }


@router.delete("/documents/{doc_id}")
def delete_doc(doc_id: str, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    delete_document(doc_id)
    db.delete(doc)
    db.commit()
    return {"deleted": doc_id}


# Local session for background callbacks (no request context)
from db.database import SessionLocal as SessionLocal_local  # noqa: E402
