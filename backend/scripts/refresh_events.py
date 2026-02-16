import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core import models
from app.core.database import SessionLocal
from app.services.pdf_service import pdf_processor
from app.services.nlp_service import nlp_orchestrator
from app.utils.logger import logger
from tqdm import tqdm

async def refresh_events():
    db = SessionLocal()
    try:
        # Get all processed documents
        docs = db.query(models.Document).filter(models.Document.status == "processed").all()
        logger.info(f"Refreshing events for {len(docs)} documents...")

        for doc in tqdm(docs):
            if not os.path.exists(doc.path):
                logger.warning(f"File not found: {doc.path}")
                continue

            # 1. Re-extract text
            pdf_data = pdf_processor.process_pdf(doc.path)
            
            # 2. Run event detection (now scanning 100 sentences)
            nlp_data = nlp_orchestrator.process_document(pdf_data["full_text"])
            
            # 3. Clear old events for this doc
            db.query(models.Event).filter(models.Event.document_id == doc.id).delete()
            
            # 4. Insert new events
            logger.info(f"Found {len(nlp_data['events'])} events for {doc.filename}")
            for e in nlp_data["events"]:
                event = models.Event(
                    document_id=doc.id,
                    title=f"Event in {doc.filename}",
                    description=e["sentence"],
                    date_str="Detected via NLP",
                    event_type=e["type"],
                    confidence=e["confidence"],
                    entities=nlp_data["entities"],
                    sentence=e["sentence"]
                )
                db.add(event)
            
            db.commit()
            
        logger.info("Events refreshed successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(refresh_events())
