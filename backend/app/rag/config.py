"""Environment-driven settings for the RAG (Retrieval-Augmented Generation) module."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

_DEFAULT_PERSIST_DIR = ".chroma"
_DEFAULT_COLLECTION_NAME = "petrosage_corpus"
_DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
_DEFAULT_CHUNK_SIZE = 800
_DEFAULT_CHUNK_OVERLAP = 120
_DEFAULT_TOP_K = 5


@dataclass(frozen=True, slots=True)
class RagSettings:
    """Runtime settings for the vector store, with safe local-development defaults.

    Attributes:
        persist_dir: Filesystem path where Chroma persists its local database.
        collection_name: Name of the Chroma collection holding the technical corpus.
        embedding_model: Sentence-embedding model used to vectorize chunks and
            queries. Defaults to a small, free, locally-run model so Day 1 setup
            has no external API dependency; can be swapped later if quality on
            the real corpus requires it.
        chunk_size: Target size (in characters) of each indexed document chunk.
        chunk_overlap: Overlap (in characters) between consecutive chunks, to
            avoid cutting a relevant passage in half.
        top_k: Default number of chunks retrieved per query.
    """

    persist_dir: str
    collection_name: str
    embedding_model: str
    chunk_size: int
    chunk_overlap: int
    top_k: int

    @classmethod
    def from_environment(cls) -> RagSettings:
        return cls(
            persist_dir=os.getenv("CHROMA_PERSIST_DIR", _DEFAULT_PERSIST_DIR),
            collection_name=os.getenv("CHROMA_COLLECTION_NAME", _DEFAULT_COLLECTION_NAME),
            embedding_model=os.getenv("EMBEDDING_MODEL", _DEFAULT_EMBEDDING_MODEL),
            chunk_size=int(os.getenv("RAG_CHUNK_SIZE", _DEFAULT_CHUNK_SIZE)),
            chunk_overlap=int(os.getenv("RAG_CHUNK_OVERLAP", _DEFAULT_CHUNK_OVERLAP)),
            top_k=int(os.getenv("RAG_TOP_K", _DEFAULT_TOP_K)),
        )


@lru_cache
def get_rag_settings() -> RagSettings:
    """Load RAG settings once per process."""
    return RagSettings.from_environment()
