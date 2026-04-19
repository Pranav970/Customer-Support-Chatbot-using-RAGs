"""
Generation layer: build RAG prompt → call Claude Sonnet 4.6 → return answer + sources.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import anthropic

from app.core.generation.prompt_templates import (
    SYSTEM_PROMPT,
    NO_CONTEXT_PROMPT,
    build_rag_prompt,
)
from app.core.retrieval.retriever import RetrievedChunk
from app.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class GenerationResult:
    answer: str
    sources: list[dict]
    query_used: str
    had_context: bool


class Generator:
    def __init__(self):
        cfg = get_settings()
        self._client = anthropic.Anthropic(api_key=cfg.anthropic_api_key)
        self._model = cfg.claude_model
        self._max_tokens = cfg.max_tokens
        self._temperature = cfg.temperature
        logger.info(f"Generator initialised with model: {self._model}")

    def generate(
        self,
        query: str,
        chunks: list[RetrievedChunk],
        query_used: str,
    ) -> GenerationResult:
        """
        Build a RAG prompt, call Claude, return a GenerationResult.
        FIX: temperature is passed as top-level kwarg (valid in anthropic SDK >= 0.20)
        """
        had_context = len(chunks) > 0

        context_for_prompt = [
            {"text": c.text, "filename": c.filename, "score": c.score}
            for c in chunks
        ]

        if had_context:
            user_message = build_rag_prompt(query, context_for_prompt)
        else:
            user_message = f"{NO_CONTEXT_PROMPT}\n\nCustomer question: {query}"

        logger.debug(f"Sending prompt to {self._model} (context chunks: {len(chunks)})")

        # FIX: anthropic SDK messages.create() accepts temperature as a direct
        # parameter. Confirmed valid for SDK >= 0.20 and Claude 3+ models.
        response = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            temperature=self._temperature,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        answer = response.content[0].text.strip()

        sources: list[dict] = []
        seen_ids: set[str] = set()
        for chunk in chunks:
            if chunk.chunk_id not in seen_ids:
                seen_ids.add(chunk.chunk_id)
                sources.append(
                    {
                        "doc_id": chunk.doc_id,
                        "filename": chunk.filename,
                        "chunk_index": chunk.chunk_index,
                        "score": chunk.score,
                        "preview": chunk.text[:200] + ("…" if len(chunk.text) > 200 else ""),
                    }
                )

        logger.info(f"Generated answer ({len(answer)} chars) from {len(chunks)} chunks")
        return GenerationResult(
            answer=answer,
            sources=sources,
            query_used=query_used,
            had_context=had_context,
        )
