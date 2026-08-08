from groq import Groq
from typing import List, Dict
from config import Config

class LLMService:
    def __init__(self):
        if not Config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set in environment variables")
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"
    
    def generate_answer(self, question: str, context_chunks: List[Dict]) -> Dict:
        """Generate grounded answer with citations."""
        # Build context from chunks
        context = self._build_context(context_chunks)
        
        # Build prompt
        prompt = self._build_prompt(question, context)
        
        # Generate response
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based ONLY on the provided context. If the context doesn't contain enough information to answer the question, explicitly say so. Always include citations in your answer using the format [chunk_id]."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1024
        )
        
        answer = response.choices[0].message.content
        
        # Extract citations
        citations = self._extract_citations(context_chunks)
        
        return {
            "answer": answer,
            "citations": citations,
            "retrieved_chunks": len(context_chunks)
        }
    
    def _build_context(self, chunks: List[Dict]) -> str:
        """Build context string from chunks."""
        context_parts = []
        for chunk in chunks:
            context_parts.append(
                f"[{chunk['chunk_id']}] Document: {chunk['document']}, Page {chunk['page']}\n{chunk['text']}"
            )
        return "\n\n".join(context_parts)
    
    def _build_prompt(self, question: str, context: str) -> str:
        """Build prompt for LLM."""
        return f"""Context:
{context}

Question: {question}

Answer the question using ONLY the information provided in the context above. If the context doesn't contain enough information to answer the question, explicitly state that you couldn't find sufficient evidence. Include citations using the chunk IDs in square brackets, like [chunk_id]."""
    
    def _extract_citations(self, chunks: List[Dict]) -> List[Dict]:
        """Extract citation information from chunks."""
        citations = []
        for chunk in chunks:
            citations.append({
                "document": chunk["document"],
                "page": chunk["page"],
                "chunk_id": chunk["chunk_id"]
            })
        return citations
