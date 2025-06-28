"""
API Routes - Organized Endpoints
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any

from backend.models.schemas import (
    QueryRequest, QueryResponse, 
    IngestRequest, IngestResponse, 
    HealthResponse
)
from backend.services.ingestor import ContentIngestor
from backend.services.rag_engine import RAGEngine
from backend.config.settings import settings

# Main Router
router = APIRouter()

# Global instances (singleton pattern)
_ingestor = None
_rag_engine = None

def get_ingestor() -> ContentIngestor:
    """Singleton pattern for the ingestor"""
    global _ingestor
    if _ingestor is None:
        _ingestor = ContentIngestor()
    return _ingestor

def get_rag_engine() -> RAGEngine:
    """Singleton pattern for the RAG engine"""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine

@router.post("/ingest", response_model=IngestResponse)
async def ingest_content(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Ingest JSON content into Qdrant
    Executes in background to not block
    """
    try:
        ingestor = get_ingestor()
        
        # Execute ingestion (can be slow)
        result = ingestor.process_all(force_refresh=request.force_refresh)
        
        return IngestResponse(
            success=result["success"],
            files_processed=result.get("files_processed", 0),
            vectors_created=result.get("vectors_created", 0),
            message=result["message"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion error: {str(e)}")

@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Ask the RAG system a question
    Vector search + LLM generation
    """
    try:
        rag_engine = get_rag_engine()
        
        # Process query
        result = rag_engine.answer_question(
            query=request.question,
            max_results=request.max_results
        )
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            confidence=result["confidence"],
            response_time=result["response_time"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Complete health check of the system
    Verifies connectivity of all services
    """
    try:
        # Test Qdrant
        qdrant_connected = False
        articles_count = 0
        try:
            rag_engine = get_rag_engine()
            stats = rag_engine.get_collection_stats()
            qdrant_connected = stats["status"] == "healthy"
            articles_count = stats["total_vectors"]
        except Exception:
            pass
        
        # Test Redis (basic)
        redis_connected = False
        try:
            import redis
            r = redis.from_url(settings.REDIS_URL, socket_timeout=1)
            r.ping()
            redis_connected = True
        except Exception:
            pass
        
        # Test OpenAI
        openai_configured = bool(settings.OPENAI_API_KEY)
        
        # General status
        status = "healthy" if all([
            qdrant_connected, 
            openai_configured
        ]) else "partial"
        
        return HealthResponse(
            status=status,
            qdrant_connected=qdrant_connected,
            redis_connected=redis_connected,
            openai_configured=openai_configured,
            articles_count=articles_count,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check error: {str(e)}")

@router.get("/stats")
async def get_stats():
    """Quick system statistics"""
    try:
        rag_engine = get_rag_engine()
        stats = rag_engine.get_collection_stats()
        
        # Count crawled files
        crawled_files = len(list(settings.CRAWLED_DIR.glob("*.json")))
        
        return {
            "crawled_files": crawled_files,
            "total_vectors": stats["total_vectors"],
            "vector_size": stats["vector_size"],
            "collection_status": stats["status"],
            "embedding_model": settings.EMBEDDING_MODEL,
            "generation_model": settings.GEMINI_MODEL,
            "ai_stack": {
                "embeddings": "OpenAI",
                "generation": "Google Gemini"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")

@router.get("/search")
async def search_content(q: str, limit: int = 5):
    """
    Simple endpoint for vector search without LLM
    Useful for debugging
    """
    try:
        rag_engine = get_rag_engine()
        results = rag_engine.search_similar(q, max_results=limit)
        
        return {
            "query": q,
            "results_count": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}") 