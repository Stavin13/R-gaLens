import os
import faiss
import numpy as np
import pickle
import re
from groq import Groq
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# Config
INDEX_FOLDER = "vector_db"
MODEL_NAME = "all-MiniLM-L6-v2"
GROQ_MODEL = "llama-3.3-70b-versatile"

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
    expanded = query.lower()
    for term, variants in TERM_EXPANSION.items():
        if term in expanded:
            expanded += " (" + " ".join(variants) + ")"
    return expanded

class JournalExplorer:
    def __init__(self):
        print("Initializing RagaLens CLI Explorer...")
        self.model = SentenceTransformer(MODEL_NAME)
        self.index = faiss.read_index(os.path.join(INDEX_FOLDER, "index.faiss"))
        with open(os.path.join(INDEX_FOLDER, "metadata.pkl"), "rb") as f:
            self.chunks = pickle.load(f)
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        print("Ready! Type 'exit' to quit.\n")

    def ask(self, query: str, top_k: int = 10):
        # 1. Expand Query
        search_query = expand_query(query)
        
        # 2. Search Index
        query_vector = self.model.encode([search_query]).astype("float32")
        distances, indices = self.index.search(query_vector, top_k)
        
        # 3. Build Context
        context = []
        sources = []
        for i in indices[0]:
            if i < len(self.chunks):
                fname = self.chunks[i]["filename"]
                year_match = re.search(r"(\d{4})", fname)
                year = year_match.group(1) if year_match else "Unknown"
                
                context.append(f"[YEAR: {year}] {self.chunks[i]['text']}")
                sources.append(f"{fname} (Page {self.chunks[i]['page']}, {year})")
        
        context_str = "\n---\n".join(context)
        
        # 4. Prompt
        prompt = f"""
Historical Context from Music Academy Journals (1930-2023):
{context_str}

Query: {query}

Instructions: Provide a professional, deep-dive musicological answer. 
Focus on temporal evolution and specific details found in the context.
"""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a professional musicologist specializing in the Music Academy Journals."},
                    {"role": "user", "content": prompt}
                ],
                model=GROQ_MODEL,
            )
            
            print("\n" + "="*50)
            print("📜 SCHOLARLY RESPONSE")
            print("="*50)
            print(chat_completion.choices[0].message.content)
            print("\n" + "-"*50)
            print("📚 SOURCES CITED:")
            for s in sorted(list(set(sources))):
                print(f"• {s}")
            print("="*50 + "\n")
            
        except Exception as e:
            print(f"Error communicating with AI: {e}")

if __name__ == "__main__":
    explorer = JournalExplorer()
    while True:
        user_input = input("Ask a musicology question (or 'exit'): ")
        if user_input.lower() in ['exit', 'quit', 'q']:
            break
        if not user_input.strip():
            continue
        explorer.ask(user_input)
