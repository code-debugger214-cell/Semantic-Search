# Semantic Search with Retrieval Evaluation — Complete Project Document

## 1. Overview

A search engine that retrieves documents by **meaning**, not just keyword
matching, built over a corpus of research paper abstracts (ecology/SDG-15
topic). It is evaluated rigorously against classical keyword search (BM25)
using real retrieval metrics — the comparison itself is the point of the
project, not just building a working semantic search demo.

Positioned as an **information retrieval (IR) + evaluation** project.
Deliberately not a deep learning project — no model training/fine-tuning;
a pretrained embedding model is used as a black box. This is an intentional
scope boundary given current skill level, not a limitation to fix later.

---

## 2. Non-Technical Requirements

- **Purpose:** demonstrate real ML/IR evaluation skill — a measurable,
  defensible result ("semantic search improves Recall@5 by X% over BM25 on
  paraphrased queries"), not just a working feature.
- **Audience:** portfolio/resume project — reviewed by technical people
  (interviewers, mentors), so the write-up and metrics matter as much as
  the working demo.
- **Honesty requirement:** never claim one method "wins" without a metrics
  report backing it up. If results are close or ambiguous, say so plainly.
- **Positioning:** kept separate from [[client-discovery-agent]] (which
  stays pure LLM/product engineering) — this project carries the "real
  ML/IR" story in the portfolio.
- **Scope discipline:** one corpus done rigorously (real eval, real
  metrics) matters more than four corpora done shallowly. Corpus count is
  a stretch goal, not the MVP bar.

---

## 3. Technical Requirements

### Functional
1. Ingest a folder of research paper abstracts (corpus #1: ecology/SDG-15).
2. Chunk documents (configurable size/overlap).
3. Generate embeddings for each chunk using a pretrained model.
4. Build two retrieval indexes: FAISS (semantic/vector) and BM25 (keyword).
5. Accept a user query, return top-k results from both methods, shown side
   by side.
6. Maintain a hand-labeled evaluation set (10-15 queries + correct-document
   answers) per corpus.
7. Compute Recall@k, MRR, and NDCG for both retrieval methods.
8. Support adding additional corpora without changing pipeline code — only
   a new loader function (per corpus *type*) and a new offline build run.

### Non-Functional
- Indexes are built **offline** (once per corpus), never rebuilt live on
  every query — keeps the UI responsive.
- Pipeline code (chunker, embedder, indexer, retriever, eval harness) must
  contain **no corpus-specific logic** — genericity is enforced by design,
  not by convention.
- No training/fine-tuning of any model — pretrained embeddings only.
- No hosted vector DB / production infra required — local FAISS files are
  sufficient at this scale.

---

## 4. Features

| Feature | Description |
|---|---|
| Corpus dropdown | Select which corpus to search (stretch goal: 4 corpora) |
| Semantic search | Retrieve top-k chunks by embedding similarity |
| Keyword search | Retrieve top-k chunks via BM25 |
| Side-by-side results | Both methods' results shown together, with scores |
| Evaluation report | Precomputed Recall@k / MRR / NDCG per corpus, per method |
| Written comparison | Short analysis: where each method wins, and why |

**Explicitly deferred (Future Work):** hybrid BM25+semantic reranking,
fine-tuning a custom embedding model, hosted vector DB, RAG tie-in to
[[client-discovery-agent]].

---

## 5. Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2` default) | Pretrained, free, local, no training needed |
| Vector index | FAISS (`faiss-cpu`) | Local, no infra, fast nearest-neighbor search |
| Keyword index | `rank_bm25` | Simple, effective classical baseline |
| Frontend | Streamlit | Fast to build, no separate frontend skillset needed |
| Data validation | Pydantic | Structured result/eval-set schemas |
| Corpus source | Semantic Scholar API (or arXiv API) | Pulling ecology/SDG-15 abstracts |
| Core language | Python, numpy | Everything glues together here |

### Tech Stack Concepts (what each piece actually does, plainly)
- **Embedding model:** turns text into a list of numbers ("coordinates in
  meaning-space") so similar meanings end up numerically close together.
- **FAISS:** a library that efficiently finds "which stored vectors are
  closest to this query vector" — the engine behind semantic search.
- **BM25:** a classical statistical keyword-matching algorithm — the
  modern, better-tuned version of "Ctrl+F with word frequency weighting."
- **Recall@k:** out of all correct answers, what fraction were found in
  the top k results?
- **MRR (Mean Reciprocal Rank):** on average, how high up (1st, 2nd, 5th
  place) was the first correct answer?
- **NDCG:** like Recall/MRR but accounts for *how well-ranked* multiple
  correct answers are, not just whether they appear.

---

## 6. Architecture

### Offline (build once per corpus)
```
[Raw corpus folder] --> [Chunker] --> [Embedder] --> [FAISS index]
                                                   --> [BM25 index]
```

### Online (per query)
```
[Streamlit: corpus dropdown + query box]
   --> [Load selected corpus's FAISS + BM25 indexes]
   --> [Retrieve top-k, both methods]
   --> [Results view: semantic | keyword, side by side]
```

### Evaluation
```
[Labeled eval set per corpus] --> [Eval harness runs both methods]
   --> [Metrics report: Recall@k, MRR, NDCG per corpus, per method]
```

### Data Layout
```
corpus_store/
  <corpus_name>/
    chunks.jsonl          # chunk text + metadata
    embeddings.faiss      # FAISS index file
    bm25.pkl              # serialized BM25 index
    eval_set.json         # hand-labeled queries + correct answers
    metrics_report.json   # precomputed Recall@k / MRR / NDCG
```

### Components
- **Chunker** (`app/chunker.py`) — configurable chunk size/overlap, no
  corpus-specific logic.
- **Embedder** (`app/embedder.py`) — wraps `sentence-transformers`, model
  name is a config value.
- **Indexers** (`app/indexing.py`) — builds/saves FAISS + BM25 indexes.
- **Retriever** (`app/retriever.py`) — `semantic_search()` and
  `keyword_search()`, common result format for both.
- **Loaders** (`app/loaders/`) — the ONLY place corpus-specific code
  lives; one loader per corpus *type* (API pull, PDF folder, plain text).
- **Eval harness** (`app/eval.py`) — runs both methods over a corpus's
  eval set, computes metrics.
- **Frontend** (`app/ui.py`, Streamlit) — dropdown, query box, results,
  evaluation report tab.

---

## 7. Design — Data Structures

```python
class Chunk(BaseModel):
    chunk_id: str
    text: str
    source_file: str
    chunk_index: int

class RetrievalResult(BaseModel):
    chunk: Chunk
    score: float
    method: Literal["semantic", "keyword"]

class EvalQuery(BaseModel):
    query: str
    correct_chunk_ids: list[str]

class MetricsReport(BaseModel):
    corpus_name: str
    method: Literal["semantic", "keyword"]
    recall_at_k: dict[int, float]
    mrr: float
    ndcg: float
```

## 8. Design — User Flow
1. Select corpus from dropdown.
2. Enter a query.
3. View semantic and keyword results side by side (chunk text, source,
   score).
4. Optional: view the Evaluation Report tab for precomputed metrics and
   written comparison for the selected corpus.

## 9. Design Principles
- Always show both retrieval methods together — the comparison is the
  product, not a hidden toggle.
- Eval queries must include a mix of exact-wording and paraphrased/synonym
  queries — don't build an eval set that's secretly biased toward one
  method winning.
- Keep UI plain — this is an evaluation tool, not a polished consumer app.

---

## 10. Build Phases (summary)
1. Setup — env, dependencies, smoke-test embedding model.
2. Pull corpus #1 (ecology/SDG-15 abstracts via API).
3. Chunker + embedder, sanity-check similar sentences cluster correctly.
4. Build FAISS + BM25 indexes, manual test query.
5. Retriever + basic Streamlit UI (single corpus).
6. Hand-label eval set (10-15 queries) + eval harness + metrics report.
7. Written comparison of results.
8. (Stretch) Add corpus #2, #3, #4 — should be fast if genericity held.

**MVP estimate: 6-8 working days. Stretch (3 more corpora): +3-6 days.**

---

## 11. Key Decisions Log
- No fine-tuning/training — pretrained embeddings only, appropriate given
  deep learning not yet learned.
- Local FAISS, not a hosted vector DB — no production-scale need at this
  size.
- Comparison-first: every corpus gets its own labeled eval set; this is
  core work, not optional polish.
- Genericity enforced structurally — only `app/loaders/` may contain
  corpus-specific code.
- 4 corpora is a stretch goal — 1 corpus done rigorously is the real bar.
- Kept as a separate project from [[client-discovery-agent]] to avoid
  diluting either project's story (this one = ML/IR rigor, that one =
  product/LLM engineering).
