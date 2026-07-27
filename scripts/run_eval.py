"""
Eval harness — runs semantic search and keyword search against a hand-
labeled eval set, and reports how often each method finds the correct
paper in its top-k results.

Usage:
    python scripts/run_eval.py corpus_store/ecology_abstracts data/raw/ecology_abstracts.jsonl
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.retriever import CorpusRetriever


def load_eval_set(corpus_dir: Path) -> dict:
    with open(corpus_dir / "eval_set.json", "r", encoding="utf-8") as f:
        return json.load(f)


def build_title_to_id_map(raw_corpus_path: Path) -> dict:
    """Maps each paper's title (lowercased) to its id, from the raw corpus file."""
    title_to_id = {}
    with open(raw_corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            title_to_id[doc["title"].strip().lower()] = str(doc["id"])
    return title_to_id


def evaluate(corpus_dir: Path, raw_corpus_path: Path, k: int = 5):
    eval_data = load_eval_set(corpus_dir)
    retriever = CorpusRetriever(corpus_dir)
    title_to_id = build_title_to_id_map(raw_corpus_path)

    semantic_hits = 0
    keyword_hits = 0
    total = len(eval_data["queries"])
    skipped = 0

    print(f"Running {total} eval queries (top-{k})...\n")

    for item in eval_data["queries"]:
        query = item["query"]
        correct_title = item["correct_title"].strip().lower()
        correct_id = title_to_id.get(correct_title)

        if correct_id is None:
            print(f"WARNING: could not find paper ID for title "
                  f"'{item['correct_title'][:60]}...' — check spelling "
                  f"matches exactly. Skipping this query.\n")
            skipped += 1
            continue

        semantic_results = retriever.semantic_search(query, k=k)
        keyword_results = retriever.keyword_search(query, k=k)

        semantic_found = any(r.source_file == correct_id for r in semantic_results)
        keyword_found = any(r.source_file == correct_id for r in keyword_results)

        semantic_hits += int(semantic_found)
        keyword_hits += int(keyword_found)

        print(f"Query: {query}")
        print(f"  Expected: {item['correct_title'][:70]}...")
        print(f"  Semantic found in top-{k}: {'YES' if semantic_found else 'no'}")
        print(f"  Keyword  found in top-{k}: {'YES' if keyword_found else 'no'}")
        print()

    scored_total = total - skipped
    print("=" * 60)
    if scored_total == 0:
        print("No queries could be scored — check title spellings match "
              "the raw corpus exactly.")
        return

    print(f"Semantic search: {semantic_hits}/{scored_total} correct "
          f"({100 * semantic_hits / scored_total:.0f}%)")
    print(f"Keyword search:  {keyword_hits}/{scored_total} correct "
          f"({100 * keyword_hits / scored_total:.0f}%)")
    if skipped:
        print(f"({skipped} queries skipped due to title mismatch)")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/run_eval.py <corpus_dir> <raw_corpus_jsonl>")
        sys.exit(1)

    evaluate(Path(sys.argv[1]), Path(sys.argv[2]))