# Evaluation Write-Up — Semantic vs. Keyword Search on Ecology Corpus

## Setup
- Corpus: 50 real ecology/biodiversity research abstracts (pulled from arXiv)
- Eval set: 15 hand-labeled queries, each with one correct paper marked
  - 10 "moderate" queries — natural phrasing, loosely based on paper topics
  - 5 "hard" queries — deliberately paraphrased, avoiding the paper's own
    vocabulary, to stress-test whether semantic search holds up without
    word overlap
- Metric: whether the correct paper appeared in the top-5 results

## Results
| Method | Correct (out of 15) | Accuracy |
|---|---|---|
| Semantic search (embeddings) | 14 | 93% |
| Keyword search (BM25) | 10 | 67% |

## Findings
1. **Semantic search outperformed keyword search overall**, and the gap was
   concentrated almost entirely in the "hard" paraphrased queries. On
   queries where the question's wording didn't overlap with the paper's
   own vocabulary — e.g. "does biodiversity influence the spread of
   disease outbreaks" (paper says "Hantavirus epizootic"), and "why do
   some species survive longer at the cost of not being dominant" (paper
   says "mito-nuclear selection... evolutionary lifespan") — keyword
   search missed entirely while semantic search found the correct paper.
   This is the expected mechanism: semantic search captures meaning, not
   just shared words.

2. **Keyword search still performed reasonably on direct-vocabulary
   queries.** When a query's wording closely matched the paper's own
   terms (e.g. "can deep learning identify tree species automatically"),
   both methods succeeded — keyword search isn't obsolete, it just
   struggles specifically with paraphrasing.

3. **One query beat both methods**: "why are some species much more
   common than others in nature" failed to retrieve its correct paper
   ("Self-organized biodiversity and species abundance distribution
   patterns...") under either method. This is a useful, honest limit to
   note — very technical/jargon-heavy abstracts can sit far from plain-
   language phrasing even in embedding space, not just in keyword space.
   Semantic search narrows this gap but doesn't eliminate it entirely.

## Honest Caveats
- Corpus size (50 papers) is small — results may not generalize to a
  much larger or more diverse corpus without re-evaluation.
- Eval queries were written by looking at paper titles/abstracts first,
  which may make them easier than genuine, unprompted user queries.
- This eval set is domain-specific (ecology) — the same comparison on a
  different corpus (e.g. legal documents, FAQs) could yield different
  results; genericity of the *pipeline* doesn't guarantee identical
  *performance* on a new domain (see architecture.md).

## Conclusion
On this corpus and eval set, embedding-based semantic search meaningfully
outperformed classical keyword search, with the advantage concentrated
specifically in paraphrased/reworded queries — the exact scenario
semantic search is designed to improve on. Keyword search remains
competitive when query wording closely matches source vocabulary.
