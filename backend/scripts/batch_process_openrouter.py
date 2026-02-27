import asyncio
import sys
import os
import time
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core import models
from app.core.database import SessionLocal
from app.services.pdf_service import pdf_processor
from app.services.nlp_service import nlp_orchestrator
from app.utils.logger import logger
from tqdm import tqdm

async def batch_process_docs(batch_size=5, delay=2):
    """
    Processes all documents in the database using the new OpenRouter pipeline.
    batch_size: Number of documents to process before a short pause.
    delay: Seconds to wait between batches.
    """
    db = SessionLocal()
    try:
        # Get all documents
        # We can filter by status if we want to skip already processed ones, 
        # but for "training" on current DB, we might want to re-process.
        docs = db.query(models.Document).all()
        logger.info(f"🚀 Starting batch processing for {len(docs)} documents using OpenRouter...")

        count = 0
        for doc in tqdm(docs):
            if not os.path.exists(doc.path):
                logger.warning(f"File not found: {doc.path}")
                continue

            try:
                # 1. Extract text (OCR if needed)
                logger.info(f"Extracting text from: {doc.filename}")
                pdf_data = pdf_processor.process_pdf(doc.path)
                
                # 2. Run new OpenRouter NLP Analysis
                # This performs summarization, entity extraction, and event detection
                logger.info(f"Analyzing with OpenRouter: {doc.filename}")
                nlp_data = nlp_orchestrator.process_document(pdf_data["full_text"])
                
                # 3. Update NLP Results
                # Clear old results for this doc
                db.query(models.NLPResult).filter(models.NLPResult.document_id == doc.id).delete()
                
                nlp_result = models.NLPResult(
                    document_id=doc.id,
                    entities=nlp_data["entities"],
                    events_raw=nlp_data["events"],
                    summary=nlp_data["summary"],
                    topics=nlp_data["topics"]
                )
                db.add(nlp_result)
                
                # 4. Update Events
                # Clear old events
                db.query(models.Event).filter(models.Event.document_id == doc.id).delete()
                
                for e in nlp_data["events"]:
                    event = models.Event(
                        document_id=doc.id,
                        title=f"Event in {doc.filename}",
                        description=e.get("sentence", "No description"),
                        date_str="Detected via OpenRouter",
                        event_type=e.get("type", "event"),
                        confidence=e.get("confidence", 0.0),
                        entities=nlp_data["entities"],
                        sentence=e.get("sentence", "")
                    )
                    db.add(event)
                
                # 5. Update Doc metadata
                doc.decade = nlp_data.get("decade")
                doc.status = "processed"
                
                db.commit()
                count += 1
                
                # Chunking delay logic
                if count % batch_size == 0:
                    logger.info(f"Batch of {batch_size} completed. Resting for {delay}s...")
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Failed to process {doc.filename}: {e}")
                db.rollback()
                continue
                
        logger.info(f"✅ Finished! Successfully re-processed {count} documents.")
        
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Batch process documents via OpenRouter")
    parser.add_argument("--batch", type=int, default=5, help="Batch size")
    parser.add_argument("--delay", type=int, default=2, help="Delay between batches")
    args = parser.parse_args()
    
    asyncio.run(batch_process_docs(batch_size=args.batch, delay=args.delay))
