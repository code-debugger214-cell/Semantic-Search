# Phases — Semantic Search with Retrieval Evaluation

## Phase 0 — Setup (0.5 day)
- Repo structure, virtual environment, install `sentence-transformers`,
  `faiss-cpu`, `rank_bm25`, `streamlit`, `numpy`.
- Confirm a pretrained embedding model loads and can embed a test sentence.

## Phase 1 — Pick and Prepare Corpus #1 (0.5-1 day)
- Finalize corpus #1 choice (see memory.md "Open Questions").
- Write the loader function for that corpus type (plain text folder, PDF
  folder, API pull — whichever applies).
- Confirm ~30-100 documents/chunks load cleanly as plain text.

## Phase 2 — Chunker + Embedder (1 day)
- Implement configurable chunking.
- Implement embedding via `sentence-transformers`.
- Sanity check: embed 2-3 known-similar sentences, confirm their vectors
  are close (cosine similarity) — smoke test before building the full index.

## Phase 3 — Indexes: FAISS + BM25 (1 day)
- Build both indexes from corpus #1's chunks.
- Save to disk under `corpus_store/<corpus_name>/`.
- Confirm a manual test query returns plausible results from both.

## Phase 4 — Retriever + Basic UI (1-2 days)
- `semantic_search()` and `keyword_search()` functions.
- Streamlit UI: corpus dropdown (just corpus #1 for now), query box,
  side-by-side results.

## Phase 5 — Labeled Eval Set + Eval Harness (2 days, don't shortcut)
- Hand-label 10-15 queries with correct-document answers for corpus #1.
- Implement Recall@k, MRR, NDCG computation.
- Run both methods through the harness, produce a metrics report.

## Phase 6 — Write-Up (0.5-1 day)
- Short written comparison: where semantic won, where keyword won, any
  surprises. This is what makes the project a real evaluation, not just a
  working demo.

## Phase 7 — Add Corpus #2 (1-2 days, should be fast if Phases 1-6 were
done generically)
- New loader (if new source type) + offline build + new eval set.
- No changes to chunker/embedder/indexer/retriever code — if changes are
  needed here, that's a signal Phase 1-6 leaked corpus-specific logic
  somewhere; fix that before adding corpus #3/#4.

## Phase 8 — Corpus #3 and #4 (stretch goal, 1-2 days each)
- Same pattern as Phase 7. Only pursue after Phase 7 confirms the pipeline
  is genuinely generic and fast to extend.

**MVP Total (Phases 0-6, one solid corpus): ~6-8 working days.**
**Stretch (adding 3 more corpora): +3-6 days.**

---
## Future Work (explicitly deferred)
- Hybrid BM25 + semantic scoring/reranking.
- Fine-tuning or training a custom embedding model.
- Hosted vector DB (Pinecone/Weaviate) for production-scale deployment.
- Connecting this as a RAG layer for [[client-discovery-agent]] — revisit
  only after both projects independently work.
