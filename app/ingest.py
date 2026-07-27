"""
Ingestion Engine — Takes parsed documents, chunks them, embeds with Sentence-Transformers,
builds FAISS + BM25 indexes, and saves the new corpus store.
"""
import json
import re
from pathlib import Path
import sys
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.chunker import chunk_documents, save_chunks
from app.embedder import embed_texts, save_embeddings
from app.indexing import build_and_save_indexes
from backend.file_parsers import parse_file


CATEGORY_CHUNK_DEFAULTS = {
    "Research Papers": {"chunk_size": 400, "overlap": 75},
    "FAQs & Web": {"chunk_size": 200, "overlap": 30},
    "Personal Notes": {"chunk_size": 300, "overlap": 50},
    "General": {"chunk_size": 300, "overlap": 50},
}


def sanitize_corpus_name(name: str) -> str:
    """Sanitizes user input corpus name into clean directory slug."""
    clean = re.sub(r'[^a-zA-Z0-9_\-]', '_', name.strip().lower())
    return re.sub(r'_+', '_', clean).strip('_')


def build_corpus_from_documents(
    documents: List[Dict[str, Any]],
    corpus_name: str,
    category: str = "General",
    chunk_size: Optional[int] = None,
    overlap: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Core ingestion function:
    1. Chunks documents
    2. Generates embeddings via sentence-transformers
    3. Builds & saves FAISS index + BM25 index
    4. Generates initial starter eval_set.json
    """
    slug = sanitize_corpus_name(corpus_name)
    if not slug:
        raise ValueError("Invalid corpus name.")

    corpus_dir = Path("corpus_store") / slug
    corpus_dir.mkdir(parents=True, exist_ok=True)

    # Save raw document JSONL in data/raw for persistence
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_jsonl_path = raw_dir / f"{slug}.jsonl"

    with open(raw_jsonl_path, "w", encoding="utf-8") as f:
        for doc in documents:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    # Determine chunk parameters
    defaults = CATEGORY_CHUNK_DEFAULTS.get(category, CATEGORY_CHUNK_DEFAULTS["General"])
    c_size = chunk_size or defaults["chunk_size"]
    c_overlap = overlap or defaults["overlap"]

    # 1. Chunk documents
    chunks = chunk_documents(
        documents,
        chunk_size=c_size,
        overlap=c_overlap,
        text_field="abstract",
        id_field="id"
    )

    if not chunks:
        raise ValueError("No text chunks could be extracted from the uploaded files.")

    # 2. Save chunks
    chunks_path = corpus_dir / "chunks.jsonl"
    save_chunks(chunks, chunks_path)

    # 3. Embed chunks
    chunk_texts = [c.text for c in chunks]
    embeddings = embed_texts(chunk_texts)

    # 4. Save numpy embeddings
    save_embeddings(embeddings, corpus_dir / "embeddings.npy")

    # 5. Build & save FAISS + BM25 indexes
    build_and_save_indexes(chunks, embeddings, corpus_dir)

    # 6. Generate starter eval_set.json template from documents
    eval_queries = []
    for doc in documents[:10]:
        title = doc.get("title", "")
        abstract = doc.get("abstract", "")
        first_sentence = abstract.split(".")[0] if abstract else title
        if len(first_sentence) > 15:
            eval_queries.append({
                "query": f"What document discusses {first_sentence.lower()}?",
                "correct_title": title,
                "correct_id": str(doc.get("id"))
            })

    eval_set = {
        "corpus_name": slug,
        "category": category,
        "queries": eval_queries
    }

    with open(corpus_dir / "eval_set.json", "w", encoding="utf-8") as f:
        json.dump(eval_set, f, indent=2, ensure_ascii=False)

    return {
        "corpus_name": slug,
        "corpus_dir": str(corpus_dir),
        "total_documents": len(documents),
        "total_chunks": len(chunks),
        "embedding_dim": int(embeddings.shape[1]),
        "chunk_size": c_size,
        "overlap": c_overlap,
    }


def process_uploaded_files_and_build(
    uploaded_files: List[tuple[bytes, str]],  # (bytes, filename)
    corpus_name: str,
    category: str = "General",
    chunk_size: Optional[int] = None,
    overlap: Optional[int] = None,
) -> Dict[str, Any]:
    """Takes a list of (file_bytes, filename) tuples and ingests them."""
    all_documents = []
    for file_bytes, filename in uploaded_files:
        parsed_docs = parse_file(file_bytes, filename)
        all_documents.extend(parsed_docs)

    if not all_documents:
        raise ValueError("No valid text could be parsed from any of the provided files.")

    return build_corpus_from_documents(
        all_documents,
        corpus_name=corpus_name,
        category=category,
        chunk_size=chunk_size,
        overlap=overlap
    )


if __name__ == "__main__":
    sample_files = [
        (b"Machine learning enables scalable vector search for unstructured documents.", "sample_doc1.txt"),
        (b"BM25 is a term-frequency inverted index search algorithm.", "sample_doc2.txt")
    ]
    res = process_uploaded_files_and_build(sample_files, "test_ingest_corpus", "General")
    print("Ingest result:", res)
