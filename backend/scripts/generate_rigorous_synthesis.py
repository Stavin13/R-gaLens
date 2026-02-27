import json
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core import models
from app.core.database import SessionLocal
from app.services.nlp_service import nlp_orchestrator
from app.utils.logger import logger

def generate_rigorous_synthesis(term="Marga"):
    db = SessionLocal()
    try:
        # 1. Fetch available NLP results
        results = db.query(models.NLPResult).join(models.Document).all()
        logger.info(f"Fetched {len(results)} NLP results for synthesis.")

        if not results:
            logger.warning("No NLP results found in database. Please run batch processing first.")
            return

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
            logger.warning("No decade-tagged summaries found.")
            return

        start_year = min(years)
        end_year = max(years) + 9

        # 3. Call synthesis with the specific pattern
        final_report = nlp_orchestrator.synthesize_research(
            term=term, 
            start_year=start_year, 
            end_year=end_year, 
            decade_data=decade_data
        )

        # 4. Save and Output
        output_file = f"backend/data/{term.lower()}_rigorous_synthesis.json"
        with open(output_file, "w") as f:
            json.dump(final_report, f, indent=2)
        
        logger.info(f"✅ Rigorous Synthesis complete! Saved to {output_file}")
        print(json.dumps(final_report, indent=2))

    finally:
        db.close()

if __name__ == "__main__":
    primary_terms = ["Marga", "Raagas", "Taala", "Prabandha", "Desi", "Vaadya"]
    
    # If a specific term is provided as argument, just do that one
    if len(sys.argv) > 1:
        target_terms = [sys.argv[1]]
    else:
        target_terms = primary_terms

    for term in target_terms:
        logger.info(f"--- Synthesizing {term} ---")
        generate_rigorous_synthesis(term)
