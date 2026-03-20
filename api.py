from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import faiss
import numpy as np
import pickle
from groq import Groq
from sentence_transformers import SentenceTransformer
from typing import List
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv() # Load from .env

app = FastAPI()

# Add CORS - explicitly allow Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://r-ga-lens.vercel.app",
        "http://localhost:3000",  # Local dev
        "http://localhost:3001",  # Local dev alt
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

# Config
INDEX_FOLDER = "vector_db"
MODEL_NAME = "all-MiniLM-L6-v2"
GROQ_MODEL = "llama-3.3-70b-versatile" 

# Global Resource Handles (Lazy Loaded for Render Stability)
model = None
index = None
chunks = None
client = None

# IMPORTANT TERMS & SYNONYMS
TERM_EXPANSION = {
    "marga": ["marga", "mārga", "margi"],
    "raaga": ["raaga", "raga", "rāga", "ragas"],
    "taala": ["taala", "tala", "tāla", "tal"],
    "prabandha": ["prabandha"],
    "desi": ["desi", "deshi", "deśi", "deśya"],
    "vaadya": ["vaadya", "vadya", "vādya", "vaadyam"]
}

def expand_query(query: str) -> str:
    """Expands query with synonyms for important terms."""
    expanded = query.lower()
    for term, variants in TERM_EXPANSION.items():
        if term in expanded:
            expanded += " (" + " ".join(variants) + ")"
    return expanded

def load_resources():
    global model, index, chunks, client
    print("Loading AI models and search index into RAM... (May take 1-2 mins on free tier)")
    model = SentenceTransformer(MODEL_NAME, device='cpu')
    index = faiss.read_index(os.path.join(INDEX_FOLDER, "index.faiss"))
    with open(os.path.join(INDEX_FOLDER, "metadata.pkl"), "rb") as f:
        chunks = pickle.load(f)
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    print("Resources loaded successfully.")

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

@app.get("/")
def health_check():
    return {"status": "online", "archive": "Music Academy Journal Explorer v1.2"}

@app.post("/query")
async def process_query(req: QueryRequest):
    global model, index, chunks, client
    try:
        if model is None:
            load_resources()
            
        # Preprocess and expand query for better retrieval
        query_to_search = expand_query(req.query)
        print(f"Original: {req.query} | Expanded: {query_to_search}")
        
        # Increase top_k for temporal analysis
        query_vector = model.encode([query_to_search]).astype("float32")
        distances, indices = index.search(query_vector, req.top_k * 2) 
        
        context = []
        sources = []
        import re
        for i in indices[0]:
            if i < len(chunks):
                fname = chunks[i]["filename"]
                # Extract year roughly from filename (e.g., 1933 or 2023)
                year_match = re.search(r"(\d{4})", fname)
                year = year_match.group(1) if year_match else "Unknown"
                
                context.append(f"[YEAR: {year}] {chunks[i]['text']}")
                sources.append({
                    "filename": fname,
                    "page": chunks[i]["page"],
                    "year": year
                })
        
        context_str = "\n---\n".join(context)
        
        # Format citations for the v0-designed frontend
        formatted_citations = []
        for s in sources:
            formatted_citations.append({
                "source": s["filename"],
                "publicationYear": int(s["year"]) if s["year"].isdigit() else 0,
                "pages": f"Page {s['page']}"
            })

        prompt = f"""
Historical Context from Music Academy Journals (1930-2023):
{context_str}

Query: {req.query}

Goal: Provide a scholarly response. If the query asks about history or evolution, please highlight how the discussion has changed or remained consistent across different years/decades based on the provided context tagged with [YEAR].
"""
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional musicologist specializing in the Music Academy Journals. Answer based on the context."},
                {"role": "user", "content": prompt}
            ],
            model=GROQ_MODEL,
        )
        
        return {
            "answer": chat_completion.choices[0].message.content,
            "citations": formatted_citations
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Use PORT env var for Render/Heroku/Railway
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
