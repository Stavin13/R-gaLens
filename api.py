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

# CRITICAL: Prevent multithreading conflicts on Mac arm64
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

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
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
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
    model = SentenceTransformer(MODEL_NAME)
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
        
        # Increase top_k significantly for deep research analysis (Top 25 results)
        query_vector = model.encode([query_to_search]).astype("float32")
        distances, indices = index.search(query_vector, 25) 
        
        context = []
        sources = []
        import re
        for i in indices[0]:
            if i < len(chunks):
                fname = chunks[i]["filename"]
                # Extract year roughly from filename (e.g., 1933 or 2023)
                year_match = re.search(r"(\d{4})", fname)
                year = year_match.group(1) if year_match else "Unknown"
                
                context.append(f"[SOURCE {len(context)+1}: {fname}, Page {chunks[i]['page']}] {chunks[i]['text']}")
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
ROLE: Senior Research Musicologist & Archive Historian.
SOURCE CORPUS: Music Academy Journal Archives (1930-2023).

### MASTER RESEARCH CONTEXT (25 HIGH-RELEVANCE EXCERPTS)
{context_str}

### RESEARCH QUESTION
{req.query}

---

### REQUIRED COMPREHENSIVE OUTPUT STRUCTURE:
1. **Consensus Overview**: Provide an expanded abstract. Summarize matching and conflicting views across the sources.
2. **Deep Evidence Analysis**: For every claim, you MUST provide 1-2 sentences of specific detail from the text. Cite as [1], [2] etc.
3. **Comparative Data Table**: Construct a Markdown table that cross-references names, dates, and different terminologies found in the context.
4. **Historical Evolution (Deep Dive)**: Contrast how this specific topic was discussed in the early 20th century vs the modern era based strictly on the source numbers.
5. **Scholarly Gaps**: Identify what isn't said in these specific 25 excerpts that a musicologist would want to know.
6. **Bibliography**: List all used sources with their specific page numbers.
"""
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are an Elite Musicological Research AI. Your goal is to provide LONG, COMPREHENSIVE, "
                        "and highly technical research reports. \n"
                        "RULES: \n"
                        "1. BE VOLUMINOUS: Expand on every point. If you see a name or date, explain its relevance from the context.\n"
                        "2. In-text citations [1] are mandatory for every fact.\n"
                        "3. Use Markdown tables for any comparison.\n"
                        "4. Maintain a formal, academic tone.\n"
                        "5. If the source material is in a regional language (Sanskrit, Tamil, Kannada, etc.), "
                        "refer to the original terminology in brackets.\n"
                        "6. NEVER hallucinate. If the OCR is garbled, state 'Primary source text unclear' instead of guessing."
                    )
                },
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
    # 'workers=1' is critical for Mac ARM stability with FAISS + Torch
    uvicorn.run(app, host="0.0.0.0", port=port, workers=1, loop="asyncio")
