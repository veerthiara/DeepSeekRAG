"""
Core application configuration.
Centralized configuration management for the DeepSeek RAG Chatbot.
"""

import os

class Settings:
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "DeepSeek RAG Chatbot"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8000"))
    reload: bool = os.getenv("RELOAD", "true").lower() == "true"
    
    # Database - PostgreSQL in Docker
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "northwind")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "postgres")
    
    @property
    def database_url(self) -> str:
        """Construct PostgreSQL database URL."""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    # Vector Store
    vector_store_path: str = os.getenv("VECTOR_STORE_PATH", "data/vector_store")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # LLM Configuration
    llm_model: str = os.getenv("LLM_MODEL", "deepseek-coder")
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "2000"))
    
    # RAG Configuration
    max_retrieved_docs: int = int(os.getenv("MAX_RETRIEVED_DOCS", "5"))
    similarity_threshold: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    
    # Session Management
    session_timeout_minutes: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    max_conversation_history: int = int(os.getenv("MAX_CONVERSATION_HISTORY", "20"))
    
    # CORS
    cors_origins: list = ["http://localhost:8501", "http://127.0.0.1:8501"]
    cors_methods: list = ["GET", "POST", "PUT", "DELETE"]
    cors_headers: list = ["*"]

# Global settings instance
settings = Settings()