# Rules — Semantic Search with Retrieval Evaluation

## 1. Scope Discipline
- No fine-tuning/training embedding models — pretrained models only, used
  as a black box. This is an IR/evaluation project, not a deep learning
  project, and that's an intentional scope boundary, not a limitation to
  "fix" later.
- Don't add a 4th (or 3rd) corpus until the eval rigor (labeled set +
  metrics) is solid on the first one. Corpus count is a stretch goal, not
  the primary success metric — see PRD.md §6.
- No hybrid BM25+semantic scoring algorithm until both methods work
  independently and are evaluated separately first.

## 2. Genericity Rules
- Chunker, embedder, indexer, retriever, and eval harness code must never
  contain corpus-specific logic (no "if corpus == X" branches, no
  hardcoded file names/paths outside config).
- The ONLY place corpus-specific code is allowed is in `app/loaders/` — one
  small loader function per corpus *type* (plain text, PDF, API pull), not
  per individual corpus.
- Every corpus-affecting setting (chunk size, overlap, embedding model
  name) must be a passed-in config value, never hardcoded inline.

## 3. Evaluation Rules (this is the core of the project — don't shortcut it)
- Every corpus added gets its own hand-labeled eval set of 10-15 queries
  with correct-document answers, before it's considered "working."
- Never claim "semantic search works well on this corpus" without a
  metrics report to back it up — a good-looking demo query is not evidence.
- Always compute and report metrics for BOTH methods (semantic and BM25),
  even when semantic is expected to win — the comparison is the point, not
  just showcasing embeddings.
- When metrics are ambiguous or close, say so plainly in the write-up
  rather than picking a winner to make the results look cleaner.

## 4. Code Rules
- FAISS/BM25 indexes are built offline (a build script), never rebuilt
  live inside the Streamlit app on every query.
- All corpus-specific artifacts (indexes, eval sets, metrics reports) live
  under `corpus_store/<corpus_name>/` — nothing corpus-specific lives in
  the main `app/` code tree.
- Config values (chunk size, model name, k for top-k) live in one place
  (e.g. a `config.py` or `.env`), not scattered across files.

## 5. Definition of "Done" for MVP
Not done until: at least one corpus has a full working pipeline (chunk →
embed → index → retrieve), a real hand-labeled eval set, and a metrics
report comparing semantic vs. keyword search — plus at least one additional
corpus proven to work via the same code with no pipeline changes.
