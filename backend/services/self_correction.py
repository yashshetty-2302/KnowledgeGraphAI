from typing import List, Dict, Tuple
import re
from services.llm_service import LLMService
from config import Config

class SelfCorrectionService:
    def __init__(self):
        self.llm_service = LLMService()
        self.distance_threshold = 2.0  # Maximum distance for considering a chunk relevant
    
    def check_lexical_overlap(self, question: str, chunks: List[Dict]) -> Tuple[bool, str]:
        """
        Check if there's meaningful lexical overlap between question and chunks.
        
        Returns:
            Tuple of (has_overlap, reasoning)
        """
        if not chunks:
            return False, "No chunks to compare."
        
        # Extract important terms from question (nouns, keywords)
        question_lower = question.lower()
        important_words = set(re.findall(r'\b[a-z]{3,}\b', question_lower))
        
        # Remove common words
        common_words = {'what', 'how', 'where', 'when', 'why', 'which', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'need', 'want', 'like', 'get', 'got', 'about', 'for', 'with', 'from', 'to', 'in', 'on', 'at', 'by', 'of', 'as', 'or', 'and', 'but', 'if', 'then', 'than', 'so', 'very', 'more', 'most', 'some', 'any', 'such', 'same', 'into', 'over', 'after', 'before', 'between', 'under', 'again', 'further', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very'}
        important_words -= common_words
        
        if not important_words:
            return True, "Question contains no specific keywords to check."
        
        # Check if important words appear in chunks
        combined_chunk_text = ' '.join(chunk['text'].lower() for chunk in chunks)
        overlap_count = sum(1 for word in important_words if word in combined_chunk_text)
        
        overlap_ratio = overlap_count / len(important_words) if important_words else 0
        
        if overlap_ratio >= 0.3:  # At least 30% of important words should appear
            return True, f"Found {overlap_count}/{len(important_words)} important words in chunks."
        else:
            return False, f"Only found {overlap_count}/{len(important_words)} important words in chunks. Low lexical overlap."
    
    def check_distance_threshold(self, distances: np.ndarray) -> Tuple[bool, str]:
        """
        Check if retrieved chunks are within reasonable distance threshold.
        
        Returns:
            Tuple of (within_threshold, reasoning)
        """
        if len(distances) == 0:
            return False, "No distances to check."
        
        # Check if the best result is within threshold
        best_distance = distances[0][0] if len(distances) > 0 else float('inf')
        
        if best_distance > self.distance_threshold:
            return False, f"Best result distance {best_distance:.2f} exceeds threshold {self.distance_threshold}."
        
        # Check if most results are within reasonable range
        avg_distance = distances[0].mean() if len(distances) > 0 else float('inf')
        
        if avg_distance > self.distance_threshold * 1.5:
            return False, f"Average distance {avg_distance:.2f} too high."
        
        return True, f"Best distance {best_distance:.2f} within threshold."
    
    def evaluate_context_sufficiency_llm(self, question: str, chunks: List[Dict]) -> Tuple[bool, str]:
        """
        Use LLM to evaluate if context contains explicit evidence for the question.
        
        Returns:
            Tuple of (is_sufficient, reasoning)
        """
        if not chunks:
            return False, "No chunks were retrieved."
        
        # Build context from chunks
        context = self._build_context(chunks)
        
        # Build evaluation prompt with structured output
        prompt = f"""You are evaluating whether the following context contains EXPLICIT evidence to answer a question.

Context:
{context}

Question: {question}

Evaluate strictly: Does the provided context contain explicit, direct evidence that answers the user's question?
- The evidence must be DIRECTLY stated in the context
- If the context mentions related topics but doesn't answer the specific question, mark as insufficient
- If the question asks about specific terms (like "pet insurance", "gym membership", etc.) that are not mentioned in the context, mark as insufficient
- If the answer requires information not present in the context, mark as insufficient

Return JSON with "sufficient" (boolean) and "reason" (string) fields."""

        try:
            evaluation = self.llm_service.generate_json_response(prompt)
            
            if isinstance(evaluation, dict) and 'sufficient' in evaluation:
                is_sufficient = bool(evaluation['sufficient'])
                reasoning = evaluation.get('reason', 'No reason provided')
                return is_sufficient, reasoning
            else:
                return False, f"Invalid response format: {evaluation}"
                
        except Exception as e:
            # If evaluation fails, assume insufficient to be safe
            return False, f"Evaluation failed: {str(e)}"
    
    def evaluate_context_sufficiency(self, question: str, chunks: List[Dict], distances: np.ndarray) -> Tuple[bool, str]:
        """
        Comprehensive evaluation using multiple checks.
        
        Returns:
            Tuple of (is_sufficient, reasoning)
        """
        if not chunks:
            return False, "No chunks were retrieved."
        
        # Check 1: Distance threshold
        distance_ok, distance_reason = self.check_distance_threshold(distances)
        if not distance_ok:
            return False, f"Distance check failed: {distance_reason}"
        
        # Check 2: Lexical overlap
        lexical_ok, lexical_reason = self.check_lexical_overlap(question, chunks)
        if not lexical_ok:
            return False, f"Lexical check failed: {lexical_reason}"
        
        # Check 3: LLM evidence evaluation
        llm_ok, llm_reason = self.evaluate_context_sufficiency_llm(question, chunks)
        if not llm_ok:
            return False, f"LLM evaluation failed: {llm_reason}"
        
        return True, f"All checks passed: {distance_reason}, {lexical_reason}, {llm_reason}"
    
    def reformulate_query(self, original_question: str, chunks: List[Dict]) -> str:
        """
        Reformulate the question to improve retrieval based on initial results.
        
        Returns:
            Reformulated query string
        """
        # Build context from chunks
        context = self._build_context(chunks)
        
        # Build reformulation prompt
        prompt = f"""You are reformulating a search query to get better results from a document database.

Original Question: {original_question}

Context retrieved from initial search (this context was insufficient):
{context}

Reformulate the original question to be more specific and likely to retrieve relevant information. 
Focus on:
1. Key terms and entities that should be in the documents
2. Specific aspects of the question that need to be addressed
3. Alternative phrasings that might match document content better

Respond with ONLY the reformulated question, no explanation."""

        try:
            response = self.llm_service.client.chat.completions.create(
                model=self.llm_service.model,
                messages=[
                    {"role": "system", "content": "You are a query reformulation expert. Respond only with the reformulated question."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            reformulated = response.choices[0].message.content.strip()
            
            # If reformulation fails or is empty, return original
            if not reformulated or len(reformulated) < 5:
                return original_question
            
            return reformulated
            
        except Exception as e:
            # If reformulation fails, return original question
            return original_question
    
    def _build_context(self, chunks: List[Dict]) -> str:
        """Build context string from chunks."""
        context_parts = []
        for chunk in chunks:
            context_parts.append(
                f"[{chunk['chunk_id']}] Document: {chunk['document']}, Page {chunk['page']}\n{chunk['text']}"
            )
        return "\n\n".join(context_parts)
