from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.core import models
from app.services.nlp_service import nlp_orchestrator
from app.utils.logger import logger
import json

router = APIRouter()

@router.get("/stats")
async def get_analysis_stats(db: Session = Depends(get_db)):
    doc_count = db.query(models.Document).count()
    processed_count = db.query(models.Document).filter(models.Document.status == "processed").count()
    event_count = db.query(models.Event).count()
    return {
        "total_documents": doc_count,
        "processed_documents": processed_count,
        "total_events": event_count
    }

@router.get("/synthesis")
async def get_research_synthesis(term: str, db: Session = Depends(get_db)):
    """
    Generate a rigorous academic synthesis for a specific term (e.g., Marga, Raagas).
    """
    logger.info(f"API Request for research synthesis of: {term}")
    
    # 1. Fetch available NLP results
    results = db.query(models.NLPResult).join(models.Document).all()
    
    if not results:
        raise HTTPException(status_code=404, detail="No NLP results found. Please process documents first.")

    # 2. Group by decade and find year range
    decade_data = {}
    years = []
    for res in results:
        decade = res.document.decade
        if not decade:
            continue
        
        years.append(decade)
        decade_str = f"{decade}s"
        if decade_str not in decade_data:
            decade_data[decade_str] = []
        
        if res.summary:
            decade_data[decade_str].append(res.summary)

    if not decade_data:
        raise HTTPException(status_code=400, detail="No decade-tagged summaries found in database.")

    start_year = min(years)
    end_year = max(years) + 9

    # 3. Call synthesis
    try:
        final_report = nlp_orchestrator.synthesize_research(
            term=term, 
            start_year=start_year, 
            end_year=end_year, 
            decade_data=decade_data
        )
        return final_report
    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
