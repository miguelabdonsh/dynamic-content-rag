# Dynamic Content RAG System

AI-powered crypto news system with RAG (Retrieval-Augmented Generation) capabilities.

## 🚀 Quick Start

### 1. Start Backend Services
```bash
./scripts/start-services.sh
uv run backend/scripts/run_api.py
```

### 2. Start Frontend Interface
```bash
cd frontend
streamlit run streamlit_app.py
```

## 📖 Features

- **🤖 Chat Assistant**: Ask questions about crypto news
- **✍️ Article Creator**: Generate crypto articles with AI
- **⚡ Redis Caching**: 5-10x faster responses
- **🔍 Vector Search**: Semantic search with Qdrant
- **📊 Real-time Stats**: System health monitoring

## 🏗️ Architecture

- **Backend**: FastAPI + Qdrant + Redis + OpenAI + Google Gemini
- **Frontend**: Streamlit with modular components
- **Data**: 30 crypto news articles → 42 intelligent chunks

## 🌐 URLs

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs
