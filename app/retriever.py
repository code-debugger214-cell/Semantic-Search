"""
Retriever — runs semantic (FAISS) and keyword (BM25) search over a
corpus's saved indexes, returning results in a common format.

Generic by design: takes a corpus directory + query, returns results.
No corpus-specific logic here.
"""
from dataclasses import dataclass
from pathlib import Path
import sys
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.chunker import load_chunks
from app.indexing import load_faiss_index, load_bm25_index
from app.embedder import embed_texts


@dataclass
class RetrievalResult:
    chunk_id: str
    text: str
    source_file: str
    score: float
    method: str  # "semantic" or "keyword"


class CorpusRetriever:
    """Loads a corpus's chunks + both indexes once, then answers queries."""

    def __init__(self, corpus_dir: Path):
        self.corpus_dir = corpus_dir
        self.chunks = load_chunks(corpus_dir / "chunks.jsonl")
        self.faiss_index = load_faiss_index(corpus_dir / "embeddings.faiss")
        self.bm25_index = load_bm25_index(corpus_dir / "bm25.pkl")

    def semantic_search(self, query: str, k: int = 5) -> list[RetrievalResult]:
        query_vec = embed_texts([query])[0]
        norm = np.linalg.norm(query_vec)
        if norm > 0:
            query_vec = query_vec / norm

        scores, indices = self.faiss_index.search(
            query_vec.reshape(1, -1).astype("float32"), k
        )

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            chunk = self.chunks[idx]
            results.append(RetrievalResult(
                chunk_id=chunk.chunk_id,
                text=chunk.text,
                source_file=chunk.source_file,
                score=float(score),
                method="semantic",
            ))
        return results

    def keyword_search(self, query: str, k: int = 5) -> list[RetrievalResult]:
        tokenized_query = query.lower().split()
        scores = self.bm25_index.get_scores(tokenized_query)
        top_k_idx = np.argsort(scores)[::-1][:k]

        results = []
        for idx in top_k_idx:
            chunk = self.chunks[idx]
            results.append(RetrievalResult(
                chunk_id=chunk.chunk_id,
                text=chunk.text,
                source_file=chunk.source_file,
                score=float(scores[idx]),
                method="keyword",
            ))
        return results


if __name__ == "__main__":
    # This smoke test requires a real built corpus to exist — run after
    # Phase 3's build script has been run on real data.
    import sys
    if len(sys.argv) < 2:
        print("Usage: python app/retriever.py <corpus_dir>")
        sys.exit(1)

    retriever = CorpusRetriever(Path(sys.argv[1]))
    query = "how does climate change affect species migration"

    print("=== Semantic results ===")
    for r in retriever.semantic_search(query, k=3):
        print(f"[{r.score:.3f}] {r.text[:100]}...")

    print("\n=== Keyword results ===")
    for r in retriever.keyword_search(query, k=3):
        print(f"[{r.score:.3f}] {r.text[:100]}...")
