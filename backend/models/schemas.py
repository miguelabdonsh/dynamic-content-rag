# INSERT_YOUR_REWRITE_HERE
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Request Models
class QueryRequest(BaseModel):
    """Request to query the RAG"""
    question: str = Field(..., min_length=3, max_length=2000)
    max_results: int = Field(default=5, ge=1, le=20)

class IngestRequest(BaseModel):
    """Request to ingest new files"""
    force_refresh: bool = Field(default=False)

# Response Models
class QueryResponse(BaseModel):
    """Response from the RAG with answer and sources"""
    answer: str
    sources: List[str]
    confidence: float = Field(..., ge=0.0, le=1.0)
    response_time: float
    cached: bool = Field(default=False)

class IngestResponse(BaseModel):
    """Response from the ingestion"""
    success: bool
    files_processed: int
    vectors_created: int
    message: str

class HealthResponse(BaseModel):
    """Response from the health check"""
    status: str
    qdrant_connected: bool
    redis_connected: bool
    openai_configured: bool
    articles_count: int
    timestamp: datetime

# Internal Models
class Article(BaseModel):
    """Model for crawled articles"""
    title: str
    url: str
    content: str
    timestamp: str

class Chunk(BaseModel):
    """Model for content chunks"""
    text: str
    source: str
    chunk_id: int
    metadata: dict = Field(default_factory=dict) 