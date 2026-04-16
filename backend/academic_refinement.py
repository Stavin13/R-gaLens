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

def refine_report():
    print("Loading models and index...")
    model = SentenceTransformer(MODEL_NAME)
    index = faiss.read_index(os.path.join(INDEX_FOLDER, "index.faiss"))
    with open(os.path.join(INDEX_FOLDER, "metadata.pkl"), "rb") as f:
        chunks = pickle.load(f)
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    # Focused searches for explicit Desi terms
    queries = [
        "What specific Desi Taalas or Desi Raagas are discussed as neglected or research gaps?",
        "Details of Desi Prabandhas or regional musical components in the latest journals",
        "Scholarly names of Desi components in the recent past citations",
        "Criticism of current musicology neglecting Desi traditions"
    ]

    extra_context = []
    for q in queries:
        print(f"Querying for specifics: {q}")
        query_vector = model.encode([q]).astype("float32")
        distances, indices = index.search(query_vector, 5)
        for i in indices[0]:
            if i < len(chunks):
                fname = chunks[i]["filename"]
                year_match = re.search(r"(\d{4})", fname)
                year = year_match.group(1) if year_match else "Unknown"
                text = f"[Source: {fname}, Year: {year}] {chunks[i]['text']}"
                if text not in extra_context:
                    extra_context.append(text)

    # Read the previous report
    with open("academic_analysis_report.md", "r") as f:
        previous_report = f.read()

    extra_context_str = "---\n".join(extra_context)
    refinement_prompt = f"""
ACT AS: A Senior Research Musicologist.
The user felt the previous report was too summary-like. We need to go DEEPER into the musicological specifics.

PREVIOUS REPORT CORE:
{previous_report}

NEW SPECIFIC CONTEXT:
{extra_context_str}

TASK:
Rework the report to include specific musicological details found in the new context. 
- Mention specific names of Desi Taalas, Raagas, or Prabandhas if they appear in the clips.
- Provide a more critical analysis of WHY these gaps exist (e.g., is it due to Marga-centricity?).
- Focus on the "Recent Past" (2000-2023) and provide a granular view of the scholars' interests. 
- Use specific terminology (e.g., Suladi, Lakshana, regional variants).

FINAL OUTPUT:
An expanded, high-depth Academic Analysis Artifact.
"""

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a master musicology analyst. Depth and specific evidence are your hallmarks."},
            {"role": "user", "content": refinement_prompt}
        ],
        model=GROQ_MODEL,
    )
    
    final_report = chat_completion.choices[0].message.content
    
    with open("academic_analysis_report_v2.md", "w") as f:
        f.write(final_report)
    
    print("\nDeep-dive report generated: academic_analysis_report_v2.md")

if __name__ == "__main__":
    refine_report()
