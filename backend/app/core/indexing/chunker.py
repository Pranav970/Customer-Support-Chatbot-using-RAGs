"""
Intelligent chunker: splits text on sentence/paragraph boundaries,
respects chunk_size and overlap, preserves context windows.
"""
from __future__ import annotations
import re
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    text: str
    chunk_index: int
    page: int
    source_type: str
    char_start: int
    char_end: int


def _split_sentences(text: str) -> list[str]:
    """Lightweight sentence splitter (no NLTK dependency required)."""
    # Split on sentence-ending punctuation followed by whitespace / EOL
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p for p in parts if p.strip()]


def _split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]


def chunk_pages(
    pages: list[dict],
    chunk_size: int = 512,
    chunk_overlap: int = 64,
) -> list[Chunk]:
    """
    Given a list of page-dicts from the parser, return a flat list of Chunk objects.
    Strategy:
      1. Split each page into paragraphs.
      2. Accumulate paragraphs until chunk_size is reached.
      3. When a paragraph itself exceeds chunk_size, split it into sentences.
      4. Apply overlap by re-including tail tokens from the previous chunk.
    """
    chunks: list[Chunk] = []
    chunk_index = 0

    for page_dict in pages:
        text = page_dict.get("text", "").strip()
        page_num = page_dict.get("page", 1)
        source_type = page_dict.get("source_type", "unknown")

        if not text:
            continue

        paragraphs = _split_paragraphs(text)
        buffer = ""
        buffer_start = 0
        offset = 0  # character offset within page text

        for para in paragraphs:
            # If a single paragraph is huge, break into sentences first
            units = [para] if len(para) <= chunk_size else _split_sentences(para)

            for unit in units:
                if not unit.strip():
                    continue

                candidate = (buffer + " " + unit).strip() if buffer else unit

                if len(candidate) <= chunk_size:
                    buffer = candidate
                else:
                    # Flush current buffer
                    if buffer:
                        char_end = offset + len(buffer)
                        chunks.append(
                            Chunk(
                                text=buffer,
                                chunk_index=chunk_index,
                                page=page_num,
                                source_type=source_type,
                                char_start=buffer_start,
                                char_end=char_end,
                            )
                        )
                        chunk_index += 1

                        # Overlap: keep the last `chunk_overlap` chars
                        overlap_text = buffer[-chunk_overlap:] if chunk_overlap else ""
                        buffer = (overlap_text + " " + unit).strip()
                        buffer_start = char_end - len(overlap_text)
                    else:
                        buffer = unit
                        buffer_start = offset

                offset += len(unit) + 1  # +1 for space/newline

        # Flush remaining buffer
        if buffer:
            chunks.append(
                Chunk(
                    text=buffer,
                    chunk_index=chunk_index,
                    page=page_num,
                    source_type=source_type,
                    char_start=buffer_start,
                    char_end=buffer_start + len(buffer),
                )
            )
            chunk_index += 1

    logger.debug(f"Produced {len(chunks)} chunks from {len(pages)} pages")
    return chunks
