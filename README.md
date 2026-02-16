# R-gaLens: Musicology Research Assistant

R-gaLens is a comprehensive AI-powered research assistant designed for musicologists. It processes historical musicology journals (PDFs), extracts significant events, and provides a powerful, Sanskrit-aware search engine to find terms across decades of literature.

## 🚀 Features

- **Inteligent PDF Ingestion**: Automatic processing of journals using OCR (Tesseract) and image enhancement for historical scans.
- **Event Extraction**: Uses NLP models to extract dates, historical figures, and musicology-specific entities from text.
- **Sanskrit-Aware Search**: A specialized search engine that understands:
  - Common transliterations (e.g., *Raaga*, *Raga*)
  - Sanskrit diacritics (e.g., *Rāga*, *Tāla*, *Mārga*)
  - Grammar variants (e.g., *-am* endings like *Rāgam*)
  - Devanagari script support
- **Interactive Timelines**: Visualize historical events extracted from journals in a chronological order.
- **Rich Analytics**: Summarization and topic modeling of academic papers.

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy (SQLite)
- **AI/NLP**: SpaCy, HuggingFace Transformers (BART, BERT), Tesseract OCR
- **Frontend**: React.js, Vite, Tailwind CSS (Vanilla CSS base)
- **Data Management**: Event-driven extraction and structured storage

## 📦 Project Structure

```text
├── backend/
│   ├── app/                # FastAPI application logic
│   ├── scripts/            # Utility scripts (Ingestion, Search)
│   └── data/               # Local database and file storage (gitignored)
├── frontend/               # React frontend application
└── Music Academy Journals/ # Local source PDFs
```

## ⚙️ Setup & Installation

### Backend
1. Navigate to `backend/`
2. Create virtual environment: `python -m venv .venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Set up `.env` with your `DATABASE_URL`
5. Run server: `uvicorn app.main:app --reload`

### Frontend
1. Navigate to `frontend/`
2. Install dependencies: `npm install`
3. Start dev server: `npm run dev`

## 🔍 How to Search
Use the `backend/scripts/search_terms.py` script for exhaustive database searches:
```bash
python scripts/search_terms.py
```
This script is pre-configured to find terms like **Marga, Desi, Raga, Tala, Prabandha, and Vaadya** with full support for Sanskrit variations.

## 📄 License
Version 1.0.0
Created for Advanced Musicology Research.
