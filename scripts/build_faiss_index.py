"""Build FAISS index from PDF corpus."""
import os
import sys
from pathlib import Path

# Make the sibling app package importable when this file is run directly.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import Config

# PDF source directory
PDF_SOURCE_DIR = PROJECT_ROOT / "data" / "raw" / "core_corpus"
INDEX_OUTPUT_PATH = Config.FAISS_INDEX_PATH


def load_pdfs(directory: str):
    """Load all PDFs from directory."""
    documents = []
    pdf_dir = Path(directory)
    
    if not pdf_dir.exists():
        print(f"PDF directory not found: {directory}")
        return documents
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files")
    
    for pdf_file in pdf_files:
        try:
            print(f"Loading {pdf_file.name}...")
            loader = PyPDFLoader(str(pdf_file))
            docs = loader.load()
            documents.extend(docs)
            print(f"  ✓ Loaded {len(docs)} pages")
        except Exception as e:
            print(f"  ✗ Error loading {pdf_file.name}: {e}")
    
    return documents


def build_index():
    """Build and save FAISS index."""
    print("Building FAISS Index...")
    print("-" * 50)
    
    # Load PDFs
    documents = load_pdfs(PDF_SOURCE_DIR)
    
    if not documents:
        print("No documents found. Please add PDF files to data/raw/core_corpus/")
        return
    
    print(f"\nTotal documents: {len(documents)}")
    
    # Split documents
    print("\nSplitting documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Total chunks: {len(chunks)}")
    
    # Create embeddings
    print("\nCreating embeddings (this may take a while)...")
    embeddings = HuggingFaceEmbeddings(model_name=Config.EMBEDDING_MODEL)
    
    # Build FAISS index
    print("Building FAISS index...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    # Create output directory
    os.makedirs(os.path.dirname(INDEX_OUTPUT_PATH) or "indexes", exist_ok=True)
    
    # Save index
    vectorstore.save_local(INDEX_OUTPUT_PATH)
    print(f"\n✓ Index saved to {INDEX_OUTPUT_PATH}")
    print("-" * 50)
    print("FAISS index building complete!")


if __name__ == "__main__":
    build_index()
