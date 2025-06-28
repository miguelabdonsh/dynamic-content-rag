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
    """Run FastAPI server"""
    print("Starting Crypto RAG API server...")
    
    # Server configuration
    print(f"Server will start on http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"API docs available at http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print(f"Redoc available at http://{settings.API_HOST}:{settings.API_PORT}/redoc")
    
    try:
        # Run server
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