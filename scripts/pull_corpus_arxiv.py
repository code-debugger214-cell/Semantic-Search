"""
Phase 1 (alternative source) — Pull corpus #1 via the arXiv API.

No API key needed, no aggressive rate limiting like Semantic Scholar.
arXiv skews CS/physics/math/quantitative-biology, so we search for
ecology/biodiversity papers phrased in ML/quantitative terms.

Run locally:
    python scripts/pull_corpus_arxiv.py

Output: data/raw/ecology_abstracts.jsonl
    One JSON object per line: {"id", "title", "abstract", "year", "source"}
"""
import json
import time
import re
import requests
from pathlib import Path
import xml.etree.ElementTree as ET

# --- Config (edit these to change what gets pulled) ---
QUERY = "mobile computing wireless networks"
TARGET_COUNT = 80
PAGE_SIZE = 50  # arXiv allows up to 100+ per request, but keep it modest
OUTPUT_PATH = Path("data/raw/mobile_networks_abstracts.jsonl")
API_URL = "http://export.arxiv.org/api/query"

ATOM_NS = "{http://www.w3.org/2005/Atom}"


def fetch_page(query: str, start: int, max_results: int) -> list[dict]:
    params = {
        "search_query": f"all:{query}",
        "start": start,
        "max_results": max_results,
    }
    for attempt in range(3):
        try:
            resp = requests.get(API_URL, params=params, timeout=30)
            resp.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            print(f"  Request failed ({e}), retrying ({attempt + 1}/3)...")
            time.sleep(5)
    else:
        print("  Giving up on this page after 3 attempts.")
        return []

    root = ET.fromstring(resp.text)
    entries = root.findall(f"{ATOM_NS}entry")

    papers = []
    for entry in entries:
        title_el = entry.find(f"{ATOM_NS}title")
        summary_el = entry.find(f"{ATOM_NS}summary")
        id_el = entry.find(f"{ATOM_NS}id")
        published_el = entry.find(f"{ATOM_NS}published")

        if title_el is None or summary_el is None:
            continue

        title = re.sub(r"\s+", " ", title_el.text or "").strip()
        abstract = re.sub(r"\s+", " ", summary_el.text or "").strip()
        arxiv_id = (id_el.text or "").strip().split("/")[-1] if id_el is not None else None
        year = None
        if published_el is not None and published_el.text:
            year = int(published_el.text[:4])

        if not abstract:
            continue

        papers.append({
            "id": arxiv_id or title[:30],
            "title": title,
            "abstract": abstract,
            "year": year,
            "source": "arxiv",
        })

    return papers


def fetch_abstracts(query: str, target_count: int) -> list[dict]:
    results = []
    start = 0

    while len(results) < target_count:
        print(f"Fetching results {start}-{start + PAGE_SIZE}...")
        papers = fetch_page(query, start, PAGE_SIZE)

        if not papers:
            print("No more results returned — stopping.")
            break

        results.extend(papers)
        print(f"  Got {len(papers)} papers with abstracts "
              f"(total so far: {len(results)})")

        start += PAGE_SIZE
        time.sleep(3)  # arXiv asks for at least 3s between requests

    return results[:target_count]


def main():
    print(f"Querying arXiv for: '{QUERY}'")
    abstracts = fetch_abstracts(QUERY, TARGET_COUNT)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for item in abstracts:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"\nDone. Saved {len(abstracts)} abstracts to {OUTPUT_PATH}")
    if len(abstracts) < 30:
        print("WARNING: fewer than 30 abstracts — try broadening QUERY, "
              "e.g. 'ecological modeling neural network' or 'biodiversity'.")


if __name__ == "__main__":
    main()
