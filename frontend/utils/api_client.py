"""
Professional API Client for RAG Backend
Handles all HTTP communication with caching and error handling
"""

import requests
import streamlit as st
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class APIConfig:
    """API Configuration with sensible defaults"""
    base_url: str = "http://localhost:8080/api/v1"
    timeout: int = 30
    
    
class RAGAPIClient:
    """Professional API client with error handling and caching"""
    
    def __init__(self, config: APIConfig = None):
        self.config = config or APIConfig()
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Generic request method with error handling"""
        url = f"{self.config.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.config.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to RAG API. Make sure the backend is running.")
            return None
        except requests.exceptions.Timeout:
            st.error("Request timed out. Try again.")
            return None
        except requests.exceptions.HTTPError as e:
            st.error(f"API Error: {e.response.status_code}")
            return None
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            return None
    
    @st.cache_data(ttl=60)  # Cache for 1 minute
    def get_health(_self) -> Optional[Dict[str, Any]]:
        """Get system health status"""
        return _self._make_request("GET", "/health")
    
    @st.cache_data(ttl=30)  # Cache for 30 seconds
    def get_stats(_self) -> Optional[Dict[str, Any]]:
        """Get system statistics"""
        return _self._make_request("GET", "/stats")
    
    def query_rag(self, question: str, max_results: int = 5) -> Optional[Dict[str, Any]]:
        """Query the RAG system"""
        payload = {
            "question": question,
            "max_results": max_results
        }
        return self._make_request("POST", "/query", json=payload)
    
    def search_content(self, query: str, limit: int = 5) -> Optional[Dict[str, Any]]:
        """Search content without LLM generation"""
        params = {"q": query, "limit": limit}
        return self._make_request("GET", "/search", params=params)
    
    def generate_article(self, topic: str, context_sources: List[str] = None) -> Optional[str]:
        """Generate article using RAG context"""
        # First get relevant context
        search_results = self.search_content(topic, limit=8)
        if not search_results:
            return None
        
        # Build context from search results
        context_texts = [result['text'][:500] + "..." for result in search_results.get('results', [])]
        context = "\n\n".join(context_texts)
        
        # Generate article using the query endpoint with a structured prompt
        article_prompt = f"""Write a comprehensive crypto news article about: {topic}

Based on this context from recent crypto news:
{context}

Requirements:
- Professional journalism style
- Include key facts and data
- Structure with clear paragraphs
- Cite relevant information from the context
- Keep it informative and engaging"""
        
        result = self.query_rag(article_prompt, max_results=8)
        return result.get('answer') if result else None


# Global instance
@st.cache_resource
def get_api_client() -> RAGAPIClient:
    """Singleton API client"""
    return RAGAPIClient() 