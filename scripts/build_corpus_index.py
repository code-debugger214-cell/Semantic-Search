"""
Build script — runs the offline pipeline (chunk -> embed -> index) for a
single corpus. Run this once per corpus, and again whenever the raw data
or chunking config changes.

Usage:
    python scripts/build_corpus_index.py \\
        --raw data/raw/ecology_abstracts.jsonl \\
        --corpus-name ecology_abstracts \\
        --text-field abstract \\
        --id-field id
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.chunker import chunk_documents, save_chunks
from app.embedder import embed_texts, save_embeddings
from app.indexing import build_and_save_indexes


def load_raw_documents(path: Path) -> list[dict]:
    docs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                docs.append(json.loads(line))
    return docs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True, help="Path to raw .jsonl file")
    parser.add_argument("--corpus-name", required=True, help="Name for this corpus")
    parser.add_argument("--text-field", default="abstract")
    parser.add_argument("--id-field", default="id")
    parser.add_argument("--chunk-size", type=int, default=300)
    parser.add_argument("--overlap", type=int, default=50)
    args = parser.parse_args()

    raw_path = Path(args.raw)
    corpus_dir = Path("corpus_store") / args.corpus_name

    print(f"Loading raw documents from {raw_path}...")
    documents = load_raw_documents(raw_path)
    print(f"Loaded {len(documents)} documents.")

    print("Chunking...")
    chunks = chunk_documents(
        documents,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
        text_field=args.text_field,
        id_field=args.id_field,
    )
    print(f"Produced {len(chunks)} chunks.")
    save_chunks(chunks, corpus_dir / "chunks.jsonl")

    print("Embedding (this may take a minute)...")
    chunk_texts = [c.text for c in chunks]
    embeddings = embed_texts(chunk_texts)
    save_embeddings(embeddings, corpus_dir / "embeddings.npy")

    print("Building indexes...")
    build_and_save_indexes(chunks, embeddings, corpus_dir)

    print(f"\nDone. Corpus '{args.corpus_name}' ready at {corpus_dir}")
    print(f"Try it: python app/retriever.py {corpus_dir}")


if __name__ == "__main__":
    main()
