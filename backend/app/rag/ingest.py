"""Corpus ingestion: load raw documents, chunk them, and index them into Chroma.

Usage (from `backend/`, once Azra has dropped source files into
`docs/corpus/raw/`):

    python -m app.rag.ingest
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from pypdf import PdfReader

from app.rag.chroma_client import get_or_create_corpus_collection
from app.rag.chunking import chunk_text
from app.rag.config import get_rag_settings

if TYPE_CHECKING:
    from chromadb.api.models.Collection import Collection

_TEXT_SUFFIXES = {".txt", ".md"}
_PDF_SUFFIXES = {".pdf"}


@dataclass(frozen=True, slots=True)
class RawDocument:
    """A single source document loaded from disk, before chunking."""

    source_name: str
    text: str


@dataclass(frozen=True, slots=True)
class IngestResult:
    """Summary of an ingestion run."""

    documents_loaded: int
    chunks_indexed: int
    skipped_files: tuple[str, ...]


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _read_pdf_file(path: Path) -> str:
    reader = PdfReader(str(path))
    pages_text = (page.extract_text() or "" for page in reader.pages)
    return "\n".join(pages_text)


def load_raw_documents(raw_dir: Path) -> tuple[list[RawDocument], list[str]]:
    """Load every supported document directly under `raw_dir`.

    Args:
        raw_dir: Directory to scan (non-recursive). Missing directory yields
            no documents rather than raising, so a fresh clone without a
            corpus yet doesn't break the pipeline.

    Returns:
        A tuple `(documents, skipped_files)`: loaded documents, and the names
        of files skipped either because their extension isn't supported yet
        or because no text could be extracted from them.
    """
    documents: list[RawDocument] = []
    skipped: list[str] = []
    if not raw_dir.exists():
        return documents, skipped

    for path in sorted(raw_dir.iterdir()):
        if not path.is_file() or path.name.startswith("."):
            continue
        suffix = path.suffix.lower()
        if suffix in _TEXT_SUFFIXES:
            text = _read_text_file(path)
        elif suffix in _PDF_SUFFIXES:
            text = _read_pdf_file(path)
        else:
            skipped.append(path.name)
            continue

        if text.strip():
            documents.append(RawDocument(source_name=path.name, text=text))
        else:
            skipped.append(path.name)
    return documents, skipped


def _default_raw_dir() -> Path:
    # This file lives at backend/app/rag/ingest.py -> repo root is 3 levels up.
    return Path(__file__).resolve().parents[3] / "docs" / "corpus" / "raw"


def ingest_corpus(
    raw_dir: Path | None = None,
    collection: Collection | None = None,
) -> IngestResult:
    """Chunk every document under `raw_dir` and index the chunks into Chroma.

    Re-running this function is safe: chunk IDs are deterministic
    (`"{filename}::chunk-{index}"`), so indexing the same corpus twice
    upserts rather than duplicates.

    Args:
        raw_dir: Directory containing the raw corpus. Defaults to
            `docs/corpus/raw` relative to the repository root.
        collection: Chroma collection to index into. Defaults to the shared
            corpus collection. Overridable for tests.

    Returns:
        A summary of how many documents were loaded and chunks indexed.
    """
    settings = get_rag_settings()
    effective_raw_dir = raw_dir if raw_dir is not None else _default_raw_dir()
    active_collection = (
        collection if collection is not None else get_or_create_corpus_collection()
    )

    documents, skipped = load_raw_documents(effective_raw_dir)

    chunk_ids: list[str] = []
    chunk_texts: list[str] = []
    chunk_metadatas: list[dict[str, str | int]] = []
    for document in documents:
        pieces = chunk_text(document.text, settings.chunk_size, settings.chunk_overlap)
        for index, piece in enumerate(pieces):
            chunk_ids.append(f"{document.source_name}::chunk-{index}")
            chunk_texts.append(piece)
            chunk_metadatas.append({"source": document.source_name, "chunk_index": index})

    if chunk_ids:
        active_collection.upsert(ids=chunk_ids, documents=chunk_texts, metadatas=chunk_metadatas)  # type: ignore[arg-type]

    return IngestResult(
        documents_loaded=len(documents),
        chunks_indexed=len(chunk_ids),
        skipped_files=tuple(skipped),
    )


def _main() -> None:
    result = ingest_corpus()
    print(f"Documents chargés : {result.documents_loaded}")
    print(f"Chunks indexés    : {result.chunks_indexed}")
    if result.skipped_files:
        print(f"Fichiers ignorés  : {', '.join(result.skipped_files)}")
    if result.documents_loaded == 0:
        print(
            "Aucun document trouvé dans docs/corpus/raw/. "
            "Voir docs/corpus/SOURCES.md pour la collecte du corpus."
        )


if __name__ == "__main__":
    _main()
