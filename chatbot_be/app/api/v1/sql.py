"""
SQL endpoints for database queries.
Direct access to database operations and data analysis.
"""

from fastapi import APIRouter, HTTPException
import time
import logging

from app.schemas.sql import SQLRequest, SQLResponse, DatabaseSchemaResponse
from app.models.database import database
from app.core.exceptions import SQLServiceException

router = APIRouter(tags=["SQL"])
logger = logging.getLogger(__name__)

@router.post("/sql", response_model=SQLResponse)
async def ask_sql_question(request: SQLRequest):
    """
    Ask a natural language question that will be converted to SQL.
    Returns both the results and optionally the generated SQL query.
    """
    try:
        start_time = time.time()
        
        # TODO: Import and use SQL agent once moved
        # For now, return a placeholder implementation
        
        # Simple example query for testing
        if "count" in request.question.lower() and "product" in request.question.lower():
            sql_query = "SELECT COUNT(*) as count FROM Products"
            results = database.execute_query(sql_query)
            
            answer = f"Found {results[0]['count']} products in the database."
            columns = ["count"]
            
        else:
            # Fallback for other questions
            sql_query = "SELECT COUNT(*) as total_tables FROM sqlite_master WHERE type='table'"
            results = database.execute_query(sql_query)
            answer = "SQL endpoint is being reorganized. Please try asking about product counts for now."
            columns = ["total_tables"]
        
        execution_time = time.time() - start_time
        
        return SQLResponse(
            answer=answer,
            data=results,
            sql_query=sql_query if request.return_sql else None,
            row_count=len(results),
            execution_time=execution_time,
            columns=columns
        )
        
    except Exception as e:
        logger.error(f"SQL endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sql/schema", response_model=DatabaseSchemaResponse)
async def get_database_schema():
    """
    Get the database schema information.
    Returns table names, columns, and basic statistics.
    """
    try:
        tables = database.get_all_tables()
        table_info = []
        
        for table_name in tables:
            # Get table schema
            schema = database.get_table_schema(table_name)
            columns = [col['name'] for col in schema]
            
            # Get row count
            count_query = f"SELECT COUNT(*) as count FROM {table_name}"
            count_result = database.execute_query(count_query)
            row_count = count_result[0]['count'] if count_result else 0
            
            table_info.append({
                "name": table_name,
                "columns": columns,
                "row_count": row_count
            })
        
        return DatabaseSchemaResponse(
            tables=table_info,
            total_tables=len(tables),
            database_name="Northwind"
        )
        
    except Exception as e:
        logger.error(f"Schema endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sql/health")
async def sql_health_check():
    """
    Check the health status of the SQL service.
    """
    try:
        # Test database connection
        tables = database.get_all_tables()
        
        return {
            "status": "healthy",
            "message": "SQL service is ready",
            "database_connected": True,
            "tables_available": len(tables)
        }
        
    except Exception as e:
        logger.error(f"SQL health check error: {str(e)}")
        return {"status": "error", "message": str(e)}