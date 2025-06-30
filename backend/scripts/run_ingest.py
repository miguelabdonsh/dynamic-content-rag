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
    print(f"Data directory: {settings.CRAWLED_DIR}")
    
    try:
        ingestor = ContentIngestor()
        result = ingestor.process_all(force_refresh=False)
        
        if result["success"]:
            print(f"✅ Success: {result['vectors_created']} vectors from {result['files_processed']} files")
        else:
            print(f"❌ Failed: {result['message']}")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 