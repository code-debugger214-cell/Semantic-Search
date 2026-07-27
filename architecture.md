# Architecture — Semantic Search with Retrieval Evaluation

## 1. High-Level Flow

### Offline (build once per corpus)
```
[Raw corpus folder] --> [Chunker] --> [Embedder (sentence-transformers)]
                                            |
                                            v
                              [FAISS index]   [BM25 index]
                                (semantic)      (keyword)
```

### Online (per query)
```
[Streamlit UI: corpus dropdown + query box]
        |
        v
[Load selected corpus's FAISS + BM25 indexes]
        |
        v
[Retrieve top-k from both methods]
        |
        v
[Results view: semantic results | keyword results, side by side]
```

### Evaluation (the ML rigor)
```
[Labeled eval set per corpus: 10-15 queries + correct doc(s)]
        |
        v
[Eval harness runs both retrieval methods over eval set]
        |
        v
[Metrics report: Recall@k, MRR, NDCG — per corpus, per method]
```

## 2. Components

### 2.1 Chunker (`app/chunker.py`)
- Input: folder of `.txt`/`.md` files (or a loader per corpus type — see
  2.5). Output: list of chunks with metadata (source file, chunk index).
- Config: `chunk_size`, `overlap` — passed in, never hardcoded per corpus.

### 2.2 Embedder (`app/embedder.py`)
- Wraps `sentence-transformers` (default model: `all-MiniLM-L6-v2` — small,
  fast, no training required, good general-purpose baseline).
- Input: list of chunk texts. Output: list of vectors (numpy arrays).
- Model name is a config value, not hardcoded — swappable per corpus if
  needed later.

### 2.3 Indexers (`app/indexing.py`)
- FAISS index: stores chunk embeddings, supports nearest-neighbor search
  (cosine similarity).
- BM25 index: `rank_bm25` library, stores tokenized chunk text.
- Both saved to disk per corpus (`corpus_store/<corpus_name>/`), built once
  offline, loaded (not rebuilt) at query time.

### 2.4 Retriever (`app/retriever.py`)
- `semantic_search(query, corpus_name, k)` → top-k chunks via FAISS.
- `keyword_search(query, corpus_name, k)` → top-k chunks via BM25.
- Both return chunk text + source file + score, in a common result format
  so the UI can render them identically regardless of method.

### 2.5 Corpus Loaders (`app/loaders/`)
- One small loader function per corpus type (plain text folder, PDF folder,
  Wikipedia API pull, arXiv abstract pull) — this is the ONLY place that
  differs per corpus type. Everything downstream (chunker onward) is
  identical regardless of source.

### 2.6 Eval Harness (`app/eval.py`)
- Input: a corpus's eval set (JSON: list of `{query, correct_doc_ids}`).
- Runs both `semantic_search` and `keyword_search` for every eval query.
- Computes Recall@k, MRR, NDCG for each method.
- Outputs a comparison table/report per corpus.

### 2.7 Frontend (Streamlit, `app/ui.py`)
- Dropdown: select corpus (lists whatever corpora have a built index in
  `corpus_store/`).
- Query box → runs both retrieval methods → renders results side by side.
- Optional: a small "Evaluation Results" tab showing the metrics report
  per corpus (static, precomputed — not run live per click).

## 3. Data Layout
```
corpus_store/
  <corpus_name>/
    chunks.jsonl        # chunk text + metadata
    embeddings.faiss    # FAISS index file
    bm25.pkl            # serialized BM25 index
    eval_set.json        # hand-labeled queries + correct doc ids
    metrics_report.json  # precomputed Recall@k/MRR/NDCG results
```
Adding a new corpus = write one loader function (if a new source type) +
run the offline build script + hand-label an eval set. No changes to
chunker, embedder, indexer, retriever, or eval harness code.

## 4. What Is Deliberately NOT in v1
- No fine-tuning/training of embedding models.
- No hosted vector DB — FAISS local files are enough at this scale.
- No live re-embedding on every query — indexes are precomputed offline.
- No hybrid-scoring algorithm (combining BM25 + semantic scores into one
  ranked list) in MVP — show both side by side first; a hybrid combiner is
  a natural Future Work extension once both work independently.

## 5. Tech Stack (confirmed)
Python, `sentence-transformers`, FAISS (`faiss-cpu`), `rank_bm25`,
Streamlit, numpy, standard Python for chunking/loaders/eval harness.
