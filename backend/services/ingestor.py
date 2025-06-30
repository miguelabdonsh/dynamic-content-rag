"""
Content Ingestor: JSON → OpenAI Embeddings → Qdrant
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any


import openai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from backend.config.settings import settings
from backend.models.schemas import Article, Chunk

class ContentIngestor:
    """Minimal and efficient Ingestor"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.qdrant_client = QdrantClient(url=settings.QDRANT_URL)
        self._ensure_collection()
    
    def _ensure_collection(self) -> None:
        """Create collection if not exists"""
        try:
            self.qdrant_client.get_collection(settings.COLLECTION_NAME)
        except Exception:
            self.qdrant_client.create_collection(
                collection_name=settings.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=settings.VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )
    
    def load_articles(self) -> List[Article]:
        """Load all crawled JSONs"""
        articles = []
        for json_file in settings.CRAWLED_DIR.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    articles.append(Article(**data))
            except Exception:
                pass
        return articles
    
    def chunk_content(self, article: Article) -> List[Chunk]:
        """Split content into optimal chunks"""
        chunks = []
        content = article.content
        
        # Split by paragraphs first
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        current_chunk = ""
        chunk_id = 0
        
        for paragraph in paragraphs:
            # If the paragraph fits in the current chunk
            if len(current_chunk) + len(paragraph) <= settings.CHUNK_SIZE:
                current_chunk += paragraph + "\n\n"
            else:
                # Save current chunk if not empty
                if current_chunk.strip():
                    chunks.append(Chunk(
                        text=current_chunk.strip(),
                        source=article.url,
                        chunk_id=chunk_id,
                        metadata={
                            "title": article.title,
                            "timestamp": article.timestamp,
                            "chunk_of": len(paragraphs)
                        }
                    ))
                    chunk_id += 1
                
                # Start new chunk
                current_chunk = paragraph + "\n\n"
        
        # Add last chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                text=current_chunk.strip(),
                source=article.url,
                chunk_id=chunk_id,
                metadata={
                    "title": article.title,
                    "timestamp": article.timestamp,
                    "chunk_of": len(paragraphs)
                }
            ))
        
        return chunks
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings with OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model=settings.EMBEDDING_MODEL,
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception:
            return []
    
    def _generate_point_id(self, chunk: Chunk) -> str:
        """Generate truly unique ID for the point"""
        # Use full content hash + source + chunk_id for uniqueness
        content_hash = hashlib.md5(chunk.text.encode('utf-8')).hexdigest()
        unique_content = f"{chunk.source}_{chunk.chunk_id}_{content_hash}"
        return hashlib.md5(unique_content.encode('utf-8')).hexdigest()
    
    def store_chunks(self, chunks: List[Chunk]) -> int:
        """Store chunks in Qdrant"""
        if not chunks:
            return 0
        
        # Generate embeddings in batch
        texts = [chunk.text for chunk in chunks]
        embeddings = self.create_embeddings(texts)
        
        if not embeddings:
            return 0
        
        # Create points for Qdrant
        points = []
        for chunk, embedding in zip(chunks, embeddings):
            point_id = self._generate_point_id(chunk)
            points.append(PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "text": chunk.text,
                    "source": chunk.source,
                    "chunk_id": chunk.chunk_id,
                    **chunk.metadata
                }
            ))
        
        # Insert in Qdrant
        try:
            self.qdrant_client.upsert(
                collection_name=settings.COLLECTION_NAME,
                points=points
            )
            return len(points)
        except Exception:
            return 0
    
    def process_all(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Complete ingestion pipeline"""
        # Clear collection if it's a refresh
        if force_refresh:
            try:
                self.qdrant_client.delete_collection(settings.COLLECTION_NAME)
                self._ensure_collection()
            except Exception:
                pass
        
        # Load and process articles
        articles = self.load_articles()
        if not articles:
            return {"success": False, "message": "No articles found"}
        
        all_chunks = []
        for article in articles:
            chunks = self.chunk_content(article)
            all_chunks.extend(chunks)
        
        # Store in Qdrant
        vectors_created = self.store_chunks(all_chunks)
        
        return {
            "success": True,
            "files_processed": len(articles),
            "vectors_created": vectors_created,
            "message": f"Processed {len(articles)} articles into {vectors_created} vectors"
        }
    
    def process_specific_files(self, file_paths: List[Path]) -> Dict[str, Any]:
        """Process only specific files"""
        if not file_paths:
            return {"success": False, "message": "No files provided"}
        
        articles = []
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    articles.append(Article(**data))
            except Exception:
                pass
        
        if not articles:
            return {"success": False, "message": "No valid articles found"}
        
        all_chunks = []
        for article in articles:
            chunks = self.chunk_content(article)
            all_chunks.extend(chunks)
        
        vectors_created = self.store_chunks(all_chunks)
        
        return {
            "success": True,
            "files_processed": len(articles),
            "vectors_created": vectors_created,
            "message": f"Processed {len(articles)} new files into {vectors_created} vectors"
        }
    
    def has_vectors(self) -> bool:
        """Check if collection has any vectors"""
        try:
            info = self.qdrant_client.get_collection(settings.COLLECTION_NAME)
            return info.points_count > 0
        except Exception:
            return False