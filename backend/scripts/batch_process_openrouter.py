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

async def batch_process_docs(batch_size=10, delay=2, force=False, start_index=0, limit=None):
    """
    Processes documents in the database.
    batch_size: Number of documents to process before a short pause.
    delay: Seconds to wait between batches.
    force: If True, re-processes documents regardless of status.
    start_index: Index to start from in the document list.
    limit: Maximum number of documents to process.
    """
    db = SessionLocal()
    try:
        if force:
            docs = db.query(models.Document).order_by(models.Document.id).all()
            logger.info(f"🚀 FORCED re-processing of all {len(docs)} documents...")
        else:
            docs = db.query(models.Document).filter(models.Document.status != "processed").order_by(models.Document.id).all()
            logger.info(f"🚀 Starting batch processing for {len(docs)} (unprocessed) documents...")

        # Apply start index and limit
        total_available = len(docs)
        docs = docs[start_index:]
        if limit is not None:
            docs = docs[:limit]
            
        if not docs:
            logger.info("Nothing to process.")
            return
            
        logger.info(f"Processing docs {start_index + 1} to {start_index + len(docs)} (Total available: {total_available})")

        count = 0
        for doc in tqdm(docs):
            if not os.path.exists(doc.path):
                logger.warning(f"File not found: {doc.path}")
                continue

            try:
                # 1. Extract text (OCR if needed)
                logger.info(f"Extracting text from: {doc.filename}")
                pdf_data = pdf_processor.process_pdf(doc.path)
                
                # 2. Run new LLM Analysis
                logger.info(f"Analyzing with LLM (Groq/OpenRouter): {doc.filename}")
                nlp_data = nlp_orchestrator.process_document(pdf_data["full_text"])
                
                # 3. Update NLP Results
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
                db.query(models.Event).filter(models.Event.document_id == doc.id).delete()
                
                for e in nlp_data["events"]:
                    event = models.Event(
                        document_id=doc.id,
                        title=f"Event in {doc.filename}",
                        description=e.get("sentence", "No description"),
                        date_str="Detected via LLM",
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
                
                if count % batch_size == 0:
                    logger.info(f"Batch of {batch_size} completed. Resting for {delay}s...")
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Failed to process {doc.filename}: {e}")
                db.rollback()
                continue
                
        logger.info(f"✅ Finished! Successfully processed {count} documents.")
        
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Batch process documents via LLM")
    parser.add_argument("--batch", type=int, default=10, help="Batch size")
    parser.add_argument("--delay", type=int, default=2, help="Delay between batches")
    parser.add_argument("--force", action="store_true", help="Re-process all documents")
    parser.add_argument("--start", type=int, default=0, help="Start index")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of docs")
    args = parser.parse_args()
    
    asyncio.run(batch_process_docs(
        batch_size=args.batch, 
        delay=args.delay, 
        force=args.force, 
        start_index=args.start, 
        limit=args.limit
    ))
