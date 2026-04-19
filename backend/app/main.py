from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.routes import chat, documents
from app.dependencies import get_vector_store
from app.models.schemas import HealthResponse

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = get_settings()
    logger.info(f"Starting {cfg.app_name}")
    os.makedirs(cfg.upload_dir, exist_ok=True)
    os.makedirs(cfg.chroma_persist_dir, exist_ok=True)
    store = get_vector_store()
    logger.info(f"Vector store ready — {store.count()} chunks indexed")
    yield
    logger.info("Shutting down")


# ── App ───────────────────────────────────────────────────────────────────────

cfg = get_settings()
app = FastAPI(
    title=cfg.app_name,
    version="1.0.0",
    description="Production-grade RAG customer support chatbot powered by Claude Sonnet.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────

app.include_router(chat.router,      prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health():
    store = get_vector_store()
    return HealthResponse(
        status="ok",
        collection_count=store.count(),
        embedding_model=cfg.embedding_model,
        generation_model=cfg.claude_model,
    )


@app.get("/", tags=["root"])
async def root():
    return {"message": f"{cfg.app_name} is running. Visit /docs for the API reference."}
