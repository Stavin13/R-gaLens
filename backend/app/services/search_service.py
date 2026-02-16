from app.utils.logger import logger
from app.core.database import SessionLocal
from app.core import models
from sqlalchemy import or_

class SemanticSearch:
    def search(self, query: str, limit: int = 20) -> dict:
        logger.info(f"Searching for: {query}")
        
        db = SessionLocal()
        try:
            # 1. First, search for Events (specific historical items)
            event_results = db.query(models.Event).filter(
                or_(
                    models.Event.description.ilike(f"%{query}%"),
                    models.Event.sentence.ilike(f"%{query}%"),
                    models.Event.title.ilike(f"%{query}%")
                )
            ).limit(limit).all()

            # 2. Also search NLPResults (summaries and topics)
            nlp_results = db.query(models.NLPResult).filter(
                or_(
                    models.NLPResult.summary.ilike(f"%{query}%"),
                    models.NLPResult.entities.astext.ilike(f"%{query}%") if "postgres" in str(db.bind.url) else models.NLPResult.entities.ilike(f"%{query}%")
                )
            ).limit(limit).all()

            # 3. Search Document filenames
            doc_results = db.query(models.Document).filter(
                models.Document.filename.ilike(f"%{query}%")
            ).limit(limit).all()

            # Combine and format to match ChromaDB structure
            ids = []
            documents = []
            metadatas = []
            
            # Process Events
            for event in event_results:
                ids.append(f"event_{event.id}")
                documents.append(event.description or event.sentence)
                metadatas.append({
                    "title": event.document.filename if event.document else "Unknown",
                    "author": "Music Academy Journal",
                    "year": str(event.document.decade) if event.document and event.document.decade else "Unknown",
                    "type": "Event"
                })

            # Process NLP Results (if not already included via events)
            for nlp in nlp_results:
                if f"nlp_{nlp.id}" not in ids:
                    ids.append(f"nlp_{nlp.id}")
                    documents.append(nlp.summary)
                    metadatas.append({
                        "title": nlp.document.filename if nlp.document else "Unknown",
                        "author": "Music Academy Journal",
                        "year": str(nlp.document.decade) if nlp.document and nlp.document.decade else "Unknown",
                        "type": "Journal Summary"
                    })

            # Process Doc results
            for doc in doc_results:
                if f"doc_{doc.id}" not in ids:
                    ids.append(f"doc_{doc.id}")
                    documents.append(f"Journal Archive: {doc.filename}")
                    metadatas.append({
                        "title": doc.filename,
                        "author": "Music Academy",
                        "year": str(doc.decade) if doc.decade else "Unknown",
                        "type": "Document"
                    })

            return {
                "ids": [ids],
                "documents": [documents],
                "metadatas": [metadatas]
            }
        finally:
            db.close()

semantic_search = SemanticSearch()
