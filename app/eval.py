"""
Evaluation Module — Computes IR metrics (Recall@k, MRR, NDCG@k) for Semantic and Keyword retrieval.

Generic by design: loads any corpus's eval_set.json or eval_set_by_id.json from corpus_store/<corpus_name>/.
"""
import json
import math
from pathlib import Path
import sys
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.retriever import CorpusRetriever


def compute_reciprocal_rank(retrieved_ids: List[str], target_id: str) -> float:
    """Computes Reciprocal Rank (1/rank of first match, or 0.0 if not found)."""
    for rank, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id == target_id:
            return 1.0 / rank
    return 0.0


def compute_ndcg_at_k(retrieved_ids: List[str], target_id: str, k: int) -> float:
    """Computes NDCG@k for single relevant document (binary relevance)."""
    sub_retrieved = retrieved_ids[:k]
    for rank, doc_id in enumerate(sub_retrieved, start=1):
        if doc_id == target_id:
            dcg = 1.0 / math.log2(rank + 1)
            idcg = 1.0 / math.log2(1 + 1)  # rank 1 is ideal
            return dcg / idcg
    return 0.0


def evaluate_corpus(corpus_dir: Path, max_k: int = 10) -> Dict[str, Any]:
    """
    Runs full evaluation over a given corpus_dir.
    Returns aggregated metrics (Recall@1, Recall@3, Recall@5, MRR, NDCG@5)
    and a query-by-query breakdown table.
    """
    # 1. Determine eval set file
    eval_file = corpus_dir / "eval_set.json"
    by_id_mode = False
    if not eval_file.exists():
        eval_file = corpus_dir / "eval_set_by_id.json"
        by_id_mode = True

    if not eval_file.exists():
        raise FileNotFoundError(f"No eval set found in {corpus_dir}")

    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    # 2. Build title to ID map if in title mode
    title_to_id = {}
    if not by_id_mode:
        raw_candidates = list(Path("data/raw").glob(f"{corpus_dir.name}*.jsonl"))
        if raw_candidates and raw_candidates[0].exists():
            with open(raw_candidates[0], "r", encoding="utf-8") as f:
                for line in f:
                    doc = json.loads(line)
                    title_to_id[doc["title"].strip().lower()] = str(doc["id"])

    retriever = CorpusRetriever(corpus_dir)

    results = []
    semantic_mrrs = []
    keyword_mrrs = []
    semantic_ndcg5 = []
    keyword_ndcg5 = []

    k_list = [1, 3, 5, 10]
    semantic_hits_at_k = {k: 0 for k in k_list}
    keyword_hits_at_k = {k: 0 for k in k_list}

    total_queries = 0

    for item in eval_data.get("queries", []):
        query = item["query"]

        if by_id_mode:
            target_id = str(item["correct_id"])
            target_label = item.get("correct_title", target_id)
        else:
            correct_title = item.get("correct_title", "").strip().lower()
            target_id = title_to_id.get(correct_title)
            target_label = item.get("correct_title", "Unknown")
            if not target_id:

                continue

        total_queries += 1

        sem_res = retriever.semantic_search(query, k=max_k)
        kw_res = retriever.keyword_search(query, k=max_k)

        sem_ids = [r.source_file for r in sem_res]
        kw_ids = [r.source_file for r in kw_res]

        # Calculate MRR
        sem_mrr = compute_reciprocal_rank(sem_ids, target_id)
        kw_mrr = compute_reciprocal_rank(kw_ids, target_id)
        semantic_mrrs.append(sem_mrr)
        keyword_mrrs.append(kw_mrr)

        # Calculate NDCG@5
        sem_ndcg = compute_ndcg_at_k(sem_ids, target_id, k=5)
        kw_ndcg = compute_ndcg_at_k(kw_ids, target_id, k=5)
        semantic_ndcg5.append(sem_ndcg)
        keyword_ndcg5.append(kw_ndcg)

        # Hits at k
        for k in k_list:
            if target_id in sem_ids[:k]:
                semantic_hits_at_k[k] += 1
            if target_id in kw_ids[:k]:
                keyword_hits_at_k[k] += 1

        # Winner status
        if sem_mrr > kw_mrr:
            winner = "Semantic"
        elif kw_mrr > sem_mrr:
            winner = "Keyword"
        else:
            winner = "Tie" if sem_mrr > 0 else "Neither"

        results.append({
            "query": query,
            "target_label": target_label,
            "target_id": target_id,
            "semantic_mrr": sem_mrr,
            "keyword_mrr": kw_mrr,
            "semantic_ndcg5": sem_ndcg,
            "keyword_ndcg5": kw_ndcg,
            "winner": winner,
            "semantic_rank": sem_ids.index(target_id) + 1 if target_id in sem_ids else None,
            "keyword_rank": kw_ids.index(target_id) + 1 if target_id in kw_ids else None,
        })

    if total_queries == 0:
        return {"error": "No scorable queries found."}

    summary = {
        "corpus_name": corpus_dir.name,
        "total_queries": total_queries,
        "semantic": {
            "mrr": float(sum(semantic_mrrs) / total_queries),
            "ndcg@5": float(sum(semantic_ndcg5) / total_queries),
            "recall@1": float(semantic_hits_at_k[1] / total_queries),
            "recall@3": float(semantic_hits_at_k[3] / total_queries),
            "recall@5": float(semantic_hits_at_k[5] / total_queries),
            "recall@10": float(semantic_hits_at_k[10] / total_queries),
        },
        "keyword": {
            "mrr": float(sum(keyword_mrrs) / total_queries),
            "ndcg@5": float(sum(keyword_ndcg5) / total_queries),
            "recall@1": float(keyword_hits_at_k[1] / total_queries),
            "recall@3": float(keyword_hits_at_k[3] / total_queries),
            "recall@5": float(keyword_hits_at_k[5] / total_queries),
            "recall@10": float(keyword_hits_at_k[10] / total_queries),
        },
        "query_details": results,
    }
    return summary


if __name__ == "__main__":
    test_dir = Path("corpus_store/ecology_abstracts")
    if test_dir.exists():
        metrics = evaluate_corpus(test_dir)
        print("Ecology Evaluation Summary:")
        print(json.dumps(metrics["semantic"], indent=2))
