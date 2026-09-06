FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	FAISS_INDEX_PATH=/app/indexes/faiss_core \
	CHROMA_PERSIST_DIR=/app/data/chroma_dynamic

WORKDIR /app

COPY --from=builder /install /usr/local
COPY app ./app
COPY run.py requirements.txt ./
# The generated index is a build artifact; raw PDFs are never needed at runtime.
COPY indexes ./indexes

RUN useradd --create-home --uid 10001 appuser \
	&& mkdir -p /app/data \
	&& chown -R appuser:appuser /app

USER appuser

# One gthread worker keeps memory bounded; two threads provide limited I/O concurrency
# without duplicating the embedding model across multiple processes on the free tier.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:?PORT must be set} --workers 1 --threads 2 --worker-class gthread --timeout 120 run:app"]
