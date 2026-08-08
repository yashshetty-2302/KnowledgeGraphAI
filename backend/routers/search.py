from fastapi import APIRouter, Depends, HTTPException
from schemas import QueryRequest, QueryResponse
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore
from services.llm_service import LLMService
from config import Config

router = APIRouter()

# Global instances to ensure consistency across requests
_embedding_service = None
_vector_store = None
_llm_service = None

def get_embedding_service():
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store

def get_llm_service():
    global _llm_service
    if _llm_service is None:
        try:
            _llm_service = LLMService()
        except ValueError as e:
            print(f"Warning: {str(e)}")
    return _llm_service

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query documents using RAG."""
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    llm = get_llm_service()
    if llm is None:
        raise HTTPException(status_code=500, detail="LLM service not configured. Please set GROQ_API_KEY")
    
    # Generate embedding for question
    embedding_service = get_embedding_service()
    query_embedding = embedding_service.generate_embedding(request.question)
    
    # Search for relevant chunks
    vector_store = get_vector_store()
    results, distances = vector_store.search(query_embedding, k=Config.TOP_K_RESULTS)
    
    if not results:
        return QueryResponse(
            answer="I couldn't find any relevant information in the uploaded documents to answer your question.",
            citations=[],
            retrieved_chunks=0
        )
    
    # Generate answer using LLM
    try:
        response = llm.generate_answer(request.question, results)
        return QueryResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")
