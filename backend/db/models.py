from sqlalchemy import Column, String, Integer, DateTime, Float, Text
from sqlalchemy.sql import func
from db.database import Base
import uuid

class Document(Base):
    __tablename__ = "documents"
    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename    = Column(String, nullable=False)
    filepath    = Column(String, nullable=False)
    total_pages = Column(Integer, default=0)
    total_chunks= Column(Integer, default=0)
    file_size   = Column(Integer, default=0)
    status      = Column(String, default="pending")  # pending/ingesting/done/error
    error_msg   = Column(Text, nullable=True)
    created_at  = Column(DateTime, server_default=func.now())

class IngestJob(Base):
    __tablename__ = "ingest_jobs"
    id           = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id  = Column(String, nullable=False)
    status       = Column(String, default="queued")  # queued/running/done/error
    progress     = Column(Float, default=0.0)
    current_step = Column(String, default="")
    created_at   = Column(DateTime, server_default=func.now())
    updated_at   = Column(DateTime, onupdate=func.now())
