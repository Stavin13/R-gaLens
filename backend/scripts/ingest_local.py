import os
import asyncio
import sys
from pathlib import Path

# Add the backend directory to sys.path so we can import 'app'
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core import models
from app.core.database import SessionLocal, engine
from app.api.routes.documents import process_document_task
from app.core.config import settings
from app.utils.logger import logger
from tqdm import tqdm

async def ingest_files(folder_path: str):
    # Ensure database tables exist
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Get all PDF files in the folder, excluding Mac system files
        files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf") and not f.startswith("._")]
        logger.info(f"Found {len(files)} PDF files in {folder_path}")

        for filename in tqdm(files, desc="Ingesting PDFs"):
            file_path = os.path.abspath(os.path.join(folder_path, filename))
            
            # 1. Check if already exists in DB
            existing = db.query(models.Document).filter(models.Document.filename == filename).first()
            if existing:
                logger.debug(f"Skipping {filename}: Already exists in database.")
                continue

            # 2. Register in DB
            db_doc = models.Document(
                filename=filename,
                path=file_path,
                status="uploaded"
            )
            db.add(db_doc)
            db.commit()
            db.refresh(db_doc)

            # 3. Process immediately
            logger.info(f"Starting processing for {filename}...")
            # Note: since this is a script, we await the task directly
            await process_document_task(db_doc.id, file_path, db)
            
    finally:
        db.close()

if __name__ == "__main__":
    # Default to the uploads directory in the backend structure
    target_folder = os.path.join(os.path.dirname(__file__), "..", "data", "uploads")
    
    # If a path is provided as an argument, use it
    if len(sys.argv) > 1:
        target_folder = sys.argv[1]
    
    folder_abs = os.path.abspath(target_folder)
    if not os.path.exists(folder_abs):
        print(f"Error: Folder {folder_abs} does not exist.")
        sys.exit(1)

    asyncio.run(ingest_files(folder_abs))
