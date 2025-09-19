"""
Schemas for SQL operations and database queries.
Defines data structures for database interactions and data analysis.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union

class SQLRequest(BaseModel):
    """Request model for SQL queries."""
    question: str = Field(..., description="Natural language question to convert to SQL")
    return_sql: bool = Field(False, description="Whether to return the generated SQL query")
    limit: Optional[int] = Field(100, ge=1, le=1000, description="Maximum number of rows to return")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Show me the top 5 products by price",
                "return_sql": True,
                "limit": 5
            }
        }

class SQLResponse(BaseModel):
    """Response model for SQL queries."""
    answer: str = Field(..., description="Natural language answer based on query results")
    data: List[Dict[str, Any]] = Field(..., description="Query results as list of dictionaries")
    sql_query: Optional[str] = Field(None, description="Generated SQL query (if requested)")
    row_count: int = Field(..., description="Number of rows returned")
    execution_time: float = Field(..., description="Query execution time in seconds")
    columns: List[str] = Field(..., description="Column names in the result set")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Here are the top 5 products by price:",
                "data": [
                    {"ProductName": "Product A", "Price": 100.00},
                    {"ProductName": "Product B", "Price": 95.00}
                ],
                "sql_query": "SELECT ProductName, Price FROM Products ORDER BY Price DESC LIMIT 5",
                "row_count": 5,
                "execution_time": 0.05,
                "columns": ["ProductName", "Price"]
            }
        }

class DatabaseSchemaResponse(BaseModel):
    """Response model for database schema information."""
    tables: List[Dict[str, Any]] = Field(..., description="List of tables and their schemas")
    total_tables: int = Field(..., description="Total number of tables")
    database_name: str = Field(..., description="Name of the database")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tables": [
                    {
                        "name": "Products",
                        "columns": ["ProductID", "ProductName", "Price"],
                        "row_count": 77
                    }
                ],
                "total_tables": 8,
                "database_name": "Northwind"
            }
        }