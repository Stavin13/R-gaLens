import os
import faiss
import numpy as np
import pickle
import json
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from tqdm import tqdm

# Config
INDEX_FOLDER = "vector_db"
PDF_FOLDER = "Music Academy Journals"
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
MODEL_NAME = "all-MiniLM-L6-v2"
STATE_FILE = os.path.join(INDEX_FOLDER, "index_state.json")
FAISS_FILE = os.path.join(INDEX_FOLDER, "index.faiss")
METADATA_FILE = os.path.join(INDEX_FOLDER, "metadata.pkl")

# Load embedding model once
print(f"Loading {MODEL_NAME}...")
model = SentenceTransformer(MODEL_NAME)

def extract_text_from_pdf(pdf_path: str) -> List[Dict]:
    """Extracts text from PDF page by page."""
    results = []
    try:
        pages = list(extract_pages(pdf_path))
        for page_num, page_layout in enumerate(pages):
            text = ""
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    text += element.get_text()
            if text.strip():
                results.append({"text": text, "page": page_num + 1})
    except Exception as e:
        print(f"\n[!] Error extracting {os.path.basename(pdf_path)}: {e}")
    return results

def get_chunks(text: str, page: int, filename: str) -> List[Dict]:
    """Generates overlapping chunks from text."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk_text = text[start:end]
        chunks.append({
            "text": chunk_text,
            "filename": filename,
            "page": page,
            "preview": chunk_text[:100].replace("\n", " ").strip() + "..."
        })
        if end >= len(text): break
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks

def mass_ingest():
    """Builds/Updates the FAISS index incrementally for all 83 journals."""
    if not os.path.exists(INDEX_FOLDER):
        os.makedirs(INDEX_FOLDER)

    # Load State
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
            processed_files = set(state.get("processed_files", []))
    else:
        processed_files = set()

    # Load existing FAISS index and metadata
    index = None
    all_metadata = []
    if os.path.exists(FAISS_FILE) and os.path.exists(METADATA_FILE):
        index = faiss.read_index(FAISS_FILE)
        with open(METADATA_FILE, "rb") as f:
            all_metadata = pickle.load(f)
        print(f"Resuming with {len(processed_files)} previously indexed journals.")

    # Get all PDF files
    pdf_files = sorted([f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")])
    to_process = [f for f in pdf_files if f not in processed_files]
    
    if not to_process:
        print("All journals are already indexed.")
        return

    print(f"Preparing to index {len(to_process)} new journals...")
    
    for filename in tqdm(to_process, desc="Incremental Ingestion"):
        path = os.path.join(PDF_FOLDER, filename)
        pages_text = extract_text_from_pdf(path)
        
        file_chunks = []
        for p in pages_text:
            file_chunks.extend(get_chunks(p["text"], p["page"], filename))
            
        if file_chunks:
            texts = [c["text"] for c in file_chunks]
            embeddings = model.encode(texts, show_progress_bar=False)
            embeddings = np.array(embeddings).astype("float32")
            
            # Initialize or update index
            if index is None:
                dimension = embeddings.shape[1]
                index = faiss.IndexFlatL2(dimension)
            
            index.add(embeddings)
            all_metadata.extend(file_chunks)
            processed_files.add(filename)
            
            # Sub-incremental Save: every file to be safe
            faiss.write_index(index, FAISS_FILE)
            with open(METADATA_FILE, "wb") as f:
                pickle.dump(all_metadata, f)
            with open(STATE_FILE, "w") as f:
                json.dump({"processed_files": list(processed_files)}, f)

    print(f"\n🚀 SUCCESS: Final index contains {len(pdf_files)} journals ({len(all_metadata)} chunks).")

if __name__ == "__main__":
    mass_ingest()
