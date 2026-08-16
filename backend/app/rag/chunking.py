"""Split raw document text into overlapping chunks suitable for embedding.

Chunking on word boundaries (rather than raw character slicing) avoids cutting
a term in half, which would otherwise degrade embedding quality for technical
vocabulary (e.g. splitting "perméabilité" across two chunks).
"""

from __future__ import annotations


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Split `text` into chunks of at most `chunk_size` characters.

    Consecutive chunks share roughly `chunk_overlap` characters of trailing
    context, so a passage that would otherwise fall on a chunk boundary is
    still retrievable in full from at least one chunk.

    Args:
        text: Source text to split. Whitespace is normalized (words are
            re-joined with single spaces).
        chunk_size: Maximum number of characters per chunk.
        chunk_overlap: Number of characters of overlap between consecutive
            chunks. Must be smaller than `chunk_size`.

    Returns:
        The list of chunks, in order. Empty if `text` has no words.

    Raises:
        ValueError: If `chunk_size` isn't positive, or `chunk_overlap` isn't
            in `[0, chunk_size)`.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive number of characters.")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be >= 0 and strictly smaller than chunk_size.")

    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(words):
        current, end = _fill_chunk(words, start, chunk_size)
        chunks.append(" ".join(current))
        if end >= len(words):
            break
        start = _next_start(words, start, end, chunk_overlap)
    return chunks


def _fill_chunk(words: list[str], start: int, chunk_size: int) -> tuple[list[str], int]:
    """Greedily collect words from `start` while staying within `chunk_size`."""
    current: list[str] = []
    length = 0
    end = start
    while end < len(words):
        word = words[end]
        extra = len(word) + (1 if current else 0)
        if current and length + extra > chunk_size:
            break
        current.append(word)
        length += extra
        end += 1
    return current, end


def _next_start(words: list[str], start: int, end: int, chunk_overlap: int) -> int:
    """Find the index to resume from, keeping ~chunk_overlap trailing characters."""
    overlap_len = 0
    back = end
    while back > start:
        word = words[back - 1]
        extra = len(word) + (1 if overlap_len else 0)
        if overlap_len + extra > chunk_overlap:
            break
        overlap_len += extra
        back -= 1
    # Guarantee forward progress even if overlap logic would otherwise stall.
    return back if back > start else end
