"""
Embedder — turns text chunks into vectors using a pretrained model.

Generic by design: takes a list of strings, returns vectors. No corpus-
specific logic. Model name is a config value, not hardcoded per corpus.
"""
import numpy as np
from pathlib import Path

DEFAULT_MODEL = "all-MiniLM-L6-v2"

_model_cache = {}


def get_model(model_name: str = DEFAULT_MODEL):
    """Load (and cache) a sentence-transformers model by name."""
    if model_name not in _model_cache:
        from sentence_transformers import SentenceTransformer
        _model_cache[model_name] = SentenceTransformer(model_name)
    return _model_cache[model_name]


def embed_texts(texts: list[str], model_name: str = DEFAULT_MODEL) -> np.ndarray:
    """
    texts: list of chunk strings.
    Returns: numpy array of shape (len(texts), embedding_dim).
    """
    model = get_model(model_name)
    embeddings = model.encode(texts, show_progress_bar=len(texts) > 20)
    return np.asarray(embeddings, dtype="float32")


def save_embeddings(embeddings: np.ndarray, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(output_path, embeddings)


def load_embeddings(input_path: Path) -> np.ndarray:
    return np.load(input_path)


if __name__ == "__main__":
    # Smoke test — requires internet access to download the model once.
    sample = [
        "Machine learning improves biodiversity monitoring.",
        "AI helps track species populations in the wild.",
        "The stock market fell sharply today.",
    ]
    vecs = embed_texts(sample)
    print("Embedding shape:", vecs.shape)

    def cosine(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    print("Sim (related pair):", cosine(vecs[0], vecs[1]))
    print("Sim (unrelated pair):", cosine(vecs[0], vecs[2]))
