"""
Updated tests for the RAG system
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
    print("Testing configuration...")
    
    # Verify AI models
    assert settings.EMBEDDING_MODEL == "text-embedding-ada-002"
    assert settings.GEMINI_MODEL == "gemini-2.0-flash-lite"
    
    # Verify services
    assert "localhost:6333" in settings.QDRANT_URL
    assert settings.COLLECTION_NAME == "crypto_articles"
    
    # Verify API
    assert settings.API_PORT == 8080
    assert settings.API_VERSION == "0.2.0"
    
    print("Configuration test passed")

def test_crawled_data():
    """Test that crawled data exists"""
    print("Testing crawled data...")
    
    json_files = list(settings.CRAWLED_DIR.glob("*.json"))
    assert len(json_files) > 0, f"No JSON files found in {settings.CRAWLED_DIR}"
    
    # Verify structure of a JSON file
    if json_files:
        import json
        with open(json_files[0], 'r', encoding='utf-8') as f:
            sample_data = json.load(f)
            required_keys = ['title', 'url', 'content', 'timestamp']
            for key in required_keys:
                assert key in sample_data, f"Missing key '{key}' in JSON structure"
    
    print(f"Found {len(json_files)} crawled JSON files with correct structure")

def test_core_imports():
    """Test that core modules can be imported"""
    print("Testing core imports...")
    
    try:
        from backend.services.ingestor import ContentIngestor
        from backend.services.rag_engine import RAGEngine
        from backend.api.app import app
        from backend.models.schemas import QueryRequest, QueryResponse
        
        print("Core modules import successfully")
        
    except Exception as e:
        print(f"Import error: {e}")
        raise

def main():
    """Run all tests"""
    print("Running RAG system tests...\n")
    
    tests = [
        test_configuration,
        test_crawled_data,
        test_core_imports
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"{test.__name__} failed: {e}")
            failed += 1
        print()
    
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("All tests passed! RAG system ready.")
        return 0
    else:
        print("Some tests failed. Check configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 