# R-gaLens: Musicology Research Assistant (v2.0)

R-gaLens is a comprehensive AI-powered research assistant designed for musicologists. It processes archival musicology journals (PDFs) from 1930 to the present, extracts significant events, and builds a longitudinal synthesis of academic theory across the decades.

## 🚀 Key Features

- **Inteligent Ingestion**: Automatic processing of archival journals using **PyMuPDF** and **Tesseract OCR** with image enhancement for historical scans.
- **OpenRouter LLM Engine**: Advanced reasoning using **Kimi K2.5** (Moonshot AI) and **GPT-OSS 120B** (OpenAI) for academic-grade summarization and analysis.
- **Theory Synthesis (New)**: A rigorous 5-stage synthesis pipeline that maps the evolution of 6 primary concepts:
  - **Marga**, **Raagas**, **Taala**, **Prabandha**, **Desi**, **Vaadya**
- **Longitudinal Analysis**: Automatically tags and groups research by decade, enabling researchers to see how dominant framings and methodologies shifted over time.
- **Interactive Research Dashboard**: A React-based interface for:
  - **Granular Search**: Locating specific mentions with Sanskrit diacritic awareness.
  - **Theory Reports**: Generating decade-by-decade academic synthesis on-demand.

## 🛠️ Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy (SQLite)
- **AI/NLP**: OpenRouter (Kimi K2.5, GPT-OSS), SpaCy (local), Tesseract OCR
- **Frontend**: React.js, Vite, Lucide Icons
- **Data Architecture**: Structured JSON persistent storage for cross-decade theoretical mapping.

## 📐 Architecture

For a detailed breakdown of our 5-stage pipeline and methodology, see [ARCHITECTURE.md](./ARCHITECTURE.md).

## ⚙️ Setup & Installation

### Backend
1. Navigate to `backend/`
2. Create virtual environment: `python -m venv .venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Configure `.env`:
   ```env
   OPENROUTER_API_KEY=your_key_here
   DATABASE_URL=sqlite:///./data/musicology.db
   ```
5. Start API server: `uvicorn app.main:app --reload`

### Frontend
1. Navigate to `frontend/`
2. Install dependencies: `npm install`
3. Start dev server: `npm run dev`

## 🛠️ Operational Commands

### 1. Batch Document Ingestion
To re-process your entire PDF database using the new OpenRouter pipeline:
```bash
PYTHONPATH=backend ./.venv/bin/python backend/scripts/batch_process_openrouter.py --batch 5 --delay 10
```

### 2. Manual Theory Synthesis
To generate a rigorous academic report for a specific term from the CLI:
```bash
PYTHONPATH=backend ./.venv/bin/python backend/scripts/generate_rigorous_synthesis.py "Marga"
```

## 📄 License & Version
**Version 2.0.0 (OpenRouter Edition)**
Designed for rigorous musicology research and archival analysis.
