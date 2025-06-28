"""
FastAPI Application - Crypto RAG API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.config.settings import settings
from backend.services.auto_ingest import auto_ingest
from backend.services.ingestor import ContentIngestor

# Create application with configuration from YAML
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware with configuration from YAML
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.CORS_METHODS, 
    allow_headers=settings.CORS_HEADERS,
)

# Include routes
app.include_router(router, prefix="/api/v1")

# Basic health check at root
@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "running",
        "stack": {
            "embeddings": "OpenAI text-embedding-ada-002",
            "generation": f"Google {settings.GEMINI_MODEL}",
            "vectordb": "Qdrant",
            "cache": "Redis"
        },
        "docs": "/docs"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize system on startup - fully automatic"""
    print("Configuration loaded successfully")
    print(f"AI Stack: {settings.EMBEDDING_MODEL} + {settings.GEMINI_MODEL}")
    print(f"API Server: {settings.API_HOST}:{settings.API_PORT}")
    
    # Auto-initialization: Check if we need initial ingestion
    ingestor = ContentIngestor()
    if not ingestor.has_vectors():
        print("No vectors found - performing initial ingestion...")
        try:
            result = ingestor.process_all(force_refresh=False)
            if result["success"]:
                print(f"Initial ingestion complete: {result['vectors_created']} vectors created")
            else:
                print("Initial ingestion failed - check your data directory")
        except Exception as e:
            print(f"Initial ingestion error: {e}")
    else:
        print("Vectors found - skipping initial ingestion")
    
    # Start auto-ingest file watcher for new files
    auto_ingest.start_watching()
    print("Auto-ingest started - monitoring for new files")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    auto_ingest.stop_watching()
    print("Auto-ingest stopped") 