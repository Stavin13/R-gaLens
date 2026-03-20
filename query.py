import os
import faiss
import numpy as np
import pickle
from groq import Groq
from sentence_transformers import SentenceTransformer

# Config
INDEX_FOLDER = "vector_db"
MODEL_NAME = "all-MiniLM-L6-v2"
GROQ_MODEL = "llama3-70b-8192"

def query_rag(query: str, top_k: int = 5):
    """Retrieves relevant chunks and sends to Groq."""
    
    # 1. Load Everything
    print("Loading models and index...")
    model = SentenceTransformer(MODEL_NAME)
    index = faiss.read_index(os.path.join(INDEX_FOLDER, "index.faiss"))
    with open(os.path.join(INDEX_FOLDER, "metadata.pkl"), "rb") as f:
        chunks = pickle.load(f)
    
    # 2. Embed Query
    print(f"Searching for: {query}")
    query_vector = model.encode([query]).astype("float32")
    distances, indices = index.search(query_vector, top_k)
    
    # 3. Retrieve Context
    context = []
    metadata = []
    for i in indices[0]:
        if i < len(chunks):
            context.append(chunks[i]["text"])
            metadata.append(f"[{chunks[i]['filename']}, Page {chunks[i]['page']}]")
    
    context_str = "\n---\n".join(context)
    sources_str = ", ".join(set(metadata))
    
    # 4. Prompt Groq
    print("Asking Groq...")
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    prompt = f"""
Journal Context:
{context_str}

Query: {query}

Instructions: Using the historical Music Academy Journal excerpts above, provide a scholarly answer. 
Reference specific volumes if possible. If the context doesn't contain the answer, inform the researcher.
"""

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a professional musicologist specializing in the Music Academy Journals."},
            {"role": "user", "content": prompt}
        ],
        model=GROQ_MODEL,
    )
    
    print("\n--- SCHOLARLY RESPONSE ---")
    print(chat_completion.choices[0].message.content)
    print("\nSources Cited:", sources_str)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query_rag(" ".join(sys.argv[1:]))
    else:
        print("Provide a query, e.g., 'What are the main topics discussed in 1933?'")
