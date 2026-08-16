from __future__ import annotations

import pytest

from app.rag.chunking import chunk_text


def test_empty_text_returns_no_chunks() -> None:
    assert chunk_text("   ", chunk_size=100, chunk_overlap=10) == []


def test_short_text_fits_in_a_single_chunk() -> None:
    text = "Indice de productivite d'un puits conventionnel."
    chunks = chunk_text(text, chunk_size=200, chunk_overlap=20)

    assert chunks == [text]


def test_long_text_is_split_into_multiple_chunks_within_size_limit() -> None:
    text = " ".join(f"mot{i}" for i in range(200))  # long synthetic text

    chunks = chunk_text(text, chunk_size=50, chunk_overlap=10)

    assert len(chunks) > 1
    assert all(len(chunk) <= 50 for chunk in chunks)


def test_consecutive_chunks_overlap() -> None:
    text = " ".join(f"mot{i}" for i in range(50))

    chunks = chunk_text(text, chunk_size=40, chunk_overlap=15)

    first_words = set(chunks[0].split())
    second_words = set(chunks[1].split())
    assert first_words & second_words, "consecutive chunks should share some words"


def test_all_words_are_preserved_across_chunks() -> None:
    words = [f"terme{i}" for i in range(80)]
    text = " ".join(words)

    chunks = chunk_text(text, chunk_size=60, chunk_overlap=15)

    covered_words: set[str] = set()
    for chunk in chunks:
        covered_words.update(chunk.split())
    assert covered_words == set(words)


def test_progress_is_guaranteed_even_with_overlap_close_to_chunk_size() -> None:
    text = " ".join(f"w{i}" for i in range(100))

    chunks = chunk_text(text, chunk_size=20, chunk_overlap=19)

    # Must terminate (no infinite loop) and make forward progress.
    assert len(chunks) > 1


@pytest.mark.parametrize("chunk_size", [0, -10])
def test_non_positive_chunk_size_raises(chunk_size: int) -> None:
    with pytest.raises(ValueError, match="chunk_size"):
        chunk_text("some text", chunk_size=chunk_size, chunk_overlap=0)


@pytest.mark.parametrize("chunk_overlap", [-1, 100])
def test_invalid_chunk_overlap_raises(chunk_overlap: int) -> None:
    with pytest.raises(ValueError, match="chunk_overlap"):
        chunk_text("some text", chunk_size=100, chunk_overlap=chunk_overlap)
