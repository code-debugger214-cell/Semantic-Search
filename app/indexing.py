"""
Indexing — builds and saves FAISS (semantic) and BM25 (keyword) indexes.

Generic by design: takes chunks + embeddings, writes index files to a
given corpus directory. No corpus-specific logic here.
"""
import pickle
import numpy as np
from pathlib import Path


def build_faiss_index(embeddings: np.ndarray):
    import faiss
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # inner product ~ cosine sim if vectors are normalized
    # Normalize so inner product behaves like cosine similarity.
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10
    normalized = embeddings / norms
    index.add(normalized)
    return index


def save_faiss_index(index, path: Path) -> None:
    import faiss
    path.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(path))


def load_faiss_index(path: Path):
    import faiss
    return faiss.read_index(str(path))


def build_bm25_index(chunk_texts: list[str]):
    from rank_bm25 import BM25Okapi
    tokenized = [text.lower().split() for text in chunk_texts]
    return BM25Okapi(tokenized)


def save_bm25_index(bm25, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(bm25, f)


def load_bm25_index(path: Path):
    with open(path, "rb") as f:
        return pickle.load(f)


def build_and_save_indexes(chunks, embeddings: np.ndarray, corpus_dir: Path) -> None:
    """
    chunks: list of Chunk objects (from chunker.py)
    embeddings: numpy array aligned with chunks (same order, same length)
    corpus_dir: e.g. Path("corpus_store/ecology_abstracts")
    """
    assert len(chunks) == len(embeddings), \
        "chunks and embeddings must be the same length and same order"

    faiss_index = build_faiss_index(embeddings)
    save_faiss_index(faiss_index, corpus_dir / "embeddings.faiss")

    chunk_texts = [c.text for c in chunks]
    bm25_index = build_bm25_index(chunk_texts)
    save_bm25_index(bm25_index, corpus_dir / "bm25.pkl")

    print(f"Saved FAISS index ({len(chunks)} vectors) and BM25 index "
          f"to {corpus_dir}")


if __name__ == "__main__":
    # Smoke test with fake data — no real corpus needed.
    fake_embeddings = np.random.rand(10, 384).astype("float32")
    idx = build_faiss_index(fake_embeddings)
    D, I = idx.search(fake_embeddings[:1], k=3)
    print("FAISS smoke test — nearest indices:", I)

    fake_texts = [f"sample text number {i} about biodiversity" for i in range(10)]
    bm25 = build_bm25_index(fake_texts)
    scores = bm25.get_scores("biodiversity sample".split())
    print("BM25 smoke test — scores:", scores[:5])
