from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pytest

from app.rag import chroma_client
from app.rag.config import get_rag_settings


class _FakeEmbeddingFunction:
    """Deterministic, offline embedding stub so unit tests never hit the network."""

    def __call__(self, input: Sequence[str]) -> list[list[float]]:
        return [[float(len(text)), float(text.count(" ") + 1)] for text in input]


@pytest.fixture(autouse=True)
def _isolated_rag_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Point Chroma at a temporary directory and reset process-wide caches."""
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / ".chroma"))
    monkeypatch.setenv("CHROMA_COLLECTION_NAME", "test_corpus")
    get_rag_settings.cache_clear()
    chroma_client.get_chroma_client.cache_clear()
    yield
    get_rag_settings.cache_clear()
    chroma_client.get_chroma_client.cache_clear()


def test_get_chroma_client_persists_to_configured_directory(tmp_path: Path) -> None:
    client = chroma_client.get_chroma_client()

    assert client is chroma_client.get_chroma_client()  # cached: single shared instance
    assert (tmp_path / ".chroma").exists()


def test_get_or_create_corpus_collection_uses_configured_name() -> None:
    collection = chroma_client.get_or_create_corpus_collection(
        embedding_function=_FakeEmbeddingFunction(),
    )

    assert collection.name == "test_corpus"
    assert collection.count() == 0


def test_collection_round_trips_documents() -> None:
    collection = chroma_client.get_or_create_corpus_collection(
        embedding_function=_FakeEmbeddingFunction(),
    )

    collection.add(
        ids=["doc-1"],
        documents=["Indice de productivite d'un puits conventionnel."],
        metadatas=[{"source": "spe-manual", "page": 12}],
    )

    result = collection.query(query_texts=["indice de productivite"], n_results=1)

    assert result["ids"][0] == ["doc-1"]
    assert result["metadatas"][0][0]["source"] == "spe-manual"


def test_get_or_create_corpus_collection_reuses_shared_client() -> None:
    client = chroma_client.get_chroma_client()
    collection = chroma_client.get_or_create_corpus_collection(
        client=client,
        embedding_function=_FakeEmbeddingFunction(),
    )

    assert collection.name == "test_corpus"
