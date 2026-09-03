from flask import Blueprint, request, jsonify, current_app
from app.retriever import RAGRetriever
from app.cache import ResponseCache
from app import limiter
import json

api_bp = Blueprint('api', __name__)

# Global retriever instance
retriever = None


def get_retriever():
    """Lazy load retriever."""
    global retriever
    if retriever is None:
        retriever = RAGRetriever()
    return retriever


@api_bp.route('/health', methods=['GET'])
@limiter.limit("10/minute")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "research-assistant-rag"
    }), 200


@api_bp.route('/query', methods=['POST'])
@limiter.limit("30/minute")
def query():
    """Main query endpoint for RAG."""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                "error": "Missing 'question' field"
            }), 400
        
        question = data.get('question', '').strip()
        user_id = data.get('user_id', 'default')
        conversation_history = data.get('conversation_history', [])
        
        if not question:
            return jsonify({
                "error": "Question cannot be empty"
            }), 400
        
        # Initialize cache
        cache = ResponseCache(current_app.redis_client)
        
        # Check cache
        cached_response = cache.get(question, user_id)
        if cached_response:
            cached_response['from_cache'] = True
            return jsonify(cached_response), 200
        
        # Get retriever
        rag = get_retriever()
        
        # Retrieve relevant documents
        docs = rag.retrieve(question, top_k=5)
        
        # Generate answer
        answer = rag.generate_answer(question, docs, conversation_history)
        
        # Prepare response
        response = {
            "question": question,
            "answer": answer,
            "sources": [
                {
                    "content": doc.page_content[:200],
                    "metadata": doc.metadata if hasattr(doc, 'metadata') else {}
                }
                for doc in docs
            ],
            "from_cache": False
        }
        
        # Cache the response
        cache.set(question, response, user_id)
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@api_bp.route('/add-document', methods=['POST'])
@limiter.limit("20/minute")
def add_document():
    """Add a user document to the knowledge base."""
    try:
        data = request.get_json()
        
        if not data or 'document' not in data:
            return jsonify({
                "error": "Missing 'document' field"
            }), 400
        
        document = data.get('document', '').strip()
        metadata = data.get('metadata', {})
        user_id = data.get('user_id', 'default')
        
        if not document:
            return jsonify({
                "error": "Document cannot be empty"
            }), 400
        
        # Add user metadata
        metadata['user_id'] = user_id
        
        # Get retriever and add document
        rag = get_retriever()
        rag.add_user_document(document, metadata)
        
        return jsonify({
            "message": "Document added successfully",
            "user_id": user_id
        }), 201
    
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
