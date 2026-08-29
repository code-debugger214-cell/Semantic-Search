<div align="center">

# ⚡ Semantic Search & RAG Evaluation Studio

**Benchmarking Dense Vector Search (FAISS + MiniLM) vs. Classical BM25 Keyword Search**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19-61dafb?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8-646cff?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![FAISS](https://img.shields.io/badge/FAISS-CPU-blue?style=for-the-badge&logo=facebook&logoColor=white)](https://github.com/facebookresearch/faiss)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

</div>

---

## 📌 Overview

**Semantic Search & RAG Evaluation Studio** is a full-stack IR (Information Retrieval) system designed to compare and evaluate **Dense Vector Search** (`all-MiniLM-L6-v2` + FAISS) against **Sparse Keyword Search** (`rank-bm25`) side-by-side with real-time metrics (**Recall@k**, **MRR**, **NDCG@5**).

---

## ✨ Features

- ⚡ **Side-by-Side Retrieval**: Run semantic vector search and BM25 keyword search simultaneously.
- 🧬 **Sentence-Level Matching**: Find exact relevant sentences inside documents with match score highlighting.
- 📊 **IR Metrics Harness**: Compute Recall@1/3/5, MRR, and NDCG@5 using hand-labeled test sets.
- 📂 **4 Pre-built Corpora**: Ecology, ML Papers, FAQ/SQuAD, and Telecom Research.
- 📤 **Custom Ingestion**: Upload PDF, DOCX, TXT, or JSONL files to index on the fly.
- 🌐 **Unified Deployment**: Production React frontend served directly by FastAPI.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
|---|---|---|
| **Embeddings** | `sentence-transformers` | 384-dimensional dense vectors (`all-MiniLM-L6-v2`) |
| **Vector Search** | `FAISS` (CPU) | High-performance approximate nearest neighbor search |
| **Keyword Search** | `rank-bm25` | Probabilistic TF-IDF baseline retrieval |
| **Backend** | `FastAPI` + `Uvicorn` | High-concurrency REST API |
| **Frontend** | `React 19` + `Vite` + `Tailwind CSS` | Modern glassmorphism UI |

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/code-debugger214-cell/Semantic-Search.git
cd Semantic-Search

# Setup Python Virtual Environment
python -m venv venv
venv\Scripts\activate      # On Windows
# source venv/bin/activate # On macOS/Linux

pip install -r requirements.txt
```

### 2. Run Application

```bash
# Option A: Single Unified Production Server (Recommended)
python build_and_start.py
# 🚀 Access at: http://localhost:8000

# Option B: Development Mode
# Terminal 1 (Backend API):
uvicorn backend.main:app --reload --port 8000

# Terminal 2 (Frontend UI):
cd frontend && npm install && npm run dev
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/corpora` | List all available datasets |
| `POST` | `/api/search` | Execute side-by-side search (Semantic vs BM25) |
| `POST` | `/api/search-sentence` | Execute sentence-level vector search |
| `GET` | `/api/eval/{corpus}` | Fetch evaluation metrics (Recall, MRR, NDCG) |
| `POST` | `/api/upload` | Upload & index custom files |

> Interactive Swagger API docs are available at **`/docs`** when running the server.

---


## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
