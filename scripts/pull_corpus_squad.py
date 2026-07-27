"""
Phase 1 (corpus #3, different source type) — Pull a Q&A/FAQ-style corpus
from the SQuAD dataset via Hugging Face's `datasets` library.

Unlike arXiv abstracts (dense academic prose), SQuAD contexts are short,
everyday-language paragraphs (Wikipedia excerpts) paired with real
questions people would naturally ask — a genuinely different content
style, testing whether the pipeline generalizes beyond one type of text.

Run locally:
    python scripts/pull_corpus_squad.py

Output: data/raw/faq_squad.jsonl
    One JSON object per line: {"id", "title", "text", "source"}
"""
import json
from pathlib import Path

TARGET_COUNT = 80
OUTPUT_PATH = Path("data/raw/faq_squad.jsonl")


def main():
    from datasets import load_dataset

    print("Downloading SQuAD dataset (first run may take a minute)...")
    dataset = load_dataset("squad", split="train")

    seen_contexts = set()
    documents = []

    for row in dataset:
        context = row["context"].strip()
        if context in seen_contexts:
            continue  # SQuAD repeats the same context for multiple questions
        seen_contexts.add(context)

        documents.append({
            "id": row["id"],
            "title": row["title"],
            "text": context,
            "source": "squad",
        })

        if len(documents) >= TARGET_COUNT:
            break

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for doc in documents:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    print(f"Done. Saved {len(documents)} unique passages to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()