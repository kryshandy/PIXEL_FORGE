"""Semantic retrieval over the indexed technical corpus.

Given a natural-language query, embeds it with the same embedding function
used at ingestion time and returns the most relevant chunks from Chroma,
together with their source document, so an answer can be traced back to a
document.

Usage (from `backend/`, after `python -m app.rag.ingest` has indexed a
corpus):

    python -m app.rag.retrieve "indice de productivite reservoir conventionnel"
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.rag.chroma_client import get_or_create_corpus_collection
from app.rag.config import get_rag_settings

if TYPE_CHECKING:
    from chromadb.api.models.Collection import Collection


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    """A single chunk returned by a retrieval query, with its provenance."""

    text: str
    source: str
    chunk_index: int
    distance: float


def retrieve(
    query: str,
    top_k: int | None = None,
    collection: Collection | None = None,
) -> list[RetrievedChunk]:
    """Return the `top_k` chunks most relevant to `query`.

    Args:
        query: Natural-language search query.
        top_k: Number of chunks to return. Defaults to `RagSettings.top_k`.
        collection: Chroma collection to query. Defaults to the shared
            corpus collection. Overridable for tests.

    Returns:
        Chunks ordered from most to least relevant (ascending distance).
        Empty list if the collection has no indexed chunks yet.
    """
    settings = get_rag_settings()
    active_collection = (
        collection if collection is not None else get_or_create_corpus_collection()
    )
    effective_top_k = top_k if top_k is not None else settings.top_k

    if active_collection.count() == 0:
        return []

    result = active_collection.query(
        query_texts=[query],
        n_results=min(effective_top_k, active_collection.count()),
    )

    documents = result.get("documents") or [[]]
    metadatas = result.get("metadatas") or [[]]
    distances = result.get("distances") or [[]]

    chunks: list[RetrievedChunk] = []
    for text, metadata, distance in zip(
        documents[0], metadatas[0], distances[0], strict=True
    ):
        source = str(metadata.get("source", "unknown"))
        chunk_index = int(metadata.get("chunk_index", -1))
        chunks.append(
            RetrievedChunk(
                text=text,
                source=source,
                chunk_index=chunk_index,
                distance=float(distance),
            )
        )
    return chunks


def _main() -> None:
    if len(sys.argv) < 2:
        print('Usage : python -m app.rag.retrieve "votre requete"')
        raise SystemExit(1)

    query = " ".join(sys.argv[1:])
    chunks = retrieve(query)

    if not chunks:
        print("Aucun resultat. Le corpus est-il indexe ? (python -m app.rag.ingest)")
        return

    for rank, chunk in enumerate(chunks, start=1):
        print(f"--- Resultat {rank} (source: {chunk.source}, distance: {chunk.distance:.4f}) ---")
        print(chunk.text[:300].strip())
        print()


if __name__ == "__main__":
    _main()