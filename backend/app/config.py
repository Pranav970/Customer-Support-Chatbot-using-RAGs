from __future__ import annotations
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str = ""

    # App
    app_name: str = "Customer Support RAG Chatbot"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # ChromaDB
    chroma_persist_dir: str = "./data/chromadb"
    chroma_collection_name: str = "support_docs"

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"

    # Retrieval
    retrieval_top_k: int = 5
    retrieval_score_threshold: float = 0.3

    # Generation
    claude_model: str = "claude-sonnet-4-6"
    max_tokens: int = 1024
    temperature: float = 0.2

    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 64

    # Upload
    upload_dir: str = "./data/uploads"
    max_file_size_mb: int = 50

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
