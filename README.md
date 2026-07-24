# Research Assistant RAG

A Retrieval-Augmented Generation research assistant built with Flask, LangChain,
FAISS, ChromaDB, and the OpenAI API — designed with token-cost efficiency in mind.

## Features
- Hybrid vector storage: FAISS for a large static reference corpus, ChromaDB for
  dynamic per-user documents with metadata filtering
- Cost-aware prompt construction (static-prefix-first for prompt caching, capped
  context length, capped output tokens)
- Redis-backed response cache to skip redundant LLM calls
- Session-aware conversation history with a configurable turn limit

## Architecture
Client → Flask API (auth, sessions, rate limiting) → LangChain orchestrator
(retriever router + prompt builder) → FAISS / ChromaDB → OpenAI API → Redis
response cache.

## Setup

\`\`\`bash
git clone https://github.com/<your-username>/research-assistant-rag.git
cd research-assistant-rag
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # then fill in OPENAI_API_KEY
\`\`\`

## Build the static index
Place source PDFs in `data/raw/core_corpus/`, then:

\`\`\`bash
python scripts/build_faiss_index.py
\`\`\`

## Run

\`\`\`bash
# local
python run.py

# or via Docker
docker compose up --build
\`\`\`

## API

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/query` | POST | `{"question": "..."}` → answer + sources |

## Roadmap
- [x] Ingestion pipeline
- [x] Retrieval + orchestration
- [x] Flask API + caching
- [ ] CI/CD via GitHub Actions
- [ ] Reranking / hybrid dense+sparse retrieval
- [ ] Evaluation harness

## License
MIT