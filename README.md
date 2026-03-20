# Music Academy Journal Explorer: Scholar Edition 🎓🎼

A high-performance RAG (Retrieval-Augmented Generation) system for analyzing 90 years of **Music Academy Journals (1930–2023)**. Powered by the **Groq Llama 3.3 70B** engine for ultra-fast, scholarly musicological research.

---

## 🏛 Project Vision
This system bridges the historical archives of the Music Academy, Madras, with modern AI. It enables researchers to trace the evolution of musical concepts, terms (like *Marga*, *Raaga*, *Desi*), and theoretical shifts over nearly a century of academic discourse.

## 🚀 Key Features
- **Temporal Analysis**: Every result is tagged with the year of publication, allowing for historical trend analysis.
- **Scholar-First UI**: A premium, high-contrast, large-font interface designed for readability and archival research.
- **Multi-Decade Retrieval**: An intelligent retrieval layer that gathers evidence across multiple eras (1930s-2020s) for comparative study.
- **Precision Terminology**: Integrated support for phonetic and historical variants of crucial musicological terms.

## 🏗 Tech Stack
- **AI Brain**: Meta's Llama 3.3 70B via **Groq** (480 tokens/sec).
- **Embeddings**: `sentence-transformers` (all-MiniLM-L6-v2).
- **Vector Database**: FAISS (L2 Index).
- **Backend**: FastAPI (Python).
- **Frontend**: Next.js 15, Tailwind CSS, Framer Motion (V0 Design).

---

## 🛠 Setup & Installation

### 1. Requirements
- Python 3.12+
- Node.js 18+
- Groq API Key

### 2. Backend Setup
```bash
# Clone the repository
git clone [your-repo-link]
cd ragalens

# Install Python dependencies
pip install groq fastapi uvicorn sentence-transformers faiss-cpu python-dotenv pdfminer.six tqdm

# Add your Groq API Key
echo 'GROQ_API_KEY=your_key_here' > .env

# Start the API
python3 api.py
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Running the Explorer
Visit [http://localhost:3000](http://localhost:3000) to start your research.

---

## 📂 Data Structure
- `Music Academy Journals/`: (Not included in repo by default) Place your PDF archive here.
- `vector_db/`: Contains the pre-built search index for all 83 volumes.
- `ingest.py`: Script to rebuild the vector database if you add more journals.

## ⚖️ License
This project is licensed under the **MIT License**.
*Historical Journal contents remain the property of the Music Academy, Madras.*
