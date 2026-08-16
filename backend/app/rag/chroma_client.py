"""Chroma vector-store client and collection management.

Day 1 scope: provide a persistent local Chroma client and a helper to get or
create the corpus collection. Document ingestion (chunking the corpus and
indexing it) lands on Day 2 in `app.rag.ingest`.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection
from chromadb.api.types import Documents, EmbeddingFunction
from chromadb.utils import embedding_functions

from app.rag.config import get_rag_settings


@lru_cache
def get_chroma_client() -> ClientAPI:
    """Return a process-wide persistent Chroma client.

    The client stores its database on disk at ``RagSettings.persist_dir``, so
    the indexed corpus survives across backend restarts. Cached so the whole
    application shares a single client instance.
    """
    settings = get_rag_settings()
    return chromadb.PersistentClient(path=settings.persist_dir)


def default_embedding_function() -> EmbeddingFunction[Documents]:
    """Local, free sentence-embedding function (all-MiniLM-L6-v2 via ONNX).

    Chosen for Day 1 so the vector store works end-to-end with zero external
    API dependency. Can be swapped for a hosted embedding model later if
    retrieval quality on the real corpus requires it.
    """
    embedding_function = embedding_functions.DefaultEmbeddingFunction()
    if embedding_function is None:
        # chromadb returns None only in "thin client" mode (server-only install,
        # no local inference deps). PersistentClient always runs full-mode, so
        # this guards an environment misconfiguration rather than normal use.
        raise RuntimeError(
            "chromadb's DefaultEmbeddingFunction is unavailable in this "
            "environment. Reinstall chromadb (not chromadb-client) or pass an "
            "explicit embedding_function to get_or_create_corpus_collection()."
        )
    return embedding_function


def get_or_create_corpus_collection(
    client: ClientAPI | None = None,
    embedding_function: Any | None = None,
) -> Collection:
    """Get or create the Chroma collection used to store the technical corpus.

    Args:
        client: Chroma client to use. Defaults to the shared persistent client
            from :func:`get_chroma_client`.
        embedding_function: Embedding function used by the collection. Defaults
            to :func:`default_embedding_function`. Overridable so tests and
            offline runs never need network access.
    """
    settings = get_rag_settings()
    active_client = client if client is not None else get_chroma_client()
    active_embedding_function = (
        embedding_function if embedding_function is not None else default_embedding_function()
    )
    return active_client.get_or_create_collection(
        name=settings.collection_name,
        embedding_function=active_embedding_function,  # type: ignore[arg-type]
        metadata={"hnsw:space": "cosine"},
    )
