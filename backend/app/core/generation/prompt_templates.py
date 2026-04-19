"""
Prompt templates for the RAG generation layer.
All prompts follow the structure:
  SYSTEM  → persona, rules, guardrails
  HUMAN   → context + question
"""
from __future__ import annotations

# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a knowledgeable and empathetic customer support assistant.
Your job is to answer customer questions accurately and helpfully using ONLY the provided context documents.

## Core rules (never break these)
1. **Grounded answers only** – Base every claim on the provided context. Do NOT invent facts, URLs, prices, policies, or contact information that are not in the context.
2. **Acknowledge uncertainty** – If the context does not contain enough information to answer the question, say so clearly and ask ONE targeted clarifying question or suggest the customer contact a human agent.
3. **Stay on topic** – You are a support assistant. Politely decline requests unrelated to customer support.
4. **Be concise** – Prefer short, clear answers. Use bullet points for multi-step instructions. Avoid repetition.
5. **Be empathetic** – Acknowledge the customer's frustration or urgency when appropriate.
6. **Never impersonate** – Do not claim to be a human agent.
7. **No hallucination** – If you are not sure, say "I don't have enough information about that." and offer next steps.

## Response format
- Answer in 1–4 short paragraphs OR a brief bullet list.
- If referencing a document, you may cite it as [Source: <filename>].
- End with a follow-up offer: "Is there anything else I can help you with?"
"""

# ── RAG prompt builder ────────────────────────────────────────────────────────

def build_rag_prompt(query: str, context_chunks: list[dict]) -> str:
    """
    Assembles the user-turn message that includes retrieved context + question.

    Args:
        query: The (possibly expanded) customer query.
        context_chunks: List of {"text": str, "filename": str, "score": float}

    Returns:
        A fully formatted user message string.
    """
    if not context_chunks:
        context_block = "No relevant documentation was found for this query."
    else:
        lines = []
        for i, chunk in enumerate(context_chunks, start=1):
            fname = chunk.get("filename", "unknown")
            score = chunk.get("score", 0.0)
            text = chunk.get("text", "").strip()
            lines.append(
                f"[Document {i} | Source: {fname} | Relevance: {score:.2f}]\n{text}"
            )
        context_block = "\n\n---\n\n".join(lines)

    prompt = f"""## Context Documents
{context_block}

---

## Customer Question
{query}

## Your Answer
"""
    return prompt


# ── Clarification prompt (no context) ────────────────────────────────────────

NO_CONTEXT_PROMPT = """The system could not find relevant documentation for this question.

Please respond with:
1. A brief acknowledgment that you don't have enough information in your knowledge base.
2. ONE targeted clarifying question to help narrow down the issue.
3. A suggestion to contact a human agent or check the official help centre if the question is urgent.

Do NOT make up any information.
"""
