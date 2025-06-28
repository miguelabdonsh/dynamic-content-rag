"""
Script to run content ingestion
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.services.ingestor import ContentIngestor
from backend.config.settings import settings

def main():
    """Run complete ingestion"""
    print("Starting content ingestion...")
    
    # Run ingestion
    try:
        ingestor = ContentIngestor()
        print(f"Looking for JSON files in: {settings.CRAWLED_DIR}")
        
        result = ingestor.process_all(force_refresh=False)
        
        if result["success"]:
            print(f"Ingestion completed successfully!")
            print(f"Files processed: {result['files_processed']}")
            print(f"Vectors created: {result['vectors_created']}")
            print(f"Message: {result['message']}")
        else:
            print(f"Ingestion failed: {result['message']}")
            return 1
            
    except Exception as e:
        print(f"Ingestion error: {e}")
        return 1
    
    print("Ingestion completed! Ready for queries.")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 