"""
Article Creator Component
Generate crypto news articles using RAG context
"""

import streamlit as st
from typing import List, Optional
from utils.api_client import get_api_client


def render_article_creator():
    """Simple article creation interface"""
    st.header("Create Article")
    st.markdown("Generate crypto articles")
    
    # Initialize session state
    if "generated_article" not in st.session_state:
        st.session_state.generated_article = None
    
    # API client
    api_client = get_api_client()
    
    # Simple form
    topic = st.text_input("Article Topic", placeholder="e.g., Bitcoin price, DeFi trends...")
    
    if st.button("Generate Article", type="primary"):
        if topic:
            _generate_simple_article(topic, api_client)
        else:
            st.warning("Please enter a topic")
    
    # Display generated article
    if st.session_state.generated_article:
        st.divider()
        st.subheader("Generated Article")
        st.markdown(st.session_state.generated_article)


def _generate_simple_article(topic: str, api_client):
    """Generate article with simple prompt"""
    with st.spinner("Generating article..."):
        article = api_client.generate_article(topic)
    
    if article:
        st.session_state.generated_article = article
        st.success("Article generated!")
        st.balloons()
    else:
        st.error("Failed to generate article.")


 