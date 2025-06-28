"""
RAG Engine: Vector Search + Google Gemini Generation
"""

import time
from typing import List, Dict, Any, Tuple

import openai
import google.generativeai as genai
from qdrant_client import QdrantClient


from backend.config.settings import settings

class RAGEngine:
    """Optimized RAG Engine: OpenAI embeddings + Google Gemini generation"""
    
    def __init__(self):
        # OpenAI for embeddings only
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Google Gemini for content generation
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        # Qdrant for vector search
        self.qdrant_client = QdrantClient(url=settings.QDRANT_URL)
    
    def _create_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for the query"""
        try:
            response = self.openai_client.embeddings.create(
                model=settings.EMBEDDING_MODEL,
                input=[query]
            )
            return response.data[0].embedding
        except Exception:
            return []
    
    def search_similar(self, query: str, max_results: int = None) -> List[Dict[str, Any]]:
        """Vector search for similar content"""
        max_results = max_results or settings.MAX_SEARCH_RESULTS
        
        # Generate query embedding
        query_embedding = self._create_query_embedding(query)
        if not query_embedding:
            return []
        
        try:
            # Search in Qdrant
            search_result = self.qdrant_client.search(
                collection_name=settings.COLLECTION_NAME,
                query_vector=query_embedding,
                limit=max_results,
                score_threshold=settings.SCORE_THRESHOLD
            )
            
            # Format results
            results = []
            for point in search_result:
                results.append({
                    "text": point.payload.get("text", ""),
                    "source": point.payload.get("source", ""),
                    "title": point.payload.get("title", ""),
                    "score": float(point.score),
                    "timestamp": point.payload.get("timestamp", "")
                })
            
            return results
            
        except Exception:
            return []
    
    def _build_prompt(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:
        """Build prompt for GPT with context"""
        if not context_chunks:
            return f"""Question: {query}

No relevant context found in the knowledge base. Please respond that you don't have information about this topic."""
        
        # Build context
        context_text = ""
        sources = []
        
        for i, chunk in enumerate(context_chunks, 1):
            context_text += f"\n[Source {i}] {chunk['title']}\n{chunk['text']}\n"
            sources.append(chunk['source'])
        
        prompt = f"""You are a helpful assistant that answers questions about cryptocurrency news based on provided context.

Context from recent crypto news articles:
{context_text}

Question: {query}

Instructions:
- Answer the question using ONLY the information from the provided context
- If the context doesn't contain enough information, say so clearly
- Be concise and factual
- Don't make up information not present in the context
- Cite specific articles when relevant

Answer:"""
        
        return prompt
    
    def generate_answer(self, query: str, context_chunks: List[Dict[str, Any]]) -> Tuple[str, float]:
        """Generate answer with Google Gemini using the context"""
        prompt = self._build_prompt(query, context_chunks)
        
        try:
            # Configure generation
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE,
                candidate_count=1
            )
            
            # Generate answer with Gemini
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Check if there is content
            if not response.text:
                return "I couldn't generate a proper response. Please try rephrasing your question.", 0.0
            
            answer = response.text.strip()
            
            # Calculate confidence based on the quality of the context
            confidence = self._calculate_confidence(context_chunks)
            
            return answer, confidence
            
        except Exception:
            return "Sorry, I encountered an error generating the response.", 0.0
    
    def _calculate_confidence(self, context_chunks: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on the context"""
        if not context_chunks:
            return 0.0
        
        # Confidence based on search scores
        scores = [chunk.get('score', 0.0) for chunk in context_chunks]
        avg_score = sum(scores) / len(scores)
        
        # Normalize to 0-1
        confidence = min(avg_score * 1.5, 1.0)  # Adjustment factor
        
        return round(confidence, 2)
    
    def answer_question(self, query: str, max_results: int = None) -> Dict[str, Any]:
        """Complete pipeline: search + generate"""
        start_time = time.time()
        
        # Vector search
        context_chunks = self.search_similar(query, max_results)
        
        # Answer generation
        answer, confidence = self.generate_answer(query, context_chunks)
        
        # Extract unique sources
        sources = list(set(chunk.get('source', '') for chunk in context_chunks))
        sources = [s for s in sources if s]  # Filter out empties
        
        response_time = round(time.time() - start_time, 2)
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "response_time": response_time,
            "chunks_found": len(context_chunks)
        }
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            info = self.qdrant_client.get_collection(settings.COLLECTION_NAME)
            return {
                "total_vectors": info.points_count,
                "vector_size": info.config.params.vectors.size,
                "status": "healthy"
            }
        except Exception as e:
            return {
                "total_vectors": 0,
                "vector_size": 0,
                "status": f"error: {e}"
            } 