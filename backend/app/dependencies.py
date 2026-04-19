"""
Shared FastAPI dependencies (singletons via module-level instances).
"""
from __future__ import annotations
from functools import lru_cache

from app.config import get_settings
from app.core.vectorstore.chromadb_store import VectorStore
from app.core.indexing.indexer import IndexingPipeline
from app.core.retrieval.retriever import Retriever
from app.core.generation.generator import Generator


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    cfg = get_settings()
    return VectorStore(
        persist_dir=cfg.chroma_persist_dir,
        collection_name=cfg.chroma_collection_name,
    )


@lru_cache(maxsize=1)
def get_indexing_pipeline() -> IndexingPipeline:
    return IndexingPipeline(vector_store=get_vector_store())


@lru_cache(maxsize=1)
def get_retriever() -> Retriever:
    return Retriever(vector_store=get_vector_store())


@lru_cache(maxsize=1)
def get_generator() -> Generator:
    return Generator()
