import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def _path_from_env(name: str, default: str) -> str:
    path = Path(os.environ.get(name, default))
    return str(path if path.is_absolute() else BASE_DIR / path)

class Config:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
    EMBEDDING_MODEL = os.environ.get(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    FAISS_INDEX_PATH = _path_from_env("FAISS_INDEX_PATH", "indexes/faiss_core")
    CHROMA_PERSIST_DIR = _path_from_env("CHROMA_PERSIST_DIR", "indexes/chroma_dynamic")
    CHROMA_COLLECTION = os.environ.get("CHROMA_COLLECTION", "user_docs")
    MAX_HISTORY_TURNS = int(os.environ.get("MAX_HISTORY_TURNS", 4))