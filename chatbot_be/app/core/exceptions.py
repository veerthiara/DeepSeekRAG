"""
Custom exceptions for the DeepSeek RAG Chatbot.
Centralized exception handling for better error management.
"""

from typing import Optional, Dict, Any

class ChatbotBaseException(Exception):
    """Base exception for all chatbot-related errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class RAGServiceException(ChatbotBaseException):
    """Raised when RAG service encounters an error."""
    pass

class SQLServiceException(ChatbotBaseException):
    """Raised when SQL service encounters an error."""
    pass

class SessionException(ChatbotBaseException):
    """Raised when session management encounters an error."""
    pass

class QueryRoutingException(ChatbotBaseException):
    """Raised when query routing encounters an error."""
    pass

class VectorStoreException(ChatbotBaseException):
    """Raised when vector store operations fail."""
    pass

class LLMException(ChatbotBaseException):
    """Raised when LLM operations fail."""
    pass