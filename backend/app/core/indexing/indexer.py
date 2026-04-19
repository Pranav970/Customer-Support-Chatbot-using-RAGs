"""
Indexing pipeline: parse → chunk → embed → store.
"""
from __future__ import annotations
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path

from app.core.indexing.parser import parse_document
from app.core.indexing.chunker import chunk_pages
from app.core.indexing.embedder import get_embedder
from app.core.vectorstore.chromadb_store import VectorStore
from app.config import get_settings

logger = logging.getLogger(__name__)


class IndexingPipeline:
    def __init__(self, vector_store: VectorStore):
        self._store = vector_store
        cfg = get_settings()
        self._embedder = get_embedder(cfg.embedding_model)
        self._chunk_size = cfg.chunk_size
        self._chunk_overlap = cfg.chunk_overlap

    def index_document(
        self,
        file_bytes: bytes,
        filename: str,
        doc_id: str | None = None,
    ) -> dict:
        """
        Full pipeline: parse → chunk → embed → upsert to vector store.
        Returns a summary dict with doc_id and chunk count.
        """
        doc_id = doc_id or str(uuid.uuid4())
        uploaded_at = datetime.now(timezone.utc).isoformat()

        logger.info(f"Indexing '{filename}' (doc_id={doc_id})")

        # 1. Parse
        pages = parse_document(file_bytes, filename)
        if not pages:
            raise ValueError(f"No parseable content found in '{filename}'")

        # 2. Chunk
        chunks = chunk_pages(pages, self._chunk_size, self._chunk_overlap)
        if not chunks:
            raise ValueError(f"No chunks produced for '{filename}'")

        # 3. Embed
        texts = [c.text for c in chunks]
        embeddings = self._embedder.embed(texts)

        # 4. Build IDs and metadata
        file_ext = Path(filename).suffix.lower().lstrip(".")
        ids, metas = [], []
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}__chunk_{i}"
            ids.append(chunk_id)
            metas.append(
                {
                    "doc_id": doc_id,
                    "filename": filename,
                    "file_type": file_ext,
                    "chunk_index": chunk.chunk_index,
                    "page": chunk.page,
                    "source_type": chunk.source_type,
                    "char_start": chunk.char_start,
                    "char_end": chunk.char_end,
                    "uploaded_at": uploaded_at,
                }
            )

        # 5. Upsert
        self._store.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metas,
        )

        logger.info(f"Indexed {len(chunks)} chunks for '{filename}'")
        return {
            "doc_id": doc_id,
            "filename": filename,
            "chunks_indexed": len(chunks),
            "uploaded_at": uploaded_at,
        }

    def delete_document(self, doc_id: str) -> None:
        self._store.delete_by_doc_id(doc_id)
        logger.info(f"Deleted document {doc_id}")
