# PLC Error Code Troubleshooter

An AI-powered RAG chatbot for Siemens PLC error code diagnostics, built during an AI Co-op at **MHA Solutions Inc.**

## Overview

Field technicians working with Siemens PLCs often need to look up error codes across lengthy technical manuals. This tool replaces that manual process with a conversational AI assistant that retrieves accurate, grounded answers in seconds.

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────┐
│  FastAPI Backend (port 8000)        │
│                                     │
│  1. Exact match on error_code       │
│  2. Partial code match              │
│  3. FAISS semantic search           │
│     (all-MiniLM-L6-v2 embeddings)  │
│                                     │
│  Retrieved context → Gemini 1.5    │
│  Flash (temperature=0, no halluc.) │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Streamlit Frontend (port 8501)     │
│                                     │
│  Tab 1: Troubleshooter              │
│  Tab 2: Data Governance Dashboard   │
└─────────────────────────────────────┘
```

## Dataset

- **Source**: Scraped from official Siemens PLC documentation
- **Coverage**: Modbus, PtP, USS error types
- **Records**: 137 unique error codes after cleaning
- **Governance**: Full audit log of data changes + query log

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/rkdhakal/PLC_Chatbot.git
cd PLC_Chatbot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your Gemini API key
```bash
cp .env.example .env
# Edit .env and add your key
```
Get a free Gemini API key at [aistudio.google.com](https://aistudio.google.com)

### 4. Start the backend
```bash
cd backend/preprocessing
fastapi run chatbot_api.py
```

### 5. Start the frontend (new terminal)
```bash
cd frontend
streamlit run app.py
```

Open `http://localhost:8501`

## Features

- **Exact + Semantic Search** — tries exact error code match first, falls back to FAISS semantic search
- **Zero Hallucination** — LLM is strictly constrained to retrieved data only
- **Match Confidence Score** — every result shows how confident the match is
- **Match Type Badge** — shows whether result came from exact, partial, or semantic match
- **Data Governance Tab** — dataset health, query analytics, exportable audit log
- **Query Audit Log** — every query + response + confidence logged to CSV

## Tech Stack

| Layer | Technology |
|---|---|
| Embedding | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector Search | FAISS (IndexFlatIP, cosine similarity) |
| LLM | Google Gemini 1.5 Flash |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Data | Pandas + CSV |

## Author

**Ram Krishna Dhakal** — AI Co-op Intern, MHA Solutions Inc. (Jan–Apr 2025)
