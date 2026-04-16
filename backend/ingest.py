import os
# CRITICAL: Prevent multithreading conflicts on Mac arm64
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import faiss
import numpy as np
import pickle
import json
import easyocr
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from pdf2image import convert_from_path
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from tqdm import tqdm
from PIL import Image

# Config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FOLDER = os.path.join(BASE_DIR, "vector_db")
PDF_FOLDERS = [
    os.path.join(BASE_DIR, "Music Academy Journals"),
    os.path.join(BASE_DIR, "Research Database-Music")
]
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
STATE_FILE = os.path.join(INDEX_FOLDER, "index_state.json")
FAISS_FILE = os.path.join(INDEX_FOLDER, "index.faiss")
METADATA_FILE = os.path.join(INDEX_FOLDER, "metadata.pkl")

# Global Resource Handles
_model = None

def get_embedding_model():
    """Lazily loads the embedding model."""
    global _model
    if _model is None:
        print(f"Loading {MODEL_NAME}...")
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model

# Lazy-loaded OCR Readers (to save RAM)
# We map script groups that easyocr allows
_READERS = {}

def get_reader(lang_group):
    """Initializes or retrieves an easyocr Reader for a specific group."""
    global _READERS
    if lang_group not in _READERS:
        print(f"--- Initializing OCR for: {lang_group} (CPU Mode for Stability) ---")
        if lang_group == 'sanskrit':
            _READERS[lang_group] = easyocr.Reader(['hi', 'en'], gpu=False)
        elif lang_group == 'kannada':
            _READERS[lang_group] = easyocr.Reader(['kn', 'en'], gpu=False)
        elif lang_group == 'telugu':
            _READERS[lang_group] = easyocr.Reader(['te', 'en'], gpu=False)
    return _READERS[lang_group]

def extract_text_hybrid(pdf_path: str) -> List[Dict]:
    """
    Tries PDF text extraction first. 
    Falls back to OCR if page seems to be an image.
    """
    results = []
    fname = os.path.basename(pdf_path).lower()
    
    # Decide which OCR to use based on filename keywords
    primary_lang = 'sanskrit' # Default
    if 'kannada' in fname or 'vachan' in fname:
        primary_lang = 'kannada'
    elif 'telugu' in fname or 'vemana' in fname:
        primary_lang = 'telugu'

    try:
        pages = list(extract_pages(pdf_path))
        for page_num, page_layout in enumerate(pages):
            text = ""
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    text += element.get_text()
            
            # Hybrid Threshold: If text is sparse, trigger OCR
            if len(text.strip()) < 50:
                images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
                if images:
                    img_np = np.array(images[0])
                    # Run the appropriate reader
                    reader = get_reader(primary_lang)
                    ocr_results = reader.readtext(img_np, detail=0)
                    text = " ".join(ocr_results)
            
            if text.strip():
                results.append({"text": text, "page": page_num + 1})
                
    except Exception as e:
        print(f"\n[!] Error processing {os.path.basename(pdf_path)}: {e}")
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
    """Builds/Updates the FAISS index incrementally."""
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
        
    # Get all PDF files from all folders
    all_pdf_tasks = []
    for folder in PDF_FOLDERS:
        if os.path.exists(folder):
            files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".pdf")]
            all_pdf_tasks.extend(files)
    
    to_process = [f for f in all_pdf_tasks if os.path.basename(f) not in processed_files]
    
    if not to_process:
        print("All journals in the specified folders are already indexed.")
        return

    print(f"Preparing to index {len(to_process)} journals with Multilingual OCR support...")
    
    for full_path in tqdm(to_process, desc="OCR Ingestion"):
        filename = os.path.basename(full_path)
        print(f"\n[Processing] {filename}...")
        pages_text = extract_text_hybrid(full_path)
        
        file_chunks = []
        for p in pages_text:
            file_chunks.extend(get_chunks(p["text"], p["page"], filename))
            
        if file_chunks:
            texts = [c["text"] for c in file_chunks]
            # Load model only when we need to encode
            model = get_embedding_model()
            embeddings = model.encode(texts, show_progress_bar=False)
            embeddings = np.array(embeddings).astype("float32")
            
            if index is None:
                dimension = embeddings.shape[1]
                index = faiss.IndexFlatL2(dimension)
            
            index.add(embeddings)
            all_metadata.extend(file_chunks)
            processed_files.add(filename)
            
            # Save progress after each file
            faiss.write_index(index, FAISS_FILE)
            with open(METADATA_FILE, "wb") as f:
                pickle.dump(all_metadata, f)
            with open(STATE_FILE, "w") as f:
                json.dump({"processed_files": list(processed_files)}, f)

    print(f"\n🚀 SUCCESS: Final index contains {len(all_metadata)} chunks.")

if __name__ == "__main__":
    if os.path.exists(INDEX_FOLDER) and "index.faiss" in os.listdir(INDEX_FOLDER):
        # Allow incremental ingestion if model matches
        # For now, let's just run it.
        mass_ingest()
    else:
        mass_ingest()
