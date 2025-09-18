"""
sql.py
Router for LangChain SQL agent-based database question answering.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from chatbot_be.rag.sql_client import ask_sql_agent

router = APIRouter(prefix="/sql", tags=["sql-agent"])

class SQLQuestionRequest(BaseModel):
    question: str

class SQLQuestionResponse(BaseModel):
    question: str
    answer: str

@router.post("/ask", response_model=SQLQuestionResponse, summary="Ask a database question using LangChain SQL agent")
async def ask_sql_question(request: SQLQuestionRequest):
    """
    Ask a question and get an answer from the database using LangChain SQL agent.
    """
    try:
        answer = await ask_sql_agent(request.question)
        return SQLQuestionResponse(question=request.question, answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing SQL agent question: {str(e)}")

@router.get("/health", summary="Check if SQL agent is ready")
async def health_check():
    return {"status": "ready", "service": "LangChain SQL Agent"}
