from __future__ import annotations
import uuid
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from app.models.schemas import DocumentUploadResponse, DocumentListItem
from app.core.indexing.indexer import IndexingPipeline
from app.core.vectorstore.chromadb_store import VectorStore
from app.dependencies import get_vector_store, get_indexing_pipeline
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md", ".markdown",
                      ".png", ".jpg", ".jpeg", ".webp", ".gif"}


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    pipeline: IndexingPipeline = Depends(get_indexing_pipeline),
):
    """Ingest a document into the vector store."""
    cfg = get_settings()
    ext = Path(file.filename or "").suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    file_bytes = await file.read()
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > cfg.max_file_size_mb:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({size_mb:.1f} MB). Max: {cfg.max_file_size_mb} MB",
        )

    doc_id = str(uuid.uuid4())
    try:
        result = pipeline.index_document(
            file_bytes=file_bytes,
            filename=file.filename or f"{doc_id}{ext}",
            doc_id=doc_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.error(f"Indexing error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Indexing service error.")

    return DocumentUploadResponse(
        filename=file.filename or "",
        doc_id=result["doc_id"],
        chunks_indexed=result["chunks_indexed"],
        status="success",
        message=f"Indexed {result['chunks_indexed']} chunks successfully.",
    )


@router.get("", response_model=list[DocumentListItem])
async def list_documents(
    store: VectorStore = Depends(get_vector_store),
):
    """Return all indexed documents with metadata."""
    all_meta = store.get_all_docs_metadata()
    chunk_counts = store.get_chunk_counts_by_doc()

    docs = []
    for meta in all_meta:
        doc_id = meta.get("doc_id", "")
        docs.append(
            DocumentListItem(
                doc_id=doc_id,
                filename=meta.get("filename", ""),
                file_type=meta.get("file_type", ""),
                chunk_count=chunk_counts.get(doc_id, 0),
                uploaded_at=meta.get("uploaded_at", ""),
            )
        )
    return docs


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    pipeline: IndexingPipeline = Depends(get_indexing_pipeline),
):
    """Remove a document and all its chunks from the vector store."""
    try:
        pipeline.delete_document(doc_id)
    except Exception as exc:
        logger.error(f"Delete error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete document.")
    return JSONResponse({"status": "deleted", "doc_id": doc_id})
