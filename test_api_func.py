import asyncio
from api import process_query, QueryRequest
import os

# Mock the FastAPI request
async def test():
    req = QueryRequest(query="Marga vs Desi", top_k=5)
    try:
        response = await process_query(req)
        print("Response received successfully!")
        print(response["answer"][:200] + "...")
    except Exception as e:
        print(f"Error in process_query: {e}")

if __name__ == "__main__":
    asyncio.run(test())
