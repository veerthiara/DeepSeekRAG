"""
Schemas for RAG (Retrieval Augmented Generation) operations.
Defines data structures for document retrieval and knowledge queries.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class RAGRequest(BaseModel):
    """Request model for RAG queries."""
    question: str = Field(..., description="Question to answer using RAG")
    max_docs: Optional[int] = Field(5, ge=1, le=20, description="Maximum number of documents to retrieve")
    include_sources: bool = Field(True, description="Whether to include source information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the company's product strategy?",
                "max_docs": 5,
                "include_sources": True
            }
        }

class RAGResponse(BaseModel):
    """Response model for RAG queries."""
    answer: str = Field(..., description="Generated answer based on retrieved documents")
    sources: List[str] = Field(..., description="Source documents used")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score for the answer")
    retrieved_docs: int = Field(..., description="Number of documents retrieved")
    processing_time: float = Field(..., description="Processing time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "The company focuses on quality products across multiple categories...",
                "sources": ["Product catalog", "Company handbook"],
                "confidence": 0.85,
                "retrieved_docs": 3,
                "processing_time": 1.2
            }
        }

class DocumentUploadRequest(BaseModel):
    """Request model for uploading documents to the vector store."""
    content: str = Field(..., description="Text content of the document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    source: str = Field(..., description="Source identifier for the document")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "This document contains important company information...",
                "metadata": {"category": "policy", "date": "2025-09-18"},
                "source": "company_handbook.pdf"
            }
        }