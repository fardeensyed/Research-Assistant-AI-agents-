from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
import os
from app.config import Config


class RAGRetriever:
    """Hybrid retriever using FAISS + ChromaDB with LangChain orchestration."""
    
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=Config.EMBEDDING_MODEL)
        self.llm = ChatGroq(
            api_key=Config.GROQ_API_KEY,
            model=Config.GROQ_MODEL,
            temperature=0.7
        )
        self.faiss_store = None
        self.chroma_store = None
        
        self._load_vectorstores()
    
    def _load_vectorstores(self):
        """Load FAISS and ChromaDB stores."""
        # Load FAISS index if it exists
        if os.path.exists(Config.FAISS_INDEX_PATH):
            try:
                self.faiss_store = FAISS.load_local(
                    Config.FAISS_INDEX_PATH,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            except Exception as e:
                print(f"Warning: Could not load FAISS index: {e}")
        
        # Load ChromaDB collection if it exists
        if os.path.exists(Config.CHROMA_PERSIST_DIR):
            try:
                self.chroma_store = Chroma(
                    collection_name=Config.CHROMA_COLLECTION,
                    persist_directory=Config.CHROMA_PERSIST_DIR,
                    embedding_function=self.embeddings
                )
            except Exception as e:
                print(f"Warning: Could not load ChromaDB: {e}")
    
    def retrieve(self, question: str, top_k: int = 5):
        """Retrieve relevant documents for a question."""
        docs = []
        
        # Query FAISS if available
        if self.faiss_store:
            try:
                faiss_docs = self.faiss_store.similarity_search(question, k=top_k // 2)
                docs.extend(faiss_docs)
            except Exception as e:
                print(f"FAISS retrieval error: {e}")
        
        # Query ChromaDB if available
        if self.chroma_store:
            try:
                chroma_docs = self.chroma_store.similarity_search(question, k=top_k // 2)
                docs.extend(chroma_docs)
            except Exception as e:
                print(f"ChromaDB retrieval error: {e}")
        
        # Deduplicate by content
        unique_docs = []
        seen = set()
        for doc in docs:
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                unique_docs.append(doc)
        
        return unique_docs[:top_k]
    
    def generate_answer(self, question: str, context_docs: list, conversation_history: list = None):
        """Generate answer using LLM with retrieved context."""
        # Build context from documents
        context = "\n\n".join([doc.page_content for doc in context_docs])
        
        # Build conversation history string
        history_str = ""
        if conversation_history:
            for turn in conversation_history[-Config.MAX_HISTORY_TURNS:]:
                history_str += f"Q: {turn.get('question', '')}\nA: {turn.get('answer', '')}\n\n"
        
        # Prompt template with static prefix for token caching
        prompt_template = ChatPromptTemplate.from_template(
            """You are a research assistant. Answer questions based on the provided context.
Keep answers concise and cite sources when possible.

STATIC REFERENCE CONTEXT:
{context}

CONVERSATION HISTORY:
{history}

NEW QUESTION: {question}

Provide a clear, evidence-based answer."""
        )
        
        # Build the chain
        chain = (
            RunnablePassthrough.assign(
                context=lambda _: context,
                history=lambda _: history_str
            )
            | prompt_template
            | self.llm
        )
        
        # Generate response
        response = chain.invoke({"question": question})
        
        return response.content
    
    def add_user_document(self, document_text: str, metadata: dict = None):
        """Add a user document to ChromaDB."""
        if not self.chroma_store:
            self.chroma_store = Chroma(
                collection_name=Config.CHROMA_COLLECTION,
                persist_directory=Config.CHROMA_PERSIST_DIR,
                embedding_function=self.embeddings
            )
        
        if metadata is None:
            metadata = {}
        
        self.chroma_store.add_texts(
            texts=[document_text],
            metadatas=[metadata]
        )
