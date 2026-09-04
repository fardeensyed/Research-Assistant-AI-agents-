# Research Assistant RAG

A Retrieval-Augmented Generation research assistant built with Flask, LangChain,
FAISS, ChromaDB, Groq, and local Hugging Face embeddings.

## Features
- Hybrid vector storage: FAISS for a large static reference corpus, ChromaDB for
  dynamic per-user documents with metadata filtering
- Cost-aware prompt construction (static-prefix-first for prompt caching, capped
  context length, capped output tokens)
- Redis-backed response cache to skip redundant LLM calls
- Session-aware conversation history with a configurable turn limit

## Architecture
Client → Flask API (auth, sessions, rate limiting) → LangChain orchestrator
(retriever router + prompt builder) → FAISS / ChromaDB → Groq API → Redis
response cache.

## Setup

\`\`\`bash
git clone https://github.com/<your-username>/research-assistant-rag.git
cd research-assistant-rag
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env     # Windows; then fill in GROQ_API_KEY
# macOS/Linux: cp .env.example .env
\`\`\`

## Build the static index
Place source PDFs in `data/raw/core_corpus/`, then:

\`\`\`bash
python scripts/build_faiss_index.py
\`\`\`

The index uses the local `sentence-transformers/all-MiniLM-L6-v2` embedding
model. Groq is used only for answer generation, so no OpenAI API key is needed.

## Run

\`\`\`bash
# local
python run.py

# or via Docker
docker compose up --build
\`\`\`

The Docker image expects the generated `indexes/faiss_core` directory in the
build context. It copies that pre-built FAISS index into the image and does not
need the raw PDF corpus at runtime. Docker starts Gunicorn with one `gthread`
worker and two threads to keep memory bounded on small instances.

Set `GROQ_API_KEY` in the runtime environment or in a local `.env` file; it is
never copied into the image. Redis is optional: the cache degrades gracefully
and `/health` reports Redis as `degraded` when it is unreachable.

## API

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Component-level readiness check |
| `/query` | POST | `{"question": "..."}` → answer + sources |
| `/add-document` | POST | Add text to the dynamic document store |

## Local prerequisites

- Python 3.11+
- A Groq API key from [console.groq.com](https://console.groq.com/)
- Redis running locally for response caching (the app still starts if Redis is unavailable)

## Roadmap
- [x] Ingestion pipeline
- [x] Retrieval + orchestration
- [x] Flask API + caching
- [ ] CI/CD via GitHub Actions
- [ ] Reranking / hybrid dense+sparse retrieval
- [ ] Evaluation harness

## License
MIT