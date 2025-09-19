"""
Request and response schemas for chat interactions.
Defines the data structures for conversational AI endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class ChatRequest(BaseModel):
    """Request model for chat interactions."""
    question: str = Field(..., description="User's question or message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    user_preferences: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="User preferences for response style, length, etc."
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "How many products do we have?",
                "session_id": "abc123",
                "user_preferences": {"response_detail": "balanced"}
            }
        }

class ChatResponse(BaseModel):
    """Response model for chat interactions."""
    answer: str = Field(..., description="AI's response to the user's question")
    confidence: float = Field(..., description="Confidence score (0-1) for the response")
    query_type_used: str = Field(..., description="Type of processing used (RAG/SQL/HYBRID/CLARIFICATION)")
    session_id: str = Field(..., description="Session ID for this conversation")
    reasoning: str = Field(..., description="Explanation of why this approach was chosen")
    sources: List[str] = Field(..., description="Sources used to generate the response")
    sql_query: Optional[str] = Field(None, description="SQL query used (if applicable)")
    suggested_followups: List[str] = Field(..., description="Suggested follow-up questions")
    clarification_needed: Optional[str] = Field(None, description="Clarification request if question is ambiguous")
    conversation_summary: str = Field(..., description="Summary of recent conversation")
    timestamp: str = Field(..., description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "We have 77 products in our database.",
                "confidence": 0.95,
                "query_type_used": "SQL",
                "session_id": "abc123",
                "reasoning": "Question requires specific data count",
                "sources": ["Northwind database"],
                "sql_query": "SELECT COUNT(*) FROM Products",
                "suggested_followups": ["What categories do we have?", "Show me top products"],
                "clarification_needed": None,
                "conversation_summary": "User asked about product count",
                "timestamp": "2025-09-18T10:30:00Z"
            }
        }