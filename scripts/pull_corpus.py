"""
Phase 1 — Pull corpus #1: ecology/biodiversity research abstracts via the
Semantic Scholar API (free, no API key required for low-volume use).

Run locally:
    python scripts/pull_corpus.py

Output: data/raw/ecology_abstracts.jsonl
    One JSON object per line: {"id", "title", "abstract", "year", "source"}
"""
import json
import time
import requests
from pathlib import Path

# --- Config (edit these to change what gets pulled) ---
QUERY = "biodiversity monitoring machine learning"
FALLBACK_QUERY = "biodiversity"  # used if primary query returns too few abstracts
TARGET_COUNT = 80          # aim for ~80-100 abstracts
PAGE_SIZE = 25              # Semantic Scholar max per page (unauthenticated)
OUTPUT_PATH = Path("data/raw/ecology_abstracts.jsonl")
API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS = "title,abstract,year,externalIds"

def fetch_abstracts(query: str, target_count: int) -> list[dict]:
    results = []
    offset = 0
    consecutive_empty_pages = 0

    while len(results) < target_count:
        params = {
            "query": query,
            "fields": FIELDS,
            "limit": PAGE_SIZE,
            "offset": offset,
        }
        resp = requests.get(API_URL, params=params, timeout=15)

        if resp.status_code == 429:
            print("Rate limited — waiting 5s before retry...")
            time.sleep(5)
            continue

        resp.raise_for_status()
        data = resp.json()
        papers = data.get("data", [])
        total_available = data.get("total", "unknown")

        if not papers:
            print("No more results returned — stopping.")
            break

        print(f"  Page returned {len(papers)} papers "
              f"(total matching query: {total_available})")

        skipped_no_abstract = 0
        for p in papers:
            # Skip papers with no abstract — nothing to embed/search over.
            if not p.get("abstract"):
                skipped_no_abstract += 1
                continue
            results.append({
                "id": p.get("paperId"),
                "title": p.get("title", "").strip(),
                "abstract": p["abstract"].strip(),
                "year": p.get("year"),
                "source": "semantic_scholar",
            })

        if skipped_no_abstract:
            print(f"  Skipped {skipped_no_abstract} papers with no abstract")

        consecutive_empty_pages = (consecutive_empty_pages + 1
                                    if skipped_no_abstract == len(papers)
                                    else 0)
        if consecutive_empty_pages >= 4:
            print("  4 consecutive pages with no usable abstracts — "
                  "stopping this query early.")
            break

        offset += PAGE_SIZE
        print(f"Fetched {len(results)} abstracts so far...")
        time.sleep(1.5)  # be polite to the free-tier API

    return results[:target_count]


def main():
    print(f"Querying Semantic Scholar for: '{QUERY}'")
    abstracts = fetch_abstracts(QUERY, TARGET_COUNT)

    if len(abstracts) < 15:
        print(f"\nOnly {len(abstracts)} abstracts found for primary query — "
              f"trying broader fallback query: '{FALLBACK_QUERY}'")
        more = fetch_abstracts(FALLBACK_QUERY, TARGET_COUNT - len(abstracts))
        seen_ids = {a["id"] for a in abstracts}
        abstracts += [a for a in more if a["id"] not in seen_ids]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for item in abstracts:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"\nDone. Saved {len(abstracts)} abstracts to {OUTPUT_PATH}")
    if len(abstracts) < 30:
        print("WARNING: fewer than 30 abstracts — consider broadening the "
              "query or lowering TARGET_COUNT expectations.")


if __name__ == "__main__":
    main()
