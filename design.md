# Design — Semantic Search with Retrieval Evaluation

## 1. User Flow (Streamlit)
1. Dropdown: "Select corpus" — lists corpora with a built index available.
2. Text box: "Enter your query."
3. Button: "Search."
4. Two columns render side by side:
   - **Semantic results** (top-k chunks, with similarity score, source file)
   - **Keyword results** (top-k chunks, with BM25 score, source file)
5. Optional second tab: "Evaluation Report" — shows the precomputed
   Recall@k / MRR / NDCG table for the selected corpus, plus the short
   written comparison from Phase 6.

## 2. Data Structures

```python
class Chunk(BaseModel):
    chunk_id: str
    text: str
    source_file: str
    chunk_index: int  # position within source file

class RetrievalResult(BaseModel):
    chunk: Chunk
    score: float
    method: Literal["semantic", "keyword"]

class EvalQuery(BaseModel):
    query: str
    correct_chunk_ids: list[str]  # hand-labeled ground truth

class MetricsReport(BaseModel):
    corpus_name: str
    method: Literal["semantic", "keyword"]
    recall_at_k: dict[int, float]  # e.g. {1: 0.4, 3: 0.6, 5: 0.8}
    mrr: float
    ndcg: float
```

## 3. UI Principles
- Always show both methods side by side — never hide the comparison behind
  a toggle. The comparison IS the product, not an afterthought.
- Show the raw score for each result (not just rank) so differences in
  confidence are visible, not just ranking order.
- Keep it plain — no styling investment beyond Streamlit defaults; this is
  an evaluation tool, not a polished product demo.

## 4. Labeling Guidance (for building each corpus's eval set)
- Write queries the way a real user would ask, not by copying phrases
  directly from the source document — otherwise keyword search gets an
  unfair advantage and the comparison stops being honest.
- Include a mix: some queries where the wording closely matches the
  source (keyword-friendly) and some paraphrased/synonym-heavy queries
  (semantic-friendly) — the eval set should be able to show both methods
  winning somewhere, not be built to favor one from the start.
