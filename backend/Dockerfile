FROM python:3.12-slim

WORKDIR /app

# Install the backend package and its runtime dependencies (fastapi,
# uvicorn[standard], chromadb, pypdf, cryptography, google-genai, numpy).
COPY pyproject.toml README.md ./
COPY app ./app
RUN pip install --no-cache-dir .

# Bake in the already-ingested vector store. The raw corpus PDFs are
# gitignored (see docs/corpus/SOURCES.md) and .chroma/ is built locally via
# `python -m app.rag.ingest`; copying the built index here avoids needing a
# persistent volume or re-downloading/re-ingesting the corpus at deploy time.
COPY .chroma ./.chroma

# Warm the local sentence-embedding model cache (all-MiniLM-L6-v2, ONNX) at
# build time instead of on the first production request.
RUN python -c "from app.rag.chroma_client import default_embedding_function; default_embedding_function()"

ENV CHROMA_PERSIST_DIR=/app/.chroma

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]