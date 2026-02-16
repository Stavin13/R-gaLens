
import sys
import os
import re
import json
from sqlalchemy import inspect

# Add backend to path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.core import models

def search_all_db():
    # Comprehensive set of variations including diacritics
    terms_map = {
        "Marga": [r"Ma?arga[ms]?", r"Maarga[mh]?", r"Mārg[am]?", "मार्ग"],
        "Desi": [r"Des[ih]i", r"De[sś]ya[ms]?", r"Deś[ia]m?", "देशी", "देसी"],
        "Raagas": [r"Ra?aga[ms]?", r"Ra?ag\b", r"Ra?agam", r"Ra?agah", r"Rāga[ms]?", "राग"],
        "Taala": [r"Ta?ala[ms]?", r"Ta?al\b", r"Ta?alam", r"Ta?alah", r"Tāla[ms]?", "ताल"],
        "Prabandha": [r"Prabandha[ms]?", r"Prabandh\b", r"Prabandha[mh]?", "प्रबन्ध", "प्रबंध"],
        "Vaadya": [r"Va?adya[ms]?", r"Va?adya\b", r"Vādya[ms]?", "वाद्य"]
    }
    
    db = SessionLocal()
    try:
        inspector = inspect(db.bind)
        all_tables = [models.Document, models.NLPResult, models.Event, models.Timeline]
        
        results = {cat: [] for cat in terms_map}
        
        for category, patterns in terms_map.items():
            combined_pattern = "|".join(patterns)
            regex = re.compile(combined_pattern, re.IGNORECASE)
            
            for table_class in all_tables:
                table_name = table_class.__tablename__
                rows = db.query(table_class).all()
                
                for row in rows:
                    # Search all columns in the row
                    row_data = {c.key: getattr(row, c.key) for c in inspect(row).mapper.column_attrs}
                    
                    found_in_row = False
                    context = ""
                    matched_val = ""
                    
                    for col, val in row_data.items():
                        if val is None:
                            continue
                        
                        str_val = str(val)
                        match = regex.search(str_val)
                        if match:
                            found_in_row = True
                            matched_val = match.group()
                            # Get some context around the match
                            start = max(0, match.start() - 50)
                            end = min(len(str_val), match.end() + 50)
                            context = f"{col}: ...{str_val[start:end]}..."
                            break
                    
                    if found_in_row:
                        # Get a friendly name for the document if possible
                        doc_name = "N/A"
                        if hasattr(row, 'document') and row.document:
                            doc_name = row.document.filename
                        elif table_name == 'documents':
                            doc_name = row.filename
                        elif hasattr(row, 'document_id'):
                            doc = db.query(models.Document).filter(models.Document.id == row.document_id).first()
                            if doc:
                                doc_name = doc.filename
                                
                        results[category].append({
                            "table": table_name,
                            "id": row.id,
                            "doc": doc_name,
                            "matched": matched_val,
                            "context": context
                        })
        
        # Output results
        print("\n=== EXHAUSTIVE DATABASE SEARCH RESULTS ===\n")
        for category, hits in results.items():
            print(f"Category: {category} ({len(hits)} hits)")
            if not hits:
                print("  No matches found.\n")
                continue
            
            # Group by doc for better reading
            doc_groups = {}
            for hit in hits:
                if hit['doc'] not in doc_groups:
                    doc_groups[hit['doc']] = []
                doc_groups[hit['doc']].append(hit)
            
            for doc, items in doc_groups.items():
                print(f"  - Document: {doc}")
                for item in items:
                    print(f"    [{item['table']} ID {item['id']}] Matched '{item['matched']}': {item['context']}")
            print("")
            
    finally:
        db.close()

if __name__ == "__main__":
    search_all_db()
