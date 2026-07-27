"""
Phase 0 smoke test — run this locally to confirm the embedding model works.
Requires internet access (downloads model from Hugging Face on first run).
"""
from sentence_transformers import SentenceTransformer
import numpy as np

print("Loading model (first run downloads ~90MB, cached after)...")
model = SentenceTransformer('all-MiniLM-L6-v2')

sentences = [
    "Machine learning improves biodiversity monitoring.",
    "AI helps track species populations in the wild.",
    "The stock market fell sharply today.",
]

embeddings = model.encode(sentences)
print("Embedding shape:", embeddings.shape)  # expect (3, 384)

def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

sim_related = cosine_sim(embeddings[0], embeddings[1])
sim_unrelated = cosine_sim(embeddings[0], embeddings[2])

print(f"Similarity (ML+biodiversity vs AI+species): {sim_related:.3f}  <- should be HIGH")
print(f"Similarity (ML+biodiversity vs stock market): {sim_unrelated:.3f}  <- should be LOW")

assert sim_related > sim_unrelated, "Something's off — related sentences should score higher!"
print("\nPASS: semantic similarity behaves correctly. Phase 0 embedding check done.")
