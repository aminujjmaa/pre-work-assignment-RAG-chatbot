from pydantic_settings import BaseSettings
from pathlib import Path
import os

class Settings(BaseSettings):
    CHROMA_PATH: str = str(Path(__file__).parent.parent / "chroma_db")
    UPLOAD_PATH: str = str(Path(__file__).parent.parent / "uploads")
    DB_PATH: str = str(Path(__file__).parent.parent / "rag.db")
    STATIC_PATH: str = str(Path(__file__).parent / "static")

    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # LLM Provider: "groq", "nvidia", "gemini", or "auto" (tries in order)
    LLM_PROVIDER: str = "auto"

    # Groq Cloud — https://console.groq.com (free: 30 RPM)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # NVIDIA NIM — https://build.nvidia.com (free: 1000 credits/month)
    NVIDIA_API_KEY: str = ""
    NVIDIA_MODEL: str = "meta/llama-3.1-70b-instruct"

    # Google Gemini Flash — https://aistudio.google.com (free: 15 RPM)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Ollama (fallback)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"

    CHUNK_SIZE_WORDS: int = 500
    CHUNK_OVERLAP_WORDS: int = 80
    TOP_K_RETRIEVE: int = 8
    TOP_K_RERANK: int = 5

    class Config:
        env_file = str(Path(__file__).parent / ".env")

settings = Settings()

# Ensure dirs exist
for d in [settings.CHROMA_PATH, settings.UPLOAD_PATH]:
    os.makedirs(d, exist_ok=True)
