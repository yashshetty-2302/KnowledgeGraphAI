from fastapi import APIRouter, Depends, HTTPException
from schemas import QueryRequest, QueryResponse
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore
from services.llm_service import LLMService
from services.self_correction import SelfCorrectionService
from services.graph_service import GraphService
from config import Config

router = APIRouter()

# Global instances to ensure consistency across requests
_embedding_service = None
_vector_store = None
_llm_service = None
_self_correction_service = None
_graph_service = None

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

def get_graph_service():
    global _graph_service
    if _graph_service is None:
        _graph_service = GraphService()
    return _graph_service

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
    graph_service = get_graph_service()
    
    # Initial retrieval
    current_question = request.question
    query_embedding = embedding_service.generate_embedding(current_question)
    results, distances = vector_store.search(query_embedding, k=Config.TOP_K_RESULTS)
    
    # Graph search
    graph_entities, graph_relationships = graph_service.search_graph(current_question)
    graph_chunk_ids = graph_service.get_relevant_chunks_from_graph(graph_entities, graph_relationships)
    
    # Debug: print graph search results
    print(f"DEBUG: Graph entities: {graph_entities}")
    print(f"DEBUG: Graph relationships: {graph_relationships}")
    print(f"DEBUG: Graph chunk IDs: {graph_chunk_ids}")
    
    retrieval_attempts = 1
    self_corrected = False
    graph_used = False
    
    if not results:
        # No results at all
        return QueryResponse(
            answer="I couldn't find any relevant information in the uploaded documents to answer your question.",
            citations=[],
            retrieved_chunks=0,
            retrieval_attempts=retrieval_attempts,
            self_corrected=self_corrected,
            evidence_sufficient=False,
            graph_used=False,
            graph_entities=[],
            graph_relationships=[]
        )
    
    # Evaluate context sufficiency with comprehensive checks
    is_sufficient, reasoning = self_correction.evaluate_context_sufficiency(current_question, results, distances)
    
    # Combine graph results if available
    if graph_entities or graph_relationships:
        # Use graph context to supplement retrieval
        graph_used = True
    
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
                evidence_sufficient=False,
                graph_used=graph_used,
                graph_entities=graph_entities,
                graph_relationships=[]
            )
        
        # Re-evaluate after reformulation
        is_sufficient, reasoning = self_correction.evaluate_context_sufficiency(reformulated_question, results, distances)
        
        if not is_sufficient:
            # Still insufficient after reformulation
            insufficient_response = llm.generate_insufficient_response(len(results))
            # Format relationships for response
            formatted_relationships = []
            for rel in graph_relationships:
                if isinstance(rel, tuple):
                    formatted_relationships.append(f"{rel[0]} {rel[2]} {rel[1]}")
                else:
                    formatted_relationships.append(rel)
            
            return QueryResponse(
                **insufficient_response,
                retrieval_attempts=retrieval_attempts,
                self_corrected=self_corrected,
                evidence_sufficient=False,
                graph_used=graph_used,
                graph_entities=graph_entities,
                graph_relationships=formatted_relationships
            )
    
    # Generate answer using LLM
    try:
        # Build graph context if available
        graph_context = ""
        if graph_entities or graph_relationships:
            graph_context = "\n\nAdditional Context from Knowledge Graph:\n"
            if graph_entities:
                graph_context += f"Relevant entities: {', '.join(graph_entities)}\n"
            if graph_relationships:
                graph_context += "Relevant relationships:\n"
                # Handle both tuple and string formats
                for rel in graph_relationships[:5]:  # Limit to top 5
                    if isinstance(rel, tuple):
                        source, target, relation = rel
                        graph_context += f"  - {source} {relation} {target}\n"
                    else:
                        graph_context += f"  - {rel}\n"
            graph_used = True
        
        # Modify the LLM prompt to include graph context
        if graph_context:
            # We'll need to modify the LLM service to accept additional context
            # For now, prepend to the first chunk's text
            if results:
                results[0]['text'] = graph_context + "\n\n" + results[0]['text']
        
        response = llm.generate_answer(current_question, results)
        # Format relationships for response
        formatted_relationships = []
        for rel in graph_relationships:
            if isinstance(rel, tuple):
                formatted_relationships.append(f"{rel[0]} {rel[2]} {rel[1]}")
            else:
                formatted_relationships.append(rel)
        
        return QueryResponse(
            **response,
            retrieval_attempts=retrieval_attempts,
            self_corrected=self_corrected,
            evidence_sufficient=True,
            graph_used=graph_used,
            graph_entities=graph_entities,
            graph_relationships=formatted_relationships
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")
