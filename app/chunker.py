"""
Chunker — splits raw documents into overlapping text chunks.

Generic by design: takes plain text + config, knows nothing about where
the text came from (ecology, CS, FAQ, etc.). Corpus-specific logic must
never be added here — see rules.md Genericity Rules.
"""
from dataclasses import dataclass, asdict
import json
from pathlib import Path


@dataclass
class Chunk:
    chunk_id: str
    text: str
    source_file: str
    chunk_index: int


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping word-based chunks.

    chunk_size: target number of words per chunk.
    overlap: number of words repeated between consecutive chunks, so a
             sentence spanning a chunk boundary isn't lost entirely.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    step = max(chunk_size - overlap, 1)  # avoid infinite loop if overlap >= chunk_size

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        if end >= len(words):
            break
        start += step

    return chunks


def chunk_documents(
    documents: list[dict],
    chunk_size: int = 300,
    overlap: int = 50,
    text_field: str = "abstract",
    id_field: str = "id",
) -> list[Chunk]:
    """
    documents: list of dicts, each representing one source document.
               Must contain `text_field` (the text to chunk) and
               `id_field` (a unique identifier used as source_file).
    Returns a flat list of Chunk objects across all documents.
    """
    all_chunks: list[Chunk] = []

    for doc in documents:
        doc_id = doc.get(id_field, "unknown")
        text = doc.get(text_field, "")
        if not text:
            continue

        pieces = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        for i, piece in enumerate(pieces):
            all_chunks.append(Chunk(
                chunk_id=f"{doc_id}_chunk{i}",
                text=piece,
                source_file=str(doc_id),
                chunk_index=i,
            ))

    return all_chunks


def save_chunks(chunks: list[Chunk], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(asdict(c), ensure_ascii=False) + "\n")


def load_chunks(input_path: Path) -> list[Chunk]:
    chunks = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            chunks.append(Chunk(**data))
    return chunks


if __name__ == "__main__":
    # Smoke test with fake data — no corpus needed to verify logic works.
    fake_docs = [
        {"id": "paper1", "abstract": " ".join([f"word{i}" for i in range(700)])},
        {"id": "paper2", "abstract": "short abstract with few words only"},
    ]
    result = chunk_documents(fake_docs, chunk_size=300, overlap=50)
    print(f"Produced {len(result)} chunks from {len(fake_docs)} documents")
    for c in result:
        print(f"  {c.chunk_id}: {len(c.text.split())} words")
