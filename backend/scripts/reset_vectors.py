"""
Reset vectors in Qdrant collection
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.services.ingestor import ContentIngestor

def main():
    """Reset and rebuild vector collection"""
    print("Resetting vector collection...")
    
    try:
        ingestor = ContentIngestor()
        result = ingestor.process_all(force_refresh=True)
        
        if result["success"]:
            print(f"✅ Reset complete: {result['vectors_created']} vectors from {result['files_processed']} files")
        else:
            print(f"❌ Reset failed: {result['message']}")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 