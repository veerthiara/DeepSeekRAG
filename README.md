# DeepSeek RAG Chatbot - Reorganized & Simplified

## 🎯 Overview

A clean, professionally organized FastAPI-based chatbot with RAG (Retrieval Augmented Generation) and SQL capabilities. This project has been completely reorganized to follow FastAPI best practices and simplified to focus on essential functionality.

## 📁 Project Structure

```
DeepSeekRAGChatbot/
├── chatbot_be/                    # Backend (FastAPI)
│   ├── app/
│   │   ├── api/                   # API layer
│   │   │   ├── v1/               # API version 1
│   │   │   │   ├── chat.py       # Main chat endpoints
│   │   │   │   ├── health.py     # Health check endpoints
│   │   │   │   ├── rag.py        # RAG-specific endpoints
│   │   │   │   └── sql.py        # SQL query endpoints
│   │   │   └── server.py         # FastAPI app configuration
│   │   ├── core/                 # Core functionality
│   │   │   ├── config.py         # Application settings
│   │   │   ├── cors.py           # CORS configuration
│   │   │   └── exceptions.py     # Custom exceptions
│   │   ├── models/               # Database models
│   │   │   └── database.py       # Database connection & models
│   │   ├── schemas/              # Pydantic schemas
│   │   │   ├── chat.py          # Chat request/response schemas
│   │   │   ├── common.py        # Common schemas (health, errors)
│   │   │   ├── rag.py           # RAG-specific schemas
│   │   │   ├── session.py       # Session management schemas
│   │   │   └── sql.py           # SQL operation schemas
│   │   ├── services/             # Business logic
│   │   │   ├── conversational_service.py  # Main conversation orchestrator
│   │   │   ├── data_extractor.py          # Database data extraction
│   │   │   ├── llm_client.py              # LLM communication
│   │   │   ├── query_router.py            # Intelligent query routing
│   │   │   ├── rag_service.py             # RAG implementation
│   │   │   ├── session_manager.py         # Session management
│   │   │   ├── sql_client.py              # SQL agent
│   │   │   └── vector_store.py            # Vector storage
│   │   └── utils/                # Utility functions
│   ├── main.py                   # Application entry point
│   ├── pyproject.toml           # Poetry dependencies
│   └── database/                # Database files
└── chatbot_fe/                   # Frontend (Streamlit)
    ├── streamlit_chat.py        # Simple chat interface
    ├── pyproject.toml          # Frontend dependencies
    └── README.md               # Frontend documentation
```

## 🚀 Quick Start

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd chatbot_be
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Start the server:**
   ```bash
   PYTHONPATH=. poetry run python main.py
   ```

   The API will be available at:
   - Main API: http://127.0.0.1:8000
   - API Documentation: http://127.0.0.1:8000/docs
   - Health Check: http://127.0.0.1:8000/api/v1/health

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd chatbot_fe
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Start the Streamlit app:**
   ```bash
   poetry run streamlit run streamlit_chat.py
   ```

   The chat interface will be available at: http://localhost:8501

## 🔧 API Endpoints

### Core Endpoints

- **`POST /api/v1/chat`** - Main conversational interface
- **`GET /api/v1/health`** - System health check
- **`POST /api/v1/rag`** - Direct RAG queries
- **`POST /api/v1/sql`** - Direct SQL queries
- **`GET /api/v1/sql/schema`** - Database schema information

### Session Management

- **`POST /api/v1/chat/feedback`** - Submit feedback
- **`GET /api/v1/chat/session/{session_id}`** - Get session stats

## 🧠 Features

### Intelligent Query Routing
- **RAG Mode**: For conceptual questions and explanations
- **SQL Mode**: For data queries and analytics
- **Hybrid Mode**: For complex questions requiring both approaches
- **Auto-Detection**: System automatically chooses the best approach

### Session Management
- Conversation history tracking
- Context-aware responses
- User preference learning
- Session cleanup and management

### Simple UI
- Clean Streamlit interface
- No mode selection required
- Real-time backend communication
- Example questions provided

## 📊 Architecture Benefits

### Clean Separation of Concerns
- **API Layer**: HTTP endpoints and request handling
- **Business Logic**: Core services and algorithms
- **Data Layer**: Database models and connections
- **Configuration**: Centralized settings management

### Scalability
- Modular design allows easy feature additions
- Clear service boundaries enable independent scaling
- Proper dependency injection patterns

### Maintainability
- Well-organized folder structure
- Comprehensive type hints and documentation
- Standardized error handling
- Consistent coding patterns

## 🛠️ Configuration

Key settings can be configured via environment variables:

```bash
# Server Configuration
HOST=127.0.0.1
PORT=8000
DEBUG=false

# Database
DATABASE_PATH=database/Northwind.db

# LLM Configuration
LLM_MODEL=deepseek-coder
LLM_TEMPERATURE=0.1

# RAG Configuration
MAX_RETRIEVED_DOCS=5
SIMILARITY_THRESHOLD=0.7
```

## 🔍 Development

### Code Quality
- Type hints throughout the codebase
- Comprehensive error handling
- Detailed logging and monitoring
- Clean architecture patterns

### Testing
- Health check endpoints for monitoring
- Proper exception handling
- Service isolation for unit testing

## 📈 Performance

- Async/await patterns for I/O operations
- Efficient vector storage and retrieval
- Connection pooling and resource management
- Optimized query routing algorithms

## 🎉 What's Been Improved

1. **Simplified Frontend**: Removed complex UI, kept only clean Streamlit chat
2. **Professional Structure**: Follows FastAPI best practices
3. **Better Organization**: Clear separation of API, business logic, and data
4. **Centralized Configuration**: All settings in one place
5. **Improved Error Handling**: Custom exceptions and proper HTTP responses
6. **Type Safety**: Comprehensive Pydantic schemas
7. **Documentation**: Clear API docs and code comments
8. **Maintainability**: Modular design for easy updates

## 🚀 Ready to Use!

Your DeepSeek RAG Chatbot is now professionally organized and ready for production use!

- **Backend**: http://127.0.0.1:8000 (API Documentation at /docs)
- **Frontend**: http://localhost:8501 (Simple chat interface)

Just ask any question and the AI will automatically choose the best approach to help you! 🤖✨