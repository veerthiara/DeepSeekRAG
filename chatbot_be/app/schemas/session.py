"""
Schemas for session management and feedback.
Defines data structures for user sessions and feedback collection.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class SessionStatsResponse(BaseModel):
    """Response model for session statistics."""
    session_id: str = Field(..., description="Unique session identifier")
    created_at: str = Field(..., description="Session creation timestamp")
    last_activity: str = Field(..., description="Last activity timestamp")
    total_interactions: int = Field(..., description="Total number of interactions")
    query_types_used: Dict[str, int] = Field(..., description="Count of each query type used")
    user_preferences: Dict[str, Any] = Field(..., description="User preferences for this session")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc123",
                "created_at": "2025-09-18T10:00:00Z",
                "last_activity": "2025-09-18T10:30:00Z",
                "total_interactions": 5,
                "query_types_used": {"SQL": 3, "RAG": 2},
                "user_preferences": {"response_detail": "balanced"}
            }
        }

class FeedbackRequest(BaseModel):
    """Request model for user feedback on responses."""
    session_id: str = Field(..., description="Session ID for the interaction")
    interaction_id: str = Field(..., description="Specific interaction being rated")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 (poor) to 5 (excellent)")
    feedback_text: Optional[str] = Field(None, description="Optional text feedback")
    helpful: bool = Field(..., description="Whether the response was helpful")
    category: Optional[str] = Field(None, description="Category of feedback (accuracy, clarity, etc.)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc123",
                "interaction_id": "int456",
                "rating": 4,
                "feedback_text": "Good answer but could be more detailed",
                "helpful": True,
                "category": "clarity"
            }
        }

class FeedbackResponse(BaseModel):
    """Response model after submitting feedback."""
    success: bool = Field(..., description="Whether feedback was recorded successfully")
    message: str = Field(..., description="Confirmation message")
    feedback_id: str = Field(..., description="Unique identifier for this feedback")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Thank you for your feedback!",
                "feedback_id": "fb789"
            }
        }