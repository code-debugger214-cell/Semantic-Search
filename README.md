# Semantic Search with Retrieval Evaluation

Embedding-based semantic search compared rigorously against classical
keyword search (BM25), evaluated with real IR metrics (Recall@k, MRR,
NDCG). Corpus #1: research paper abstracts (ecology/SDG-15 topic).

## Start here
1. Read `COMPLETE_PROJECT_DOC.md` first — single reference covering
   requirements, tech stack, architecture, and design in one place.
2. For deeper detail on any part, see the individual docs below.
3. Follow `phases.md` for the actual build order — don't skip ahead.

## Docs in this repo
- `PRD.md` — problem, goals, scope, success criteria
- `architecture.md` — system design, data flow, components
- `rules.md` — engineering guardrails (scope discipline, genericity, eval rigor)
- `phases.md` — build order, day-by-day plan, Future Work list
- `design.md` — UI flow, data schemas (Pydantic models)
- `memory.md` — decision log; update this as real decisions get made
- `COMPLETE_PROJECT_DOC.md` — everything above, consolidated into one file

## Project structure
```
semantic-search-eval/
  app/
    loaders/          # corpus-specific loaders (ONLY place corpus logic lives)
    chunker.py         # (to be built — Phase 2)
    embedder.py         # (to be built — Phase 2)
    indexing.py          # (to be built — Phase 3)
    retriever.py           # (to be built — Phase 4)
    eval.py                  # (to be built — Phase 5)
    ui.py                      # (to be built — Phase 4, Streamlit)
  data/
    raw/                # raw pulled abstracts, before chunking (Phase 1)
  corpus_store/        # built indexes + eval sets live here, per corpus
  notebooks/            # scratch exploration (chunk size tuning, sanity checks)
  tests/                  # basic unit tests for chunker/retriever/eval
  scripts/
    phase0_smoke_test.py   # verifies embedding model works locally
  requirements.txt
  .env.example
```

## Setup
```bash
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
python scripts/phase0_smoke_test.py
```

If the smoke test passes (prints embedding shape `(384,)` per sentence and
confirms related sentences score higher in similarity), Phase 0 is done —
move to Phase 1 in `phases.md`.

## Status
Not yet started (as of this zip). Corpus #1 chosen: research paper
abstracts (ecology/SDG-15). See `memory.md` for full decision log.
