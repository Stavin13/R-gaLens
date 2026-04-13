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

def run_deep_dive():
    # 1. Load Everything
    print("Loading models and index...")
    model = SentenceTransformer(MODEL_NAME)
    index = faiss.read_index(os.path.join(INDEX_FOLDER, "index.faiss"))
    with open(os.path.join(INDEX_FOLDER, "metadata.pkl"), "rb") as f:
        chunks = pickle.load(f)
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    queries = [
        "Evolution and research trends of Desi Taala, Desi Raaga, and regional components in Music Academy Journals",
        "Recent research gaps in Desi musicological elements in 21st century journals",
        "Major areas of scholarly interest in Music Academy journals 1930-2023"
    ]

    all_context = []
    
    for q in queries:
        print(f"Querying for: {q}")
        query_vector = model.encode([q]).astype("float32")
        distances, indices = index.search(query_vector, 8) # Reduced top_k
        
        for i in indices[0]:
            if i < len(chunks):
                fname = chunks[i]["filename"]
                year_match = re.search(r"(\d{4})", fname)
                year = year_match.group(1) if year_match else "Unknown"
                text = f"[Source: {fname}, Year: {year}, Page: {chunks[i]['page']}] {chunks[i]['text']}"
                if text not in all_context:
                    all_context.append(text)

    context_str = "\n---\n".join(all_context)
    
    print(f"Consolidated {len(all_context)} context snippets. Generating in-depth report...")

    analysis_prompt = f"""
ACT AS: A Senior Research Musicologist and Academic Analyst.

DATA SOURCE: Historical excerpts from the Music Academy Journals (1930-2023).

TASKS:
1. Provide an in-depth Academic Analysis Report on:
   - The trend in the recent past (21st century vs earlier 20th) regarding research gaps specifically in DESI components (Taalas, Raagas, Desi Prabandhas, etc.).
   - Are these elements being prioritized or neglected? Identify the specific "gaps" mentioned or implied by the shift in discourse.
2. Analyze the MAJOR AREAS OF INTEREST for scholars over time.
   - What were the 'obsessions' of the 1930s-1950s vs the 2000s-Present?
   - How has the definition of "scholarly interest" transitioned?

REQUIREMENTS:
- Do NOT provide a high-level summary. Go DEEP.
- Reference specific years or decades found in the context.
- Use an academic, critical tone.
- Discuss "Marga" vs "Desi" if relevant to the context found.

CONTEXT EXCERPTS:
{context_str}

FINAL OUTPUT:
Return a comprehensive, structured academic report.
"""

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a senior musicology scholar. Provide exceptionally detailed, evidence-based academic analysis."},
            {"role": "user", "content": analysis_prompt}
        ],
        model=GROQ_MODEL,
    )
    
    report = chat_completion.choices[0].message.content
    
    with open("academic_analysis_report.md", "w") as f:
        f.write(report)
    
    print("\nReport generated: academic_analysis_report.md")

if __name__ == "__main__":
    run_deep_dive()
