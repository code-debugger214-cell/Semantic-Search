"""
FastAPI REST Server & Production SPA Server — RAG & Retrieval Studio.

Endpoints:
- GET  /api/corpora           : List available indexed corpora & metadata
- POST /api/search            : Side-by-side comparative retrieval (Semantic vs BM25)
- POST /api/search-sentence   : Sentence-level semantic search with semantic meaning explainer
- GET  /api/documents/{corpus}: List unique document IDs in a corpus
- GET  /api/eval/{corpus_name}: IR evaluation metrics (Recall@k, MRR, NDCG@5)
- POST /api/upload            : Universal multi-file upload & on-the-fly indexing
- GET  /api/chunks/{corpus_name}: Browse corpus chunks

Production:
- Serves compiled React frontend static files from frontend/dist
"""
import json
from pathlib import Path
import sys
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.retriever import CorpusRetriever
from app.eval import evaluate_corpus
from app.ingest import process_uploaded_files_and_build, sanitize_corpus_name
from backend.sentence_search import search_sentences_in_corpus

app = FastAPI(
    title="RAG & Retrieval Evaluation API",
    description="Backend API & Unified Production Server for Semantic Vector Search (FAISS + MiniLM) vs BM25 Keyword Search.",
    version="2.2.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache loaded retrievers in memory
RETRIEVER_CACHE: Dict[str, CorpusRetriever] = {}


def get_retriever(corpus_name: str) -> CorpusRetriever:
    clean_name = sanitize_corpus_name(corpus_name)
    corpus_dir = Path("corpus_store") / clean_name

    if not corpus_dir.exists() or not (corpus_dir / "embeddings.faiss").exists():
        raise HTTPException(status_code=404, detail=f"Corpus '{corpus_name}' not found or index not built.")

    if clean_name not in RETRIEVER_CACHE:
        RETRIEVER_CACHE[clean_name] = CorpusRetriever(corpus_dir)

    return RETRIEVER_CACHE[clean_name]


# ---------------------------------------------------------
# API Data Models
# ---------------------------------------------------------
class SearchRequest(BaseModel):
    corpus_name: str
    query: str
    top_k: int = 5


class SentenceSearchRequest(BaseModel):
    corpus_name: str
    query_sentence: str
    target_doc_id: Optional[str] = None
    top_k: int = 5


class RetrievalResultItem(BaseModel):
    rank: int
    chunk_id: str
    text: str
    source_file: str
    score: float
    method: str


class SearchResponse(BaseModel):
    semantic_results: List[RetrievalResultItem]
    keyword_results: List[RetrievalResultItem]
    overlap_count: int
    overlap_percentage: float
    query_word_count: int


# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------
@app.get("/api/health")
def health_check():
    return {"message": "RAG & IR Evaluation Studio API is online", "status": "running"}


@app.get("/api/corpora")
def list_corpora():
    """Lists all available indexed corpora in corpus_store/."""
    corpus_store_dir = Path("corpus_store")
    if not corpus_store_dir.exists():
        return {"corpora": []}

    results = []
    for item in corpus_store_dir.iterdir():
        if item.is_dir() and (item / "chunks.jsonl").exists():
            chunks_path = item / "chunks.jsonl"
            doc_ids = set()
            chunk_count = 0
            with open(chunks_path, "r", encoding="utf-8") as f:
                for line in f:
                    chunk_count += 1
                    try:
                        data = json.loads(line)
                        doc_ids.add(data.get("source_file"))
                    except Exception:
                        pass

            eval_file = item / "eval_set.json"
            if not eval_file.exists():
                eval_file = item / "eval_set_by_id.json"

            results.append({
                "corpus_name": item.name,
                "display_name": item.name.replace("_", " ").title(),
                "total_chunks": chunk_count,
                "total_documents": len(doc_ids),
                "has_eval_set": eval_file.exists(),
                "embedding_model": "all-MiniLM-L6-v2",
                "vector_dimension": 384,
            })

    return {"corpora": results}


@app.get("/api/documents/{corpus_name}")
def list_documents(corpus_name: str):
    """Lists all unique document IDs in a given corpus."""
    retriever = get_retriever(corpus_name)
    doc_map = {}
    for c in retriever.chunks:
        doc_id = c.source_file
        if doc_id not in doc_map:
            preview = c.text[:80].strip() + "..."
            doc_map[doc_id] = {
                "doc_id": doc_id,
                "preview": preview,
            }
    return {"documents": list(doc_map.values())}


@app.post("/api/search", response_model=SearchResponse)
def search(req: SearchRequest):
    """Executes side-by-side comparative search (Semantic vs BM25)."""
    retriever = get_retriever(req.corpus_name)

    sem_res = retriever.semantic_search(req.query, k=req.top_k)
    kw_res = retriever.keyword_search(req.query, k=req.top_k)

    semantic_items = [
        RetrievalResultItem(
            rank=i + 1,
            chunk_id=r.chunk_id,
            text=r.text,
            source_file=r.source_file,
            score=float(r.score),
            method="semantic"
        ) for i, r in enumerate(sem_res)
    ]

    keyword_items = [
        RetrievalResultItem(
            rank=i + 1,
            chunk_id=r.chunk_id,
            text=r.text,
            source_file=r.source_file,
            score=float(r.score),
            method="keyword"
        ) for i, r in enumerate(kw_res)
    ]

    sem_ids = [r.source_file for r in sem_res]
    kw_ids = [r.source_file for r in kw_res]
    overlap = set(sem_ids).intersection(set(kw_ids))
    overlap_count = len(overlap)
    overlap_pct = (overlap_count / req.top_k) * 100 if req.top_k > 0 else 0.0

    return SearchResponse(
        semantic_results=semantic_items,
        keyword_results=keyword_items,
        overlap_count=overlap_count,
        overlap_percentage=round(overlap_pct, 1),
        query_word_count=len(req.query.split())
    )


@app.post("/api/search-sentence")
def search_sentence(req: SentenceSearchRequest):
    """Searches for semantically matching sentences inside document(s)."""
    retriever = get_retriever(req.corpus_name)
    results = search_sentences_in_corpus(
        retriever=retriever,
        query_sentence=req.query_sentence,
        target_doc_id=req.target_doc_id if req.target_doc_id != "all" else None,
        top_k=req.top_k
    )
    return {
        "corpus_name": req.corpus_name,
        "query_sentence": req.query_sentence,
        "results_count": len(results),
        "sentence_matches": results
    }


@app.get("/api/eval/{corpus_name}")
def get_evaluation(corpus_name: str):
    """Returns Recall@k, MRR, and NDCG@5 metrics for a corpus."""
    clean_name = sanitize_corpus_name(corpus_name)
    corpus_dir = Path("corpus_store") / clean_name

    if not corpus_dir.exists():
        raise HTTPException(status_code=404, detail="Corpus not found")

    try:
        metrics = evaluate_corpus(corpus_dir)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/upload")
async def upload_and_index(
    corpus_name: str = Form(...),
    category: str = Form("General"),
    chunk_size: Optional[int] = Form(None),
    overlap: Optional[int] = Form(None),
    files: List[UploadFile] = File(...)
):
    """Universal upload endpoint accepting multi-format files and indexing on the fly."""
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    file_tuples = []
    for file in files:
        content = await file.read()
        file_tuples.append((content, file.filename))

    try:
        result = process_uploaded_files_and_build(
            uploaded_files=file_tuples,
            corpus_name=corpus_name,
            category=category,
            chunk_size=chunk_size,
            overlap=overlap
        )
        slug = result["corpus_name"]
        RETRIEVER_CACHE.pop(slug, None)

        return {
            "message": "Corpus successfully processed and indexed!",
            "details": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@app.get("/api/chunks/{corpus_name}")
def get_chunks(
    corpus_name: str,
    search: Optional[str] = Query(None),
    limit: int = Query(50)
):
    """Returns chunks for inspection."""
    retriever = get_retriever(corpus_name)
    chunks = retriever.chunks

    if search:
        s_lower = search.lower()
        chunks = [c for c in chunks if s_lower in c.text.lower()]

    chunks_data = [
        {
            "chunk_id": c.chunk_id,
            "text": c.text,
            "source_file": c.source_file,
            "chunk_index": c.chunk_index,
            "word_count": len(c.text.split())
        } for c in chunks[:limit]
    ]

    return {
        "total_matches": len(chunks),
        "returned": len(chunks_data),
        "chunks": chunks_data
    }


# ---------------------------------------------------------
# Static File Mounting for Unified Production Build
# ---------------------------------------------------------
dist_dir = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if dist_dir.exists():
    app.mount("/assets", StaticFiles(directory=dist_dir / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")
        file_path = dist_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(dist_dir / "index.html")
else:
    @app.get("/")
    def fallback_root():
        return {"message": "FastAPI API Server Online. (Frontend build not found at frontend/dist)"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
