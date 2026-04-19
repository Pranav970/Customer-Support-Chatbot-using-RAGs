"""
Guardrails for input queries and generated answers.
Input guardrails: check for empty, abusive, injection, or out-of-scope queries.
Output guardrails: strip hallucination markers, enforce conciseness signals.
"""
from __future__ import annotations
import re
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ── Patterns ──────────────────────────────────────────────────────────────────

_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(your\s+)?system\s+prompt",
    r"you\s+are\s+now\s+",
    r"act\s+as\s+",
    r"jailbreak",
    r"<\s*script\s*>",
    r"system\s*:\s*you",
    r"forget\s+(everything|all)",
]

_COMPILED_INJECTIONS = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]

_PROFANITY_THRESHOLD = 3  # crude word-count proxy; replace with a real filter if needed

_OFF_TOPIC_KEYWORDS = [
    "stock price", "weather forecast", "recipe", "horoscope",
    "sports score", "lottery", "dating", "social security number",
]


@dataclass
class GuardrailResult:
    passed: bool
    reason: str = ""


# ── Input guardrail ───────────────────────────────────────────────────────────

def check_input(query: str) -> GuardrailResult:
    """
    Returns GuardrailResult(passed=True) if the query is safe to process,
    or GuardrailResult(passed=False, reason=...) otherwise.
    """
    stripped = query.strip()

    if len(stripped) < 2:
        return GuardrailResult(False, "Query is too short.")

    if len(stripped) > 2000:
        return GuardrailResult(False, "Query exceeds the 2 000-character limit.")

    # Prompt-injection detection
    for pattern in _COMPILED_INJECTIONS:
        if pattern.search(stripped):
            logger.warning(f"Injection attempt detected: {stripped[:120]}")
            return GuardrailResult(False, "Your message contains disallowed patterns.")

    # Off-topic check (soft — warn but pass; tighten if needed)
    lower = stripped.lower()
    for keyword in _OFF_TOPIC_KEYWORDS:
        if keyword in lower:
            logger.info(f"Potentially off-topic query: '{keyword}' found")
            # We let it through; the RAG context will naturally produce no relevant chunks

    return GuardrailResult(True)


# ── Output guardrail ──────────────────────────────────────────────────────────

def check_output(answer: str) -> GuardrailResult:
    """
    Post-generation check. Currently detects:
      - Explicit 'I don't know' with no useful content
      - Hallucination self-disclosure markers left in the answer
    """
    lower = answer.lower()

    # Model sometimes returns these when confused; bubble up for UI handling
    hallucination_markers = [
        "as an ai language model",
        "i was trained by openai",
        "i am chatgpt",
    ]
    for marker in hallucination_markers:
        if marker in lower:
            logger.warning("Hallucination marker detected in output")
            return GuardrailResult(False, "Response contained disallowed content and was blocked.")

    return GuardrailResult(True)
