"""
sql_client.py
LangChain SQL agent for answering database questions using Ollama LLM.
"""

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
import os
import asyncio
from langchain_community.llms import Ollama


# Database connection string for Northwind Postgres (using synchronous psycopg2)
DB_URI = os.getenv("NORTHWIND_DB_URI", "postgresql://postgres:postgres@localhost:5432/northwind")

# Initialize SQLDatabase
sql_db = SQLDatabase.from_uri(DB_URI)

# Use Ollama with a more compatible model for SQL agents
llm = Ollama(model="deepseek-coder")  # This should be more compatible than deepseek-r1
# llm = Ollama(model="llama2")  # Alternative if deepseek-coder still fails

# Create LangChain SQL agent with error handling
agent_executor = create_sql_agent(
    llm=llm,
    db=sql_db,
    verbose=True,
    handle_parsing_errors=True  # This allows the agent to retry on parsing errors
)

async def ask_sql_agent(question: str) -> str:
    """
    Ask a natural language question and get an answer from the database using LangChain SQL agent.
    Args:
        question (str): User's question
    Returns:
        str: Agent's answer
    """
    try:
        # Run the synchronous agent in a thread pool to avoid blocking
        import asyncio
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, agent_executor.run, question)
        return result
    except Exception as e:
        # Log the full error for debugging
        print(f"SQL Agent Error: {str(e)}")
        print(f"Error type: {type(e)}")
        return f"SQL Agent failed: {str(e)}"
