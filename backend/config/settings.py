"""
Centralized RAG system configuration
Load from config.yaml with .env variable interpolation
"""

import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv
import os

class Settings:
    """Secure Configuration: YAML + .env with variables ${VAR}"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Base paths
        self.PROJECT_ROOT = Path(__file__).parent.parent.parent
        self.CONFIG_FILE = Path(__file__).parent / "config.yaml"
        
        # Load and interpolate configuration
        self.config = self._load_and_interpolate_config()
        
        # Apply configuration
        self._setup_all()
    
    def _load_and_interpolate_config(self) -> Dict[str, Any]:
        """Load YAML"""
        if not self.CONFIG_FILE.exists():
            raise FileNotFoundError(f"Config file not found: {self.CONFIG_FILE}")
        
        with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _setup_all(self):
        """Configure all sections from interpolated YAML"""
        
        # Paths
        paths = self.config.get('paths', {})
        self.DATA_DIR = self.PROJECT_ROOT / paths.get('data_dir')
        self.CRAWLED_DIR = self.PROJECT_ROOT / paths.get('crawled_dir')
        self.CRAWLED_DIR.mkdir(parents=True, exist_ok=True)
        
        # API Keys
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
        
        # External services
        services = self.config.get('services', {})
        self.QDRANT_URL = services.get('qdrant_url')
        self.REDIS_URL = services.get('redis_url')
        
        # API Server
        api = self.config.get('api', {})
        self.API_HOST = api.get('host')
        self.API_PORT = int(api.get('port'))
        self.API_TITLE = api.get('title')
        self.API_DESCRIPTION = api.get('description')
        self.API_VERSION = api.get('version')
        
        # CORS
        cors = api.get('cors', {})
        self.CORS_ORIGINS = cors.get('allow_origins')
        self.CORS_METHODS = cors.get('allow_methods')
        self.CORS_HEADERS = cors.get('allow_headers')
        
        # AI Models
        ai = self.config.get('ai', {})
        openai_cfg = ai.get('openai', {})
        google_cfg = ai.get('google', {})
        
        self.EMBEDDING_MODEL = openai_cfg.get('embedding_model')
        self.OPENAI_TIMEOUT = openai_cfg.get('timeout')
        self.MAX_EMBEDDING_BATCH = openai_cfg.get('max_embedding_batch')
        
        self.GEMINI_MODEL = google_cfg.get('model')
        self.MAX_TOKENS = google_cfg.get('max_tokens')
        self.TEMPERATURE = google_cfg.get('temperature')
        self.GOOGLE_TIMEOUT = google_cfg.get('timeout')
        
        # Qdrant
        qdrant = self.config.get('vectordb', {}).get('qdrant', {})
        self.COLLECTION_NAME = qdrant.get('collection_name')
        self.VECTOR_SIZE = qdrant.get('vector_size')
        self.DISTANCE_METRIC = qdrant.get('distance_metric')
        self.QDRANT_TIMEOUT = qdrant.get('timeout')
        
        # Redis
        redis_cfg = self.config.get('cache', {}).get('redis', {})
        self.CACHE_TTL = redis_cfg.get('ttl')
        self.REDIS_TIMEOUT = redis_cfg.get('timeout')
        
        # Processing
        processing = self.config.get('processing', {})
        chunking = processing.get('chunking', {})
        search = processing.get('search', {})
        
        self.CHUNK_SIZE = chunking.get('chunk_size')
        self.CHUNK_OVERLAP = chunking.get('chunk_overlap')
        self.MIN_CHUNK_SIZE = chunking.get('min_chunk_size')
        self.MAX_SEARCH_RESULTS = search.get('max_results')
        self.SCORE_THRESHOLD = search.get('score_threshold')
    

# Global instance
settings = Settings() 