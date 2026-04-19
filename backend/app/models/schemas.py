from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="User question")
    session_id: Optional[str] = Field(None, description="Optional session identifier")
    expand_query: bool = Field(True, description="Whether to apply query expansion")


class SourceDoc(BaseModel):
    doc_id: str
    filename: str
    chunk_index: int
    score: float
    preview: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceDoc]
    query_used: str
    session_id: Optional[str] = None
    flagged: bool = False
    flag_reason: Optional[str] = None


class DocumentUploadResponse(BaseModel):
    filename: str
    doc_id: str
    chunks_indexed: int
    status: str
    message: str


class DocumentListItem(BaseModel):
    doc_id: str
    filename: str
    file_type: str
    chunk_count: int
    uploaded_at: str


class HealthResponse(BaseModel):
    status: str
    collection_count: int
    embedding_model: str
    generation_model: str
