from fastapi import APIRouter, Depends, HTTPException
from schemas import QueryRequest, QueryResponse
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore
from services.llm_service import LLMService
from services.self_correction import SelfCorrectionService
from config import Config

router = APIRouter()

# Global instances to ensure consistency across requests
_embedding_service = None
_vector_store = None
_llm_service = None
_self_correction_service = None

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

def get_self_correction_service():
    global _self_correction_service
    if _self_correction_service is None:
        try:
            _self_correction_service = SelfCorrectionService()
        except ValueError as e:
            print(f"Warning: {str(e)}")
    return _self_correction_service

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query documents using RAG with self-correction."""
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    llm = get_llm_service()
    if llm is None:
        raise HTTPException(status_code=500, detail="LLM service not configured. Please set GROQ_API_KEY")
    
    self_correction = get_self_correction_service()
    if self_correction is None:
        raise HTTPException(status_code=500, detail="Self-correction service not configured")
    
    embedding_service = get_embedding_service()
    vector_store = get_vector_store()
    
    # Initial retrieval
    current_question = request.question
    query_embedding = embedding_service.generate_embedding(current_question)
    results, distances = vector_store.search(query_embedding, k=Config.TOP_K_RESULTS)
    
    retrieval_attempts = 1
    self_corrected = False
    
    if not results:
        # No results at all
        return QueryResponse(
            answer="I couldn't find any relevant information in the uploaded documents to answer your question.",
            citations=[],
            retrieved_chunks=0,
            retrieval_attempts=retrieval_attempts,
            self_corrected=self_corrected,
            evidence_sufficient=False
        )
    
    # Evaluate context sufficiency with comprehensive checks
    is_sufficient, reasoning = self_correction.evaluate_context_sufficiency(current_question, results, distances)
    
    if not is_sufficient:
        # Attempt self-correction
        # Reformulate query
        reformulated_question = self_correction.reformulate_query(current_question, results)
        
        # Second retrieval
        retrieval_attempts = 2
        self_corrected = True
        query_embedding = embedding_service.generate_embedding(reformulated_question)
        results, distances = vector_store.search(query_embedding, k=Config.TOP_K_RESULTS)
        
        if not results:
            # Still no results after reformulation
            return QueryResponse(
                answer="I couldn't find sufficient evidence in the uploaded documents to answer this question, even after reformulating the query.",
                citations=[],
                retrieved_chunks=0,
                retrieval_attempts=retrieval_attempts,
                self_corrected=self_corrected,
                evidence_sufficient=False
            )
        
        # Re-evaluate after reformulation
        is_sufficient, reasoning = self_correction.evaluate_context_sufficiency(reformulated_question, results, distances)
        
        if not is_sufficient:
            # Still insufficient after reformulation
            insufficient_response = llm.generate_insufficient_response(len(results))
            return QueryResponse(
                **insufficient_response,
                retrieval_attempts=retrieval_attempts,
                self_corrected=self_corrected,
                evidence_sufficient=False
            )
    
    # Generate answer using LLM
    try:
        response = llm.generate_answer(current_question, results)
        return QueryResponse(
            **response,
            retrieval_attempts=retrieval_attempts,
            self_corrected=self_corrected,
            evidence_sufficient=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")
