# Project Architecture & Methodology

## System Diagram

```text
       +-----------------------+
       | Musicology Journals   |
       | (PDFs, OCR Scans,     |
       |  Decade Collections)  |
       +-----------------------+
                   |
                   v
       +-------------------------------+
       | PDF Ingestion & OCR Layer     |
       | PyMuPDF (text)                |
       | Tesseract (scanned docs)      |
       | Cleaning + Normalization      |
       +-------------------------------+
                   |
                   v
       +--------------------------------------+
       | Document Structuring Layer           |
       | - Chunking                           |
       | - Metadata Extraction (Year, Author) |
       | - Term Detection                     |
       | - Decade Tagging                     |
       +--------------------------------------+
                   |
                   v
       +--------------------------------------+
       | OpenRouter LLM Analysis Engine       |
       | (Kimi K2.5 / GPT-OSS / Llama / Qwen) |
       |                                      |
       | Stage 1: Targeted Concept Extraction |
       | Stage 2: Per-Paper Summary           |
       | Stage 3: Per-Decade Synthesis        |
       | Stage 4: Cross-Decade Evolution      |
       +--------------------------------------+
                   |
         +---------+---------+
         |                   |
         v                   v
+-----------------+   +-----------------------+
| SQLite Metadata |   | Theory Synthesis      |
| - Paper Data    |   | Engine                |
| - Term JSON     |   | - Evolution Mapping   |
| - Decade Index  |   | - Shift Detection     |
+-----------------+   +-----------------------+
         |                   |
         +---------+---------+
                   |
                   v
       +----------------------------------+
       | React Research Dashboard         |
       | - Timeline View                  |
       | - Concept Comparison             |
       | - Debate Intensity Graph         |
       | - Methodology Evolution Chart    |
       +----------------------------------+
```

## Methodology Overview

### 1. Hybrid Ingestion Layer
The system handles raw, high-resolution academic journals using a combination of **PyMuPDF** for native text parsing and **Tesseract OCR** for archival scanned documents. A normalization pass cleans the extracted text to handle common OCR errors.

### 2. Document Structuring
Documents are segmented and tagged with metadata including **Decade Collections**. This creates a longitudinal anchor, allowing concepts to be tracked over a century of academic discussion.

### 3. OpenRouter LLM Orchestration
The core analysis utilizes state-of-the-art models via OpenRouter (Primary: **Kimi K2.5**, Fallback: **GPT-OSS 120B**). The processing follows a multi-stage approach:
- **Extraction**: Identifying the 6 primary musicology terms (Marga, Raagas, Taala, Prabandha, Desi, Vaadya).
- **Paper-Level Summary**: Generating rigorous academic condensations per document.
- **Synthesis**: Aggregating decade-level data to identify shifts, dominant framings, and novel methodologies.

### 4. Persistence & Research Dashboard
Structured data is persisted in **SQLite**, providing a balance of relational search and JSON storage. The **React Dashboard** visualizes this data through timelines and evolution charts, enabling researchers to see "debate intensity" and "conceptual shifts" across history.
