"""
customers.py
Router for customer-related endpoints.
"""

from fastapi import APIRouter, HTTPException
from chatbot_be.db import get_db_pool

router = APIRouter(prefix="/customers", tags=["customers"])

@router.get("/", summary="List all customers")
async def list_customers():
    """
    Fetch a list of customers from the Northwind database.
    Returns:
        List[dict]: List of customer records.
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch("SELECT customer_id, company_name, contact_name FROM customers LIMIT 20;")
            return [dict(row) for row in rows]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
