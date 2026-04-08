from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import ChatRequest, ChatResponse, SourceDoc
from app.core.retrieval.guardrails import check_input, check_output
from app.core.retrieval.retriever import Retriever
from app.core.generation.generator import Generator
from app.dependencies import get_retriever, get_generator
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    retriever: Retriever = Depends(get_retriever),
    generator: Generator = Depends(get_generator),
):
    """
    Main RAG chat endpoint.
    Flow: guardrail → retrieve → generate → output guardrail → respond
    """
    # 1. Input guardrail
    guard = check_input(request.query)
    if not guard.passed:
        return ChatResponse(
            answer=f"Your message could not be processed: {guard.reason}",
            sources=[],
            query_used=request.query,
            session_id=request.session_id,
            flagged=True,
            flag_reason=guard.reason,
        )

    # 2. Retrieve relevant chunks
    try:
        chunks, query_used = retriever.retrieve(
            query=request.query,
            expand=request.expand_query,
        )
    except Exception as exc:
        logger.error(f"Retrieval error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Retrieval service error.")

    # 3. Generate answer
    try:
        result = generator.generate(
            query=request.query,
            chunks=chunks,
            query_used=query_used,
        )
    except Exception as exc:
        logger.error(f"Generation error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Generation service error.")

    # 4. Output guardrail
    out_guard = check_output(result.answer)
    if not out_guard.passed:
        return ChatResponse(
            answer="I'm sorry, I wasn't able to generate a safe response. Please rephrase your question or contact a human agent.",
            sources=[],
            query_used=query_used,
            session_id=request.session_id,
            flagged=True,
            flag_reason=out_guard.reason,
        )

    # 5. Build response
    sources = [
        SourceDoc(
            doc_id=s["doc_id"],
            filename=s["filename"],
            chunk_index=s["chunk_index"],
            score=s["score"],
            preview=s["preview"],
        )
        for s in result.sources
    ]

    return ChatResponse(
        answer=result.answer,
        sources=sources,
        query_used=query_used,
        session_id=request.session_id,
        flagged=False,
    )
