"""
Eval harness (ID-based variant) — for corpora where titles repeat across
multiple documents (e.g. SQuAD, where many passages share one Wikipedia
article title). Matches by exact document id instead of title.

Usage:
    python scripts/run_eval_by_id.py corpus_store/faq_squad
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.retriever import CorpusRetriever


def load_eval_set(corpus_dir: Path) -> dict:
    with open(corpus_dir / "eval_set_by_id.json", "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate(corpus_dir: Path, k: int = 5):
    eval_data = load_eval_set(corpus_dir)
    retriever = CorpusRetriever(corpus_dir)

    semantic_hits = 0
    keyword_hits = 0
    total = len(eval_data["queries"])

    print(f"Running {total} eval queries (top-{k})...\n")

    for item in eval_data["queries"]:
        query = item["query"]
        correct_id = item["correct_id"]

        semantic_results = retriever.semantic_search(query, k=k)
        keyword_results = retriever.keyword_search(query, k=k)

        semantic_found = any(r.source_file == correct_id for r in semantic_results)
        keyword_found = any(r.source_file == correct_id for r in keyword_results)

        semantic_hits += int(semantic_found)
        keyword_hits += int(keyword_found)

        print(f"Query: {query}")
        print(f"  Semantic found in top-{k}: {'YES' if semantic_found else 'no'}")
        print(f"  Keyword  found in top-{k}: {'YES' if keyword_found else 'no'}")
        print()

    print("=" * 60)
    print(f"Semantic search: {semantic_hits}/{total} correct "
          f"({100 * semantic_hits / total:.0f}%)")
    print(f"Keyword search:  {keyword_hits}/{total} correct "
          f"({100 * keyword_hits / total:.0f}%)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_eval_by_id.py <corpus_dir>")
        sys.exit(1)

    evaluate(Path(sys.argv[1]))