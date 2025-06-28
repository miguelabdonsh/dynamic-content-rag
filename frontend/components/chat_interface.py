"""
Chat Interface Component for RAG Queries
Professional, clean and efficient chat experience
"""

import streamlit as st
from typing import Dict, Any
from utils.api_client import get_api_client


def render_chat_interface():
    """Simple chat interface"""
    st.header("Ask Questions")
    st.markdown("Ask about crypto news")
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # API client
    api_client = get_api_client()
    
    # Simple chat input
    query = st.chat_input("Type your question...")
    
    # Process new query
    if query:
        _process_query(query, api_client)
    
    # Display chat history
    _render_chat_history()


def _process_query(query: str, api_client):
    """Process user query and add to chat history"""
    # Add user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": query
    })
    
    # Show thinking indicator
    with st.spinner("Searching..."):
        result = api_client.query_rag(query, max_results=5)
    
    if result:
        # Add assistant response
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": result.get("answer", "No answer generated.")
        })
    else:
        # Add error message
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "Sorry, couldn't process your question."
        })


def _render_chat_history():
    """Render simple chat conversation"""
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("human"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])

