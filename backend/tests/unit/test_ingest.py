from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.rag import chroma_client, ingest
from app.rag.config import get_rag_settings


class _FakeEmbeddingFunction:
    """Deterministic, offline embedding stub so unit tests never hit the network."""

    def __call__(self, input: Sequence[str]) -> list[list[float]]:
        return [[float(len(text)), float(text.count(" ") + 1)] for text in input]


@pytest.fixture(autouse=True)
def _isolated_rag_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / ".chroma"))
    monkeypatch.setenv("CHROMA_COLLECTION_NAME", "test_corpus")
    monkeypatch.setenv("RAG_CHUNK_SIZE", "80")
    monkeypatch.setenv("RAG_CHUNK_OVERLAP", "20")
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


def test_load_raw_documents_reads_txt_and_md(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "01_note.txt").write_text("Indice de productivite.", encoding="utf-8")
    (raw_dir / "02_note.md").write_text("# Titre\n\nPression de fracturation.", encoding="utf-8")

    documents, skipped = ingest.load_raw_documents(raw_dir)

    assert {doc.source_name for doc in documents} == {"01_note.txt", "02_note.md"}
    assert skipped == []


def test_load_raw_documents_skips_unsupported_extensions(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "notes.txt").write_text("Contenu valide.", encoding="utf-8")
    (raw_dir / "image.png").write_bytes(b"\x89PNG\r\n")

    documents, skipped = ingest.load_raw_documents(raw_dir)

    assert [doc.source_name for doc in documents] == ["notes.txt"]
    assert skipped == ["image.png"]


def test_load_raw_documents_skips_empty_files(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "empty.txt").write_text("   \n  ", encoding="utf-8")

    documents, skipped = ingest.load_raw_documents(raw_dir)

    assert documents == []
    assert skipped == ["empty.txt"]


def test_load_raw_documents_ignores_hidden_files(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / ".gitkeep").write_text("", encoding="utf-8")
    (raw_dir / "notes.txt").write_text("Contenu valide.", encoding="utf-8")

    documents, skipped = ingest.load_raw_documents(raw_dir)

    assert [doc.source_name for doc in documents] == ["notes.txt"]
    assert skipped == []


def test_default_raw_dir_points_at_docs_corpus_raw() -> None:
    default_dir = ingest._default_raw_dir()

    assert default_dir.parts[-3:] == ("docs", "corpus", "raw")


def test_load_raw_documents_missing_directory_returns_empty(tmp_path: Path) -> None:
    documents, skipped = ingest.load_raw_documents(tmp_path / "does-not-exist")

    assert documents == []
    assert skipped == []


def test_load_raw_documents_extracts_pdf_text_via_pypdf(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    pdf_path = raw_dir / "manual.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake content for extraction test")

    fake_page = MagicMock()
    fake_page.extract_text.return_value = "Pression de fond et indice de productivite."
    fake_reader = MagicMock()
    fake_reader.pages = [fake_page]

    with patch("app.rag.ingest.PdfReader", return_value=fake_reader) as mock_reader:
        documents, skipped = ingest.load_raw_documents(raw_dir)

    mock_reader.assert_called_once_with(str(pdf_path))
    assert len(documents) == 1
    assert documents[0].source_name == "manual.pdf"
    assert "indice de productivite" in documents[0].text
    assert skipped == []


def test_ingest_corpus_indexes_all_chunks(tmp_path: Path, fake_collection: object) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    long_text = " ".join(f"terme{i}" for i in range(60))
    (raw_dir / "doc1.txt").write_text(long_text, encoding="utf-8")
    (raw_dir / "doc2.md").write_text("Petit document.", encoding="utf-8")

    result = ingest.ingest_corpus(raw_dir=raw_dir, collection=fake_collection)  # type: ignore[arg-type]

    assert result.documents_loaded == 2
    assert result.chunks_indexed > 0
    assert fake_collection.count() == result.chunks_indexed  # type: ignore[attr-defined]


def test_ingest_corpus_is_idempotent_on_rerun(tmp_path: Path, fake_collection: object) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "doc.txt").write_text("Contenu stable du corpus.", encoding="utf-8")

    first = ingest.ingest_corpus(raw_dir=raw_dir, collection=fake_collection)  # type: ignore[arg-type]
    second = ingest.ingest_corpus(raw_dir=raw_dir, collection=fake_collection)  # type: ignore[arg-type]

    assert first.chunks_indexed == second.chunks_indexed
    assert fake_collection.count() == first.chunks_indexed  # type: ignore[attr-defined]


def test_ingest_corpus_reports_skipped_files(tmp_path: Path, fake_collection: object) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "doc.txt").write_text("Contenu valide.", encoding="utf-8")
    (raw_dir / "archive.zip").write_bytes(b"PK\x03\x04")

    result = ingest.ingest_corpus(raw_dir=raw_dir, collection=fake_collection)  # type: ignore[arg-type]

    assert result.skipped_files == ("archive.zip",)


def test_ingest_corpus_handles_empty_raw_dir(tmp_path: Path, fake_collection: object) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()

    result = ingest.ingest_corpus(raw_dir=raw_dir, collection=fake_collection)  # type: ignore[arg-type]

    assert result.documents_loaded == 0
    assert result.chunks_indexed == 0
