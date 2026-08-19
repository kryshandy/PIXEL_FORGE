from __future__ import annotations

from collections.abc import Iterator, Sequence
from pathlib import Path

import pytest

from app.rag import chroma_client, retrieve
from app.rag.config import get_rag_settings


class _FakeEmbeddingFunction:
    """Deterministic, offline embedding stub so unit tests never hit the network."""

    def __call__(self, input: Sequence[str]) -> list[list[float]]:
        return [[float(len(text)), float(text.count(" ") + 1)] for text in input]


@pytest.fixture(autouse=True)
def _isolated_rag_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / ".chroma"))
    monkeypatch.setenv("CHROMA_COLLECTION_NAME", "test_corpus")
    monkeypatch.setenv("RAG_TOP_K", "3")
    get_rag_settings.cache_clear()
    chroma_client.get_chroma_client.cache_clear()
    yield
    get_rag_settings.cache_clear()
    chroma_client.get_chroma_client.cache_clear()


@pytest.fixture
def fake_collection() -> object:
    return chroma_client.get_or_create_corpus_collection(
        embedding_function=_FakeEmbeddingFunction(),
    )


def _seed(collection: object, count: int) -> None:
    collection.upsert(  # type: ignore[attr-defined]
        ids=[f"doc.txt::chunk-{i}" for i in range(count)],
        documents=[f"contenu du chunk numero {i} sur le reservoir" for i in range(count)],
        metadatas=[{"source": "doc.txt", "chunk_index": i} for i in range(count)],
    )


def test_retrieve_returns_empty_list_on_empty_collection(fake_collection: object) -> None:
    results = retrieve.retrieve("indice de productivite", collection=fake_collection)  # type: ignore[arg-type]

    assert results == []


def test_retrieve_returns_chunks_with_source_metadata(fake_collection: object) -> None:
    _seed(fake_collection, count=5)

    results = retrieve.retrieve("reservoir conventionnel", collection=fake_collection)  # type: ignore[arg-type]

    assert len(results) == 3  # RAG_TOP_K=3 from the isolated settings fixture
    assert all(isinstance(chunk, retrieve.RetrievedChunk) for chunk in results)
    assert all(chunk.source == "doc.txt" for chunk in results)
    assert all(chunk.chunk_index >= 0 for chunk in results)


def test_retrieve_respects_explicit_top_k(fake_collection: object) -> None:
    _seed(fake_collection, count=5)

    results = retrieve.retrieve("reservoir", top_k=2, collection=fake_collection)  # type: ignore[arg-type]

    assert len(results) == 2


def test_retrieve_caps_top_k_at_collection_size(fake_collection: object) -> None:
    _seed(fake_collection, count=2)

    results = retrieve.retrieve("reservoir", top_k=10, collection=fake_collection)  # type: ignore[arg-type]

    assert len(results) == 2


def test_retrieve_orders_results_by_ascending_distance(fake_collection: object) -> None:
    _seed(fake_collection, count=5)

    results = retrieve.retrieve("reservoir", collection=fake_collection)  # type: ignore[arg-type]

    distances = [chunk.distance for chunk in results]
    assert distances == sorted(distances)


def test_main_exits_without_query_argument(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["retrieve.py"])

    with pytest.raises(SystemExit):
        retrieve._main()


def test_main_prints_no_results_message_on_empty_collection(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    fake_collection: object,
) -> None:
    monkeypatch.setattr("sys.argv", ["retrieve.py", "reservoir"])
    monkeypatch.setattr(
        "app.rag.retrieve.get_or_create_corpus_collection",
        lambda: fake_collection,
    )

    retrieve._main()

    captured = capsys.readouterr()
    assert "Aucun resultat" in captured.out


def test_main_prints_results_with_source_and_distance(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    fake_collection: object,
) -> None:
    _seed(fake_collection, count=3)
    monkeypatch.setattr("sys.argv", ["retrieve.py", "reservoir", "conventionnel"])
    monkeypatch.setattr(
        "app.rag.retrieve.get_or_create_corpus_collection",
        lambda: fake_collection,
    )

    retrieve._main()

    captured = capsys.readouterr()
    assert "doc.txt" in captured.out
    assert "Resultat 1" in captured.out