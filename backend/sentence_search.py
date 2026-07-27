"""
Sentence Search & Semantic Meaning Explainer Engine.

Splits document text into individual sentences, embeds them, computes cosine similarity,
and generates semantic relationship explanations for matched sentences.
"""
import re
import numpy as np
from pathlib import Path
import sys
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.embedder import get_model, embed_texts
from app.retriever import CorpusRetriever


def split_into_sentences(text: str) -> List[str]:
    """Splits document text into clean individual sentences."""
    # Split by period, question mark, or exclamation mark followed by whitespace
    raw_sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 10]
    return sentences if sentences else [text]


def generate_semantic_explanation(query_sentence: str, matched_sentence: str, similarity_score: float) -> Dict[str, Any]:
    """
    Generates a human-readable explanation of why the matched sentence
    relates semantically to the user's query sentence.
    """
    query_words = set(re.findall(r'\w+', query_sentence.lower()))
    match_words = set(re.findall(r'\w+', matched_sentence.lower()))

    # Find overlapping words and distinct words
    overlapping = query_words.intersection(match_words)
    distinct_query = query_words - match_words
    distinct_match = match_words - query_words

    # Filter short stop words
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'with', 'by', 'how', 'what', 'why', 'does', 'do', 'can'}
    significant_overlap = overlapping - stop_words
    significant_distinct_query = distinct_query - stop_words
    significant_distinct_match = distinct_match - stop_words

    if similarity_score >= 0.70:
        match_type = "High Semantic Match (Strong Alignment)"
    elif similarity_score >= 0.45:
        match_type = "Moderate Semantic Paraphrase"
    else:
        match_type = "Low / Contextual Alignment"

    # Construct explanation text
    if significant_distinct_query and significant_distinct_match:
        reasoning = (
            f"Semantic Paraphrase: Your query mentions '{', '.join(list(significant_distinct_query)[:3])}', "
            f"which semantically maps to '{', '.join(list(significant_distinct_match)[:3])}' in the document text."
        )
    elif significant_overlap:
        reasoning = f"Direct & Conceptual Overlap: Matches key concepts on '{', '.join(list(significant_overlap)[:4])}'."
    else:
        reasoning = "Implicit Semantic Relation: Captures broader topic and contextual meaning without exact word duplication."

    return {
        "match_type": match_type,
        "similarity_score_pct": round(similarity_score * 100, 1),
        "explanation": reasoning,
        "overlapping_concepts": list(significant_overlap),
        "query_distinct_terms": list(significant_distinct_query)[:4],
        "matched_distinct_terms": list(significant_distinct_match)[:4]
    }


def search_sentences_in_corpus(
    retriever: CorpusRetriever,
    query_sentence: str,
    target_doc_id: Optional[str] = None,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Splits chunks/documents into individual sentences and finds the top-k
    semantically matching sentences across the corpus (or within a specific doc).
    """
    query_vec = embed_texts([query_sentence])[0]
    norm = np.linalg.norm(query_vec)
    if norm > 0:
        query_vec = query_vec / norm

    # Extract all candidate sentences
    all_sentence_entries = []
    for chunk in retriever.chunks:
        if target_doc_id and chunk.source_file != target_doc_id:
            continue

        sentences = split_into_sentences(chunk.text)
        for s_idx, sentence in enumerate(sentences):
            all_sentence_entries.append({
                "sentence": sentence,
                "doc_id": chunk.source_file,
                "chunk_id": chunk.chunk_id,
                "sentence_index": s_idx,
                "paragraph_context": chunk.text
            })

    if not all_sentence_entries:
        return []

    sentence_texts = [e["sentence"] for e in all_sentence_entries]
    sentence_vectors = embed_texts(sentence_texts)

    # Normalize sentence vectors for cosine similarity
    norms = np.linalg.norm(sentence_vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10
    normalized_vecs = sentence_vectors / norms

    # Compute dot products (cosine similarity)
    scores = np.dot(normalized_vecs, query_vec)

    # Get top-k indices
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for rank, idx in enumerate(top_indices, start=1):
        entry = all_sentence_entries[idx]
        score = float(scores[idx])
        explanation = generate_semantic_explanation(query_sentence, entry["sentence"], score)

        results.append({
            "rank": rank,
            "matched_sentence": entry["sentence"],
            "doc_id": entry["doc_id"],
            "chunk_id": entry["chunk_id"],
            "paragraph_context": entry["paragraph_context"],
            "similarity_score": score,
            "similarity_pct": round(score * 100, 1),
            "semantic_explanation": explanation
        })

    return results


if __name__ == "__main__":
    q = "how does climate change affect species migration"
    s = "Global warming and shifting weather patterns force wild populations to migrate northwards."
    exp = generate_semantic_explanation(q, s, 0.78)
    print("Semantic explanation test:", exp)
