"""
session_manager.py
Manages conversation sessions and maintains context across multiple interactions.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid

class ConversationSession:
    """
    Represents a single conversation session with a user.
    Stores conversation history, context, and user intent.
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        
        # Store conversation history - list of (question, answer, metadata) tuples
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Track what the user is currently exploring
        self.current_context = {
            "topic": None,          # e.g., "products", "customers", "orders"
            "intent": None,         # e.g., "browsing", "counting", "comparing"
            "entities": [],         # e.g., ["beverages", "dairy products"]
            "last_query_type": None # e.g., "RAG", "SQL"
        }
        
        # Store any clarifications needed
        self.pending_clarifications: List[str] = []
    
    def add_interaction(self, question: str, answer: str, query_type: str, metadata: Dict[str, Any] = None):
        """
        Add a new question-answer pair to the conversation history.
        
        Args:
            question: User's question
            answer: System's response
            query_type: Type of query used ("RAG" or "SQL")
            metadata: Additional context like retrieved documents, SQL query, etc.
        """
        self.last_activity = datetime.now()
        
        interaction = {
            "timestamp": self.last_activity,
            "question": question,
            "answer": answer,
            "query_type": query_type,
            "metadata": metadata or {}
        }
        
        self.conversation_history.append(interaction)
        
        # Update current context based on the interaction
        self._update_context(question, query_type, metadata)
    
    def _update_context(self, question: str, query_type: str, metadata: Dict[str, Any]):
        """
        Update the current conversation context based on the latest interaction.
        This helps maintain continuity in the conversation.
        """
        question_lower = question.lower()
        
        # Detect topic from question
        if any(word in question_lower for word in ["product", "item", "food", "beverage"]):
            self.current_context["topic"] = "products"
        elif any(word in question_lower for word in ["customer", "client", "buyer"]):
            self.current_context["topic"] = "customers"
        elif any(word in question_lower for word in ["order", "purchase", "sale"]):
            self.current_context["topic"] = "orders"
        
        # Detect intent from question
        if any(word in question_lower for word in ["how many", "count", "total", "number"]):
            self.current_context["intent"] = "counting"
        elif any(word in question_lower for word in ["compare", "difference", "versus", "vs"]):
            self.current_context["intent"] = "comparing"
        elif any(word in question_lower for word in ["list", "show", "what", "which"]):
            self.current_context["intent"] = "browsing"
        
        # Store the query type used
        self.current_context["last_query_type"] = query_type
    
    def get_conversation_summary(self, last_n: int = 3) -> str:
        """
        Get a summary of the last N interactions for context.
        This is used to provide conversation history to the LLM.
        """
        if not self.conversation_history:
            return "No previous conversation."
        
        # Get the last N interactions
        recent_history = self.conversation_history[-last_n:]
        
        summary_parts = []
        for i, interaction in enumerate(recent_history, 1):
            summary_parts.append(
                f"Q{i}: {interaction['question']}\n"
                f"A{i}: {interaction['answer'][:200]}{'...' if len(interaction['answer']) > 200 else ''}"
            )
        
        return "\n\n".join(summary_parts)
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if the session has expired due to inactivity."""
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)


class SessionManager:
    """
    Manages multiple conversation sessions.
    Handles session creation, retrieval, and cleanup.
    """
    
    def __init__(self):
        # Dictionary to store active sessions: session_id -> ConversationSession
        self.sessions: Dict[str, ConversationSession] = {}
    
    def create_session(self) -> str:
        """
        Create a new conversation session.
        
        Returns:
            str: Unique session ID
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = ConversationSession(session_id)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """
        Retrieve a conversation session by ID.
        
        Args:
            session_id: The session identifier
            
        Returns:
            ConversationSession or None if not found/expired
        """
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session is expired
        if session.is_expired():
            del self.sessions[session_id]
            return None
        
        return session
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions to free up memory."""
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.is_expired()
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> tuple[str, ConversationSession]:
        """
        Get an existing session or create a new one.
        
        Args:
            session_id: Optional existing session ID
            
        Returns:
            tuple: (session_id, session_object)
        """
        if session_id:
            session = self.get_session(session_id)
            if session:
                return session_id, session
        
        # Create new session if none exists or expired
        new_session_id = self.create_session()
        return new_session_id, self.sessions[new_session_id]

# Global session manager instance
session_manager = SessionManager()