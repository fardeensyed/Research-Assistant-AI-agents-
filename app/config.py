import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.environ["GROQ_API_KEY"]
    GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
    EMBEDDING_MODEL = os.environ.get(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-key")
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    FAISS_INDEX_PATH = os.environ.get("FAISS_INDEX_PATH", "indexes/faiss_core")
    CHROMA_PERSIST_DIR = os.environ.get("CHROMA_PERSIST_DIR", "indexes/chroma_dynamic")
    CHROMA_COLLECTION = os.environ.get("CHROMA_COLLECTION", "user_docs")
    MAX_HISTORY_TURNS = int(os.environ.get("MAX_HISTORY_TURNS", 4))