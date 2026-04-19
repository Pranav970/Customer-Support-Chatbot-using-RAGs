from __future__ import annotations

import logging
from collections import Counter
from pathlib import Path
from typing import Optional

import chromadb
from chromadb import Settings as ChromaSettings

logger = logging.getLogger(__name__)


class VectorStore:
    """Persistent ChromaDB vector store wrapper."""

    def __init__(self, persist_dir: str, collection_name: str):
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        # FIX: import Settings from chromadb (not chromadb.config) for >=0.4
        # FIX: disable telemetry cleanly via Settings object
        self._client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection_name = collection_name
        self._collection = self._get_or_create_collection()
        logger.info(f"VectorStore ready: {collection_name} @ {persist_dir}")

    def _get_or_create_collection(self):
        return self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    # ── Write ────────────────────────────────────────────────────────────────

    def upsert(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        logger.debug(f"Upserted {len(ids)} chunks")

    def delete_by_doc_id(self, doc_id: str) -> None:
        results = self._collection.get(where={"doc_id": doc_id})
        if results["ids"]:
            self._collection.delete(ids=results["ids"])
            logger.info(f"Deleted {len(results['ids'])} chunks for doc {doc_id}")

    # ── Read ─────────────────────────────────────────────────────────────────

    def query(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        where: Optional[dict] = None,
    ) -> dict:
        """
        FIX: Guard against empty collection — ChromaDB raises ValueError when
        n_results > number of documents in the index.
        """
        current_count = self._collection.count()
        if current_count == 0:
            # Return empty-but-valid structure so callers don't crash
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

        # Cap n_results to what's actually available
        safe_k = min(top_k, current_count)

        kwargs: dict = dict(
            query_embeddings=[query_embedding],
            n_results=safe_k,
            include=["documents", "metadatas", "distances"],
        )
        if where:
            kwargs["where"] = where
        return self._collection.query(**kwargs)

    def get_all_docs_metadata(self) -> list[dict]:
        """Return deduplicated document-level metadata."""
        results = self._collection.get(include=["metadatas"])
        seen: set[str] = set()
        docs: list[dict] = []
        for meta in results.get("metadatas", []):
            doc_id = meta.get("doc_id", "")
            if doc_id not in seen:
                seen.add(doc_id)
                docs.append(meta)
        return docs

    def get_chunk_counts_by_doc(self) -> dict[str, int]:
        """Return {doc_id: chunk_count} for every stored chunk."""
        results = self._collection.get(include=["metadatas"])
        counts: Counter[str] = Counter()
        for meta in results.get("metadatas", []):
            counts[meta.get("doc_id", "")] += 1
        return dict(counts)

    def count(self) -> int:
        return self._collection.count()

    def collection_name(self) -> str:
        return self._collection_name
