"""
Simple tests for the RAG system
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Mock API keys for tests if not configured
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "test-key"
if not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = "test-key"

from backend.config.settings import settings

def test_configuration():
    """Test basic system configuration"""
    assert settings.EMBEDDING_MODEL == "text-embedding-ada-002"
    assert settings.GEMINI_MODEL == "gemini-2.0-flash-lite"
    assert "localhost:6333" in settings.QDRANT_URL
    assert settings.COLLECTION_NAME == "crypto_articles"
    assert settings.API_PORT == 8080

def test_data_availability():
    """Test that crawled data exists"""
    json_files = list(settings.CRAWLED_DIR.glob("*.json"))
    assert len(json_files) > 0, f"No JSON files found in {settings.CRAWLED_DIR}"

def test_imports():
    """Test that core modules can be imported"""
    from backend.services.ingestor import ContentIngestor
    from backend.services.rag_engine import RAGEngine
    from backend.services.cache import cache
    from backend.services.auto_ingest import auto_ingest
    from backend.api.app import app

def main():
    """Run all tests"""
    tests = [test_configuration, test_data_availability, test_imports]
    
    for test in tests:
        test()
    
    print("All tests passed")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 