from fastapi import APIRouter

router = APIRouter()

@router.get("/stats")
async def get_analysis_stats():
    return {"message": "Analysis stats endpoint stub"}
