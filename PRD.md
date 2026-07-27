# PRD — Semantic Search with Retrieval Evaluation

## 1. Problem Statement
Keyword search (e.g. Ctrl+F, BM25) misses relevant results when a query uses
different words than the document, even if the meaning matches. This project
builds a semantic search engine (meaning-based retrieval) and rigorously
evaluates it against classical keyword search — rather than just assuming
"embeddings are better."

## 2. Goal
For a given corpus of documents, let a user search by meaning, not just
keywords, and demonstrate — with real metrics, not just a demo — where
semantic search wins, where keyword search wins, and where a hybrid of both
is best.

## 3. Non-Goals (explicitly out of scope for MVP)
- No training or fine-tuning of embedding models — use a pretrained model
  as a black box (matches current skill level; this is an evaluation/IR
  project, not a deep learning project).
- No hosted/production vector DB (Pinecone, Weaviate) — local FAISS index
  is sufficient for MVP.
- No live web-scale corpus — small, curated, bounded corpora only.
- Not a general-purpose product — a research/portfolio project with a
  Streamlit demo UI, not a deployed service.

## 4. MVP Scope
### Inputs
- A folder of text documents (the corpus) — corpus source TBD, one of:
  personal notes/papers, research abstracts, FAQ/Q&A dataset, Wikipedia
  articles. See memory.md "Open Questions" for current status.
- A user query (typed in Streamlit UI).

### Pipeline (per corpus, built once, offline)
1. Chunk documents (configurable chunk size/overlap).
2. Embed chunks with a pretrained model (`sentence-transformers`).
3. Build two indexes: FAISS (semantic/vector) and BM25 (keyword).
4. Hand-label a small eval set (10-15 queries with correct-document answers).

### Outputs (per query, online)
- Top-k results from semantic search.
- Top-k results from keyword (BM25) search.
- Shown side by side so the difference is visible, not just claimed.

### Outputs (evaluation, offline)
- Recall@k, MRR (Mean Reciprocal Rank), and NDCG for both methods, per
  corpus, plus a short written comparison of where each method wins.

## 5. Multi-Corpus Design
The pipeline is corpus-agnostic by construction — chunking, embedding,
indexing, and retrieval code takes a folder path and config values (chunk
size, model name) as parameters, never anything hardcoded to a specific
corpus's content or structure.
- Settings (chunk size, embedding model, corpus path) solve the
  "can it run on a new corpus" problem.
- They do NOT solve the "does it perform well on a new corpus" problem —
  that requires building a small labeled eval set and running the metrics,
  every time a new corpus is added. This is a manual step, not automatable.
- Target: 4 corpora total for MVP, selectable via a UI dropdown, each with
  its own pre-built index and its own small eval set.

## 6. Success Criteria (MVP)
- Full pipeline works end-to-end on at least one real corpus.
- Real Recall@k/MRR/NDCG numbers are produced and compared (not just a
  working demo with no evaluation).
- At least 2-3 corpora working via the dropdown before calling this "done";
  4 is the stretch target.

## 7. Positioning
- Framed honestly as an information retrieval (IR) + evaluation project —
  embeddings, vector similarity, retrieval metrics. Not a deep learning
  project (no model training), and not "just an LLM wrapper" like
  [[client-discovery-agent]] — this one has real experimental comparison
  and measurable results, which is the ML-adjacent rigor being aimed for.

## 8. Risks
- Building labeled eval sets by hand is tedious and easy to under-scope —
  budget real time for this (see phases.md).
- Chunking strategy affects results a lot; don't over-tune before you have
  a baseline number to compare against.
- Adding a 4th corpus "for completeness" can eat time better spent on
  eval rigor for the first 1-2 corpora — quality over corpus count if time
  runs short.
