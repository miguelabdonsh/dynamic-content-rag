"""
Crypto RAG Streamlit Application
Professional frontend for the dynamic content RAG system
"""

import streamlit as st
from utils.api_client import get_api_client
from components.chat_interface import render_chat_interface
from components.article_creator import render_article_creator


def main():
    """Main application entry point"""
    # Page configuration
    st.set_page_config(
        page_title="Crypto RAG Assistant",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    _inject_custom_css()
    
    # Sidebar
    _render_sidebar()
    
    # Main content
    _render_main_content()


def _inject_custom_css():
    """Minimal CSS for better spacing"""
    st.markdown("""
    <style>
    .main .block-container { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)


def _render_sidebar():
    """Simple sidebar navigation"""
    st.sidebar.title("Crypto Assistant")
    
    # Navigation only
    page = st.sidebar.radio(
        "Select:",
        ["Chat", "Create Article"],
        index=0
    )
    
    # Store page selection in session state
    st.session_state.current_page = page
    
    # Simple clear button
    if st.sidebar.button("Clear History"):
        if "chat_history" in st.session_state:
            st.session_state.chat_history = []
        if "generated_article" in st.session_state:
            st.session_state.generated_article = None
        st.rerun()





def _render_main_content():
    """Render main content based on current page"""
    page = st.session_state.get("current_page", "Chat")
    
    if page == "Chat":
        render_chat_interface()
    elif page == "Create Article":
        render_article_creator()
    else:
        st.error("Unknown page selected")





if __name__ == "__main__":
    main() 