"""
Retriever: embed query → vector search → return ranked chunks.
Optional query expansion rewrites the query for better recall.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from app.core.indexing.embedder import get_embedder
from app.core.vectorstore.chromadb_store import VectorStore
from app.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    doc_id: str
    filename: str
    chunk_index: int
    page: int
    source_type: str
    score: float        # cosine similarity (higher = more relevant)
    uploaded_at: str


def expand_query(original_query: str) -> str:
    """
    Lightweight rule-based query expansion.
    Appends common support synonyms to widen retrieval.
    """
    expansions = {
        "refund": "refund return money back charge",
        "cancel": "cancel cancellation terminate subscription",
        "password": "password reset login credentials access",
        "shipping": "shipping delivery tracking order status",
        "error": "error issue problem bug failure",
        "account": "account profile settings user",
        "payment": "payment billing invoice charge card",
        "contact": "contact support help agent phone email",
    }
    lower = original_query.lower()
    extras: list[str] = []
    for keyword, synonyms in expansions.items():
        if keyword in lower:
            extras.append(synonyms)

    if extras:
        expanded = original_query + " " + " ".join(extras)
        logger.debug(f"Query expanded: '{original_query}' → '{expanded[:120]}'")
        return expanded

    return original_query


class Retriever:
    def __init__(self, vector_store: VectorStore):
        self._store = vector_store
        cfg = get_settings()
        self._embedder = get_embedder(cfg.embedding_model)
        self._top_k = cfg.retrieval_top_k
        self._threshold = cfg.retrieval_score_threshold

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        expand: bool = True,
    ) -> tuple[list[RetrievedChunk], str]:
        """
        Returns (chunks, query_used).
        FIX: Handles empty vector store gracefully — returns empty list
        instead of crashing when no documents are indexed.
        """
        k = top_k or self._top_k
        query_used = expand_query(query) if expand else query

        # FIX: Short-circuit if the collection is empty — avoids ChromaDB
        # ValueError: "n_results > number of elements in index"
        if self._store.count() == 0:
            logger.info("Vector store is empty — skipping retrieval")
            return [], query_used

        embedding = self._embedder.embed_one(query_used)
        results = self._store.query(query_embedding=embedding, top_k=k)

        chunks: list[RetrievedChunk] = []
        ids = results.get("ids", [[]])[0]
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for chunk_id, text, meta, dist in zip(ids, docs, metas, distances):
            # ChromaDB cosine distance: 0 = identical, 2 = opposite
            # Convert to similarity score in [0, 1]
            similarity = 1.0 - (dist / 2.0)
            if similarity < self._threshold:
                continue

            chunks.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    text=text,
                    doc_id=meta.get("doc_id", ""),
                    filename=meta.get("filename", ""),
                    chunk_index=int(meta.get("chunk_index", 0)),
                    page=int(meta.get("page", 1)),
                    source_type=meta.get("source_type", ""),
                    score=round(similarity, 4),
                    uploaded_at=meta.get("uploaded_at", ""),
                )
            )

        logger.info(f"Retrieved {len(chunks)} chunks (threshold={self._threshold})")
        return chunks, query_used
