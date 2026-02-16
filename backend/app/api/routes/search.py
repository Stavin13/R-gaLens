from fastapi import APIRouter
from app.services.search_service import semantic_search

router = APIRouter()

@router.get("/search")
async def search(query: str):
    results = semantic_search.search(query)
    return {"query": query, "results": results}
