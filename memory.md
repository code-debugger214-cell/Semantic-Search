# Memory / Decision Log — Semantic Search with Retrieval Evaluation

Purpose: running log so any future session (you, or an AI coding assistant)
can pick this project back up without re-deriving context. Update on real
decisions, not routine progress — that belongs in commit messages.

## Status
- Current phase: Phases 2-4 code written (chunker, embedder, indexing,
  retriever, build script). Chunker + indexing smoke-tested successfully
  in sandbox (fake data). Embedder untestable in sandbox (no network
  access to Hugging Face) — needs local run. Corpus pull script
  (`scripts/pull_corpus.py`) written, not yet successfully run with a
  full real corpus (was returning too few abstracts — script now has
  debug output + fallback query to diagnose/fix this).
- Next concrete step: run `pull_corpus.py` locally, confirm a real corpus
  of 50+ abstracts lands in `data/raw/`, then run
  `scripts/build_corpus_index.py` to build the actual FAISS+BM25 indexes,
  then test `app/retriever.py` on real queries.

## Key Decisions Made (and why)
- **No fine-tuning/training of embedding models.** Pretrained model used as
  a black box (`sentence-transformers`, default `all-MiniLM-L6-v2`) — this
  is intentional given current skill level (deep learning not yet learned)
  and keeps the project's rigor focused on evaluation methodology, not
  model training.
- **Local FAISS, not a hosted vector DB.** No need for production-scale
  infra at this project's size.
- **Comparison-first design.** The project's whole value is comparing
  semantic vs. keyword search with real metrics — not just building a
  working semantic search demo. Every corpus added must get its own
  labeled eval set; this is treated as core work, not optional polish.
- **Genericity enforced via `app/loaders/`.** Only corpus-specific code
  lives there (one loader per corpus *type*); everything downstream
  (chunk/embed/index/retrieve/eval) is shared and must never branch on
  corpus identity.
- **4 corpora is a stretch goal, not the MVP bar.** One corpus done
  rigorously (real eval, real metrics) matters more than four corpora done
  shallowly. See rules.md §1.
- **Positioned as a separate project from [[client-discovery-agent]]** —
  that project stays pure LLM/product engineering; this one carries the
  "real ML/IR evaluation" story. A future RAG tie-in between them is
  explicitly deferred (see phases.md Future Work).

## Open Questions (revisit before the relevant phase)
- Final corpus #1 choice — must be resolved before Phase 1.
- Exact chunk size/overlap defaults — decide empirically in Phase 2/3, not
  in advance.
- Whether `all-MiniLM-L6-v2` is sufficient or a stronger model is worth
  trying — decide only after seeing Phase 5 metrics on corpus #1.

## Do Not Re-Open Without a Real Reason
- Any Future Work item in phases.md (hybrid scoring, fine-tuning, hosted
  vector DB, RAG tie-in to the discovery agent).
