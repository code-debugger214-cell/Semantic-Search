<div align="center">

# 🔍 RAG & Retrieval Evaluation Studio

**Dense semantic search vs. BM25 keyword search — rigorously compared, not just demo'd.**

[![Python](https://img.shields.io/badge/Python-3.11-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61dafb?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8-646cff?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev)
[![FAISS](https://img.shields.io/badge/FAISS-CPU-blue?style=flat-square)](https://github.com/facebookresearch/faiss)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

[Live Demo](#-quick-start) · [API Docs](#-api-reference) · [Deploy](#-deployment)

</div>

---

## What Is This?

Most retrieval demos just *show* semantic search working. This project *measures* it.

> **Semantic search (FAISS + MiniLM) vs BM25 keyword search — side-by-side results, head-to-head IR metrics, 4 real corpora.**

This is a portfolio-grade information retrieval evaluation system. Every search query runs through **both** retrieval methods simultaneously, and every corpus ships with a hand-labeled eval set so you can see real **Recall@k**, **MRR**, and **NDCG@5** numbers — not vibes.

---

## ✨ Features

| Feature | Description |
|---|---|
| ⚡ **Side-by-side search** | Semantic + BM25 results shown together in real time |
| 🧬 **Sentence-level search** | Pin-point matching within documents, not just chunk retrieval |
| 📊 **IR Evaluation** | Recall@1/3/5, MRR, NDCG@5 computed from hand-labeled eval sets |
| 📂 **4 pre-built corpora** | Ecology, ML Research, FAQ/SQuAD, Mobile Networks |
| 📤 **Upload your own** | Ingest PDF, TXT, DOCX, or JSONL — indexed on the fly |
| 🔎 **Chunk inspector** | Browse and search the raw index for any corpus |
| 🌐 **Unified server** | React SPA served directly by FastAPI — single deployment |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                 │
│  Compare │ Sentence │ Evaluate │ Ingest │ Chunks          │
└────────────────────┬────────────────────────────────────┘
                     │  REST API  (same origin)
┌────────────────────▼────────────────────────────────────┐
│                   FastAPI Backend                        │
│  /api/search  /api/search-sentence  /api/eval            │
│  /api/upload  /api/corpora  /api/chunks                  │
└──────────┬──────────────────────┬───────────────────────┘
           │                      │
┌──────────▼──────────┐  ┌───────▼────────────────────────┐
│   FAISS Index        │  │   BM25 Index (rank-bm25)        │
│   (sentence-trans.)  │  │   Classic TF-IDF variant        │
│   all-MiniLM-L6-v2  │  │   No ML, pure statistics        │
└──────────┬──────────┘  └───────┬────────────────────────┘
           └──────────┬──────────┘
              ┌───────▼────────┐
              │  corpus_store/ │
              │  chunks.jsonl  │
              │  embeddings.*  │
              │  bm25.pkl      │
              │  eval_set.json │
              └────────────────┘
```

### Offline Build (once per corpus)
```
Raw documents → Chunker → Embedder → FAISS index
                                   → BM25 index
                                   → eval_set.json
```

### Online Query (per search)
```
User query → [FAISS semantic search]  → top-k results ┐
           → [BM25 keyword search]    → top-k results ┘→ side-by-side UI
```

---

## 🧰 Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| **Embeddings** | `sentence-transformers` (`all-MiniLM-L6-v2`) | 384-dim dense vectors, no training needed |
| **Vector Index** | `faiss-cpu` | Fast approximate nearest-neighbor search |
| **Keyword Index** | `rank-bm25` | Classical probabilistic retrieval baseline |
| **Backend** | `FastAPI` + `Uvicorn` | REST API + static file serving |
| **Frontend** | `React 19` + `Vite 8` + `Tailwind CSS v4` | Interactive comparison UI |
| **Data** | `Pydantic v2` + JSONL | Typed schemas, streaming corpus format |

---

## 📊 Evaluation Metrics — What They Mean

```
Recall@k  →  "Did the right answer appear in the top k results?"
             Perfect = 1.0 | Miss = 0.0

MRR       →  "How high up was the FIRST correct result?"
             Rank 1 = 1.0 | Rank 2 = 0.5 | Rank 5 = 0.2

NDCG@5    →  "Were the correct results ranked well among the top 5?"
             Accounts for position AND multiple correct answers
```

---

## 📦 Pre-built Corpora

| Corpus | Domain | Chunks | Eval Queries |
|---|---|---|---|
| `ecology_abstracts` | Ecology / SDG-15 research papers | 50 | 10 |
| `ml_research` | Machine learning paper abstracts | 50 | 10 |
| `faq_squad` | Wikipedia FAQ (SQuAD-style) | 50 | 10 |
| `mobile_networks_abstracts` | Telecom / 5G research | 50 | 10 |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### Run locally (development)

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/rag-retrieval-studio.git
cd rag-retrieval-studio

# 2. Python env
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt

# 3. Start the backend
uvicorn backend.main:app --reload --port 8000
# API: http://localhost:8000/api/health

# 4. Start the frontend (separate terminal)
cd frontend
npm install
npm run dev
# UI: http://localhost:5173
```

### Run as unified production server

```bash
python build_and_start.py
# → Builds React bundle, starts FastAPI on http://localhost:8000
```

---

## 🌐 Deployment

This app ships ready-to-deploy config files for all major platforms.

### ▲ Render (Recommended — full-stack free tier)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Push to GitHub
2. Go to [render.com](https://render.com) → **New** → **Blueprint**
3. Connect your repo — `render.yaml` is auto-detected
4. Click **Deploy** ✓

### 🚂 Railway

```bash
# Install Railway CLI
npm install -g @railway/cli
railway login
railway up
```

Or connect your GitHub repo at [railway.app](https://railway.app) — `railway.toml` is auto-detected.

### ▲ Vercel (frontend only)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

Vercel auto-detects `vercel.json`. Backend must be deployed separately (e.g., Render).

### ◈ Netlify (frontend only)

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start)

Netlify auto-detects `netlify.toml`. Backend must be deployed separately.

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/corpora` | List all indexed corpora + metadata |
| `POST` | `/api/search` | Side-by-side semantic + BM25 search |
| `POST` | `/api/search-sentence` | Sentence-level semantic search |
| `GET` | `/api/eval/{corpus}` | Recall@k, MRR, NDCG metrics |
| `POST` | `/api/upload` | Upload files and index a new corpus |
| `GET` | `/api/chunks/{corpus}` | Browse raw index chunks |
| `GET` | `/api/documents/{corpus}` | List unique documents in a corpus |

Interactive API docs available at **`/docs`** (Swagger UI) and **`/redoc`** when the server is running.

---

## 📁 Project Structure

```
rag-retrieval-studio/
├── app/                        # Core ML pipeline
│   ├── chunker.py              # Configurable text chunking
│   ├── embedder.py             # sentence-transformers wrapper
│   ├── indexing.py             # Builds FAISS + BM25 indexes
│   ├── retriever.py            # semantic_search() + keyword_search()
│   ├── eval.py                 # Recall@k, MRR, NDCG harness
│   ├── ingest.py               # Upload → chunk → embed → index pipeline
│   └── loaders/                # Corpus-specific loaders (only place)
├── backend/
│   ├── main.py                 # FastAPI app + SPA server
│   ├── sentence_search.py      # Sentence-level search logic
│   └── file_parsers.py         # PDF / DOCX / TXT / JSONL parsers
├── frontend/                   # React + Vite + Tailwind CSS v4
│   └── src/
│       ├── App.jsx             # Main app + all tab views
│       └── components/         # LiveSearch, EvalDashboard, etc.
├── corpus_store/               # Pre-built indexes (committed to git)
│   ├── ecology_abstracts/
│   ├── ml_research/
│   ├── faq_squad/
│   └── mobile_networks_abstracts/
├── scripts/                    # Offline build + pull scripts
├── render.yaml                 # Render deployment config
├── railway.toml                # Railway deployment config
├── netlify.toml                # Netlify frontend config
├── vercel.json                 # Vercel frontend config
├── Procfile                    # Universal process launcher
└── requirements.txt
```

---

## 🔬 Key Design Decisions

- **No model training** — pretrained `all-MiniLM-L6-v2` used as a black box. The comparison is the contribution, not fine-tuning.
- **Offline index build** — FAISS and BM25 indexes are built once and stored in `corpus_store/`. Live queries never rebuild indexes.
- **Genericity by structure** — corpus-specific code is only allowed in `app/loaders/`. The rest of the pipeline is 100% corpus-agnostic.
- **Honest evaluation** — eval sets include paraphrased queries (semantic advantage) *and* exact-wording queries (BM25 advantage) to avoid bias.

---

## 📄 License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

Built with ❤️ as a rigorous ML/IR portfolio project.

⭐ Star this repo if you found it useful!

</div>
