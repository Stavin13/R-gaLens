from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
import os
import shutil
import uuid
import json
from app.api.dependencies import get_db
from app.core import models
from app.core.config import settings
from app.services.pdf_service import pdf_processor
from app.services.nlp_service import nlp_orchestrator
from app.utils.logger import logger

router = APIRouter()

async def process_document_task(doc_id: int, file_path: str, db: Session):
    try:
        # Update status
        doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
        doc.status = "processing"
        db.commit()

        # 1. PDF Processing
        pdf_data = pdf_processor.process_pdf(file_path)
        
        # 2. NLP Analysis
        nlp_data = nlp_orchestrator.process_document(pdf_data["full_text"])
        
        # 3. Store NLP Results
        nlp_result = models.NLPResult(
            document_id=doc_id,
            entities=nlp_data["entities"],
            events_raw=nlp_data["events"],
            summary=nlp_data["summary"],
            topics=nlp_data["topics"]
        )
        db.add(nlp_result)
        
        # 4. Store Events
        for e in nlp_data["events"]:
            # Basic event construction from NLP data
            # In a real app, you'd extract more specific fields
            event = models.Event(
                document_id=doc_id,
                title=f"Event in {doc.filename}",
                description=e["sentence"],
                date_str="Unknown", # Heuristic needed
                normalized_date=None,
                event_type=e["type"],
                confidence=e["confidence"],
                entities=nlp_data["entities"],
                sentence=e["sentence"]
            )
            db.add(event)
        
        # Update Document
        doc.decade = nlp_data["decade"]
        doc.status = "processed"
        db.commit()
        logger.info(f"Successfully processed document {doc_id}")

    except Exception as e:
        logger.error(f"Error processing document {doc_id}: {e}")
        doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
        if doc:
            doc.status = "failed"
            db.commit()

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_doc = models.Document(
        filename=file.filename,
        path=file_path,
        status="uploaded"
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    background_tasks.add_task(process_document_task, db_doc.id, file_path, db)

    return {"id": db_doc.id, "filename": db_doc.filename, "status": db_doc.status}

@router.get("/")
async def list_documents(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    docs = db.query(models.Document).offset(skip).limit(limit).all()
    return docs

@router.get("/{id}")
async def get_document(id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.get("/{id}/nlp")
async def get_document_nlp(id: int, db: Session = Depends(get_db)):
    nlp = db.query(models.NLPResult).filter(models.NLPResult.document_id == id).first()
    if not nlp:
        raise HTTPException(status_code=404, detail="NLP results not found")
    return nlp
