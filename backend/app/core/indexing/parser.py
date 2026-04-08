"""
Document parser: PDF, DOCX, TXT, MD, images.
Each parser returns a list of {"text": str, "page": int} dicts.
"""
from __future__ import annotations
import io
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _safe_import(module: str):
    import importlib
    try:
        return importlib.import_module(module)
    except ImportError:
        return None


# ── Per-type parsers ─────────────────────────────────────────────────────────

def parse_txt(file_bytes: bytes, filename: str) -> list[dict]:
    text = file_bytes.decode("utf-8", errors="replace")
    return [{"text": text, "page": 1, "source_type": "txt"}]


def parse_md(file_bytes: bytes, filename: str) -> list[dict]:
    text = file_bytes.decode("utf-8", errors="replace")
    return [{"text": text, "page": 1, "source_type": "markdown"}]


def parse_pdf(file_bytes: bytes, filename: str) -> list[dict]:
    pypdf2 = _safe_import("PyPDF2")
    if pypdf2 is None:
        logger.warning("PyPDF2 not installed; falling back to raw text")
        return parse_txt(file_bytes, filename)

    pages = []
    try:
        reader = pypdf2.PdfReader(io.BytesIO(file_bytes))
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append({"text": text, "page": i, "source_type": "pdf"})
    except Exception as exc:
        logger.error(f"PDF parse error for {filename}: {exc}")
    return pages


def parse_docx(file_bytes: bytes, filename: str) -> list[dict]:
    docx = _safe_import("docx")
    if docx is None:
        logger.warning("python-docx not installed")
        return []

    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        text = "\n\n".join(paragraphs)
        return [{"text": text, "page": 1, "source_type": "docx"}]
    except Exception as exc:
        logger.error(f"DOCX parse error for {filename}: {exc}")
        return []


def parse_image(file_bytes: bytes, filename: str, caption_fn=None) -> list[dict]:
    """
    If a caption_fn is supplied (callable that takes bytes → str), use it.
    Otherwise emit a placeholder so the image is at least indexed.
    """
    if caption_fn:
        try:
            caption = caption_fn(file_bytes)
        except Exception as exc:
            logger.error(f"Image captioning failed for {filename}: {exc}")
            caption = f"[Image: {filename}]"
    else:
        caption = f"[Image: {filename} — no captioning model configured]"

    return [{"text": caption, "page": 1, "source_type": "image"}]


# ── Dispatcher ────────────────────────────────────────────────────────────────

EXTENSION_MAP = {
    ".pdf": parse_pdf,
    ".docx": parse_docx,
    ".doc": parse_docx,
    ".txt": parse_txt,
    ".md": parse_md,
    ".markdown": parse_md,
    ".png": parse_image,
    ".jpg": parse_image,
    ".jpeg": parse_image,
    ".webp": parse_image,
    ".gif": parse_image,
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def parse_document(
    file_bytes: bytes,
    filename: str,
    caption_fn=None,
) -> list[dict]:
    """
    Main entry point. Returns a list of page-dicts:
        [{"text": str, "page": int, "source_type": str}, ...]
    """
    ext = Path(filename).suffix.lower()
    parser = EXTENSION_MAP.get(ext)

    if parser is None:
        logger.warning(f"Unsupported file type: {ext} — treating as plain text")
        return parse_txt(file_bytes, filename)

    if ext in IMAGE_EXTENSIONS:
        return parser(file_bytes, filename, caption_fn)  # type: ignore[call-arg]

    return parser(file_bytes, filename)
