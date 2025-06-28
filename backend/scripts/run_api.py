"""
Script to run the API server
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

import uvicorn
from backend.config.settings import settings

def main():
    """Run FastAPI server - fully automatic"""
    print("Starting Crypto RAG API server...")
    print(f"Server: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"Docs: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    
    try:
        uvicorn.run(
            "backend.api.app:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=True,  
            access_log=True,
            log_level="info"
        )
    except Exception as e:
        print(f"Server error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 