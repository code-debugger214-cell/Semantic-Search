"""
Streamlit Web Application — Semantic Search with Retrieval Evaluation

A modern, dark-themed, glassmorphic UI comparing Semantic Search (FAISS + MiniLM)
against Keyword Search (BM25) with side-by-side search results and empirical IR metrics.
"""
import json
from pathlib import Path
import sys
import numpy as np
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.retriever import CorpusRetriever
from app.eval import evaluate_corpus

# ---------------------------------------------------------
# Page Configuration & Custom CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="Semantic vs BM25 Search Evaluator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Base background */
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    color: #f8fafc;
}

/* Glassmorphism containers */
.glass-card {
    background: rgba(30, 41, 59, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.glass-card:hover {
    border-color: rgba(99, 102, 241, 0.4);
    transform: translateY(-2px);
}

.semantic-card {
    border-left: 5px solid #8b5cf6 !important;
}

.keyword-card {
    border-left: 5px solid #10b981 !important;
}

/* Score Badges */
.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.82rem;
    font-family: 'JetBrains Mono', monospace;
}

.badge-semantic {
    background: rgba(139, 92, 246, 0.2);
    color: #c084fc;
    border: 1px solid rgba(139, 92, 246, 0.4);
}

.badge-keyword {
    background: rgba(16, 185, 129, 0.2);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.4);
}

.badge-win-semantic {
    background: rgba(139, 92, 246, 0.25);
    color: #a78bfa;
    padding: 4px 8px;
    border-radius: 6px;
}

.badge-win-keyword {
    background: rgba(16, 185, 129, 0.25);
    color: #6ee7b7;
    padding: 4px 8px;
    border-radius: 6px;
}

.badge-win-tie {
    background: rgba(245, 158, 11, 0.25);
    color: #fcd34d;
    padding: 4px 8px;
    border-radius: 6px;
}

/* Custom Progress Bar */
.bar-container {
    width: 100%;
    background-color: rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    height: 8px;
    margin-top: 8px;
    margin-bottom: 12px;
    overflow: hidden;
}

.bar-semantic {
    height: 100%;
    background: linear-gradient(90deg, #6366f1, #a855f7);
    border-radius: 6px;
}

.bar-keyword {
    height: 100%;
    background: linear-gradient(90deg, #059669, #14b8a6);
    border-radius: 6px;
}

/* Query Pill Button */
.sample-pill {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: #e2e8f0;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.85rem;
    cursor: pointer;
    display: inline-block;
    margin-right: 8px;
    margin-bottom: 8px;
    transition: all 0.2s;
}

.sample-pill:hover {
    background: rgba(99, 102, 241, 0.2);
    border-color: #6366f1;
    color: #ffffff;
}

/* Highlighted search match */
.match-highlight {
    background-color: rgba(16, 185, 129, 0.25);
    color: #6ee7b7;
    font-weight: 600;
    padding: 1px 4px;
    border-radius: 3px;
}

/* Custom metric card */
.kpi-card {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}

.kpi-title {
    font-size: 0.85rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}

.kpi-value {
    font-size: 1.8rem;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------
# Helper Functions & Caching
# ---------------------------------------------------------
CORPUS_DIR_MAP = {
    "🌱 Ecology Abstracts (SDG-15)": Path("corpus_store/ecology_abstracts"),
    "📡 Mobile Networks Abstract (5G/6G)": Path("corpus_store/mobile_networks_abstracts"),
    "📚 SQuAD Wikipedia Passages (QA)": Path("corpus_store/faq_squad"),
}

SAMPLE_QUERIES = {
    "🌱 Ecology Abstracts (SDG-15)": [
        "how climate change affects species migration",
        "biodiversity loss in tropical rainforest ecosystems",
        "mitochondrial and nuclear genomes in cellular respiration",
        "population viability analysis models",
    ],
    "📡 Mobile Networks Abstract (5G/6G)": [
        "energy efficiency in 5G network slicing",
        "massive MIMO beamforming optimization techniques",
        "deep reinforcement learning for radio resource management",
        "ultra-reliable low latency communications URLLC",
    ],
    "📚 SQuAD Wikipedia Passages (QA)": [
        "what is superluminal motion in astronomy",
        "how does photosynthesis work in green plants",
        "history of quantum mechanics and wave particle duality",
        "structure of eukaryotic cell membrane",
    ]
}


@st.cache_resource
def get_retriever(corpus_dir_path: str):
    return CorpusRetriever(Path(corpus_dir_path))


@st.cache_data
def get_eval_metrics(corpus_dir_path: str):
    return evaluate_corpus(Path(corpus_dir_path))


def format_highlighted_text(text: str, query: str) -> str:
    """Highlights matching query words in text for keyword view."""
    words = set(query.lower().split())
    tokens = text.split()
    highlighted = []
    for token in tokens:
        clean_t = token.lower().strip(".,!?;:()[]\"'")
        if clean_t in words and len(clean_t) > 2:
            highlighted.append(f'<span class="match-highlight">{token}</span>')
        else:
            highlighted.append(token)
    return " ".join(highlighted)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Corpus & Settings")

    selected_corpus_label = st.selectbox(
        "Select Corpus",
        options=list(CORPUS_DIR_MAP.keys()),
        index=0
    )
    selected_dir = CORPUS_DIR_MAP[selected_corpus_label]

    st.markdown("---")

    top_k = st.slider("Top-K Results", min_value=1, max_value=10, value=5, step=1)

    st.markdown("---")

    # Load corpus details
    retriever = get_retriever(str(selected_dir))
    num_chunks = len(retriever.chunks)
    unique_docs = len(set(c.source_file for c in retriever.chunks))

    st.markdown("#### 📊 Corpus Statistics")
    st.markdown(f"""
    - **Total Documents:** `{unique_docs}`
    - **Total Chunks:** `{num_chunks}`
    - **Embedding Model:** `all-MiniLM-L6-v2`
    - **Vector Dimension:** `384`
    - **Chunk Size:** `300 words` (50 overlap)
    """)

    st.markdown("---")
    st.caption("🚀 Powered by FAISS, BM25 Okapi & Sentence-Transformers")


# ---------------------------------------------------------
# Header Hero Section
# ---------------------------------------------------------
st.markdown("""
<div style="text-align: center; padding: 20px 0 30px 0;">
    <h1 style="font-size: 2.8rem; font-weight: 800; background: linear-gradient(90deg, #8b5cf6, #3b82f6, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        ⚡ Semantic vs Keyword Search Evaluator
    </h1>
    <p style="font-size: 1.1rem; color: #94a3b8; max-width: 800px; margin: 0 auto;">
        Benchmarking <b>Dense Vector Semantic Search (FAISS + MiniLM)</b> against <b>Classical Sparse Keyword Search (BM25)</b> across diverse domain corpora with real IR evaluation metrics.
    </p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Navigation Tabs
# ---------------------------------------------------------
tab_search, tab_eval, tab_corpus = st.tabs([
    "🔍 Live Comparative Search",
    "📈 Retrieval Evaluation Dashboard",
    "📦 Corpus & Chunk Inspector"
])


# ---------------------------------------------------------
# TAB 1: Live Comparative Search
# ---------------------------------------------------------
with tab_search:
    st.subheader("Compare Retrieval Results Side-by-Side")

    # Clickable Sample Queries
    st.markdown("**💡 Try Sample Queries:**")
    sample_cols = st.columns(len(SAMPLE_QUERIES[selected_corpus_label]))
    for idx, sample in enumerate(SAMPLE_QUERIES[selected_corpus_label]):
        if sample_cols[idx].button(sample, key=f"btn_{idx}"):
            st.session_state["query_input"] = sample

    # Query Input
    query_text = st.text_input(
        "Enter your search query:",
        value=st.session_state.get("query_input", SAMPLE_QUERIES[selected_corpus_label][0]),
        placeholder="Type a natural language question or keyword query...",
        key="main_query_input"
    )

    if query_text:
        # Perform Search
        semantic_results = retriever.semantic_search(query_text, k=top_k)
        keyword_results = retriever.keyword_search(query_text, k=top_k)

        # Overlap analysis
        sem_ids = [r.source_file for r in semantic_results]
        kw_ids = [r.source_file for r in keyword_results]
        overlap_ids = set(sem_ids).intersection(set(kw_ids))
        overlap_pct = (len(overlap_ids) / top_k) * 100

        # Overlap Banner
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255, 255, 255, 0.1); padding: 10px 16px; border-radius: 10px; margin: 15px 0; display: flex; align-items: center; justify-content: space-between;">
            <div>
                <span style="font-weight: 600; color: #cbd5e1;">Top-{top_k} Overlap:</span> 
                <span style="font-weight: 700; color: #818cf8;">{len(overlap_ids)} common document(s) ({overlap_pct:.0f}% similarity)</span>
            </div>
            <div>
                <span style="font-size: 0.85rem; color: #94a3b8;">Query length: {len(query_text.split())} words</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_sem, col_kw = st.columns(2)

        # SEMANTIC COLUMN
        with col_sem:
            st.markdown("### 🧠 Semantic Search (FAISS)")
            st.caption("Captures intent, synonyms, and conceptual meaning.")

            max_sem_score = max([r.score for r in semantic_results]) if semantic_results else 1.0
            max_sem_score = max(max_sem_score, 0.001)

            for rank, res in enumerate(semantic_results, start=1):
                # Normalizing score for visual bar (cosine sim is between 0 and 1)
                bar_width = max(min(int(res.score * 100), 100), 5)
                st.markdown(f"""
                <div class="glass-card semantic-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; color: #c084fc;">#{rank} · Chunk: {res.chunk_id}</span>
                        <span class="badge badge-semantic">Sim: {res.score:.3f}</span>
                    </div>
                    <div class="bar-container">
                        <div class="bar-semantic" style="width: {bar_width}%;"></div>
                    </div>
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 8px;">
                        📄 <b>Doc ID:</b> <code>{res.source_file}</code>
                    </div>
                    <div style="font-size: 0.95rem; color: #e2e8f0; line-height: 1.5;">
                        "{res.text}"
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # KEYWORD COLUMN
        with col_kw:
            st.markdown("### 🔤 Keyword Search (BM25)")
            st.caption("Matches exact word occurrences & term frequencies.")

            max_kw_score = max([r.score for r in keyword_results]) if keyword_results else 1.0
            max_kw_score = max(max_kw_score, 0.001)

            for rank, res in enumerate(keyword_results, start=1):
                bar_width = max(min(int((res.score / max_kw_score) * 100), 100), 5)
                highlighted = format_highlighted_text(res.text, query_text)
                st.markdown(f"""
                <div class="glass-card keyword-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; color: #34d399;">#{rank} · Chunk: {res.chunk_id}</span>
                        <span class="badge badge-keyword">BM25: {res.score:.2f}</span>
                    </div>
                    <div class="bar-container">
                        <div class="bar-keyword" style="width: {bar_width}%;"></div>
                    </div>
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 8px;">
                        📄 <b>Doc ID:</b> <code>{res.source_file}</code>
                    </div>
                    <div style="font-size: 0.95rem; color: #e2e8f0; line-height: 1.5;">
                        "{highlighted}"
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ---------------------------------------------------------
# TAB 2: Retrieval Evaluation Dashboard
# ---------------------------------------------------------
with tab_eval:
    st.subheader(f"📊 Information Retrieval Metrics — {selected_corpus_label}")
    st.caption("Evaluated on hand-labeled ground truth query sets across Recall@k, MRR, and NDCG@5.")

    with st.spinner("Computing evaluation metrics over test harness..."):
        metrics_data = get_eval_metrics(str(selected_dir))

    if "error" in metrics_data:
        st.error(metrics_data["error"])
    else:
        sem_m = metrics_data["semantic"]
        kw_m = metrics_data["keyword"]
        total_q = metrics_data["total_queries"]

        st.markdown(f"**Evaluated on `{total_q}` queries**")

        # Top KPI Scorecards
        k1, k2, k3, k4 = st.columns(4)

        with k1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">MRR (Mean Recip. Rank)</div>
                <div class="kpi-value" style="color: #c084fc;">{sem_m['mrr']:.3f}</div>
                <div style="font-size: 0.8rem; color: #34d399;">BM25: {kw_m['mrr']:.3f}</div>
            </div>
            """, unsafe_allow_html=True)

        with k2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">NDCG @ 5</div>
                <div class="kpi-value" style="color: #c084fc;">{sem_m['ndcg@5']:.3f}</div>
                <div style="font-size: 0.8rem; color: #34d399;">BM25: {kw_m['ndcg@5']:.3f}</div>
            </div>
            """, unsafe_allow_html=True)

        with k3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Recall @ 5</div>
                <div class="kpi-value" style="color: #c084fc;">{sem_m['recall@5']*100:.1f}%</div>
                <div style="font-size: 0.8rem; color: #34d399;">BM25: {kw_m['recall@5']*100:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with k4:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Recall @ 1 (Top Pick)</div>
                <div class="kpi-value" style="color: #c084fc;">{sem_m['recall@1']*100:.1f}%</div>
                <div style="font-size: 0.8rem; color: #34d399;">BM25: {kw_m['recall@1']*100:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Metric Comparison Table & Chart
        col_chart, col_summary = st.columns([3, 2])

        with col_chart:
            st.markdown("#### 📉 Recall Curve Comparison (Recall@k)")
            import pandas as pd
            chart_df = pd.DataFrame({
                "k": [1, 3, 5, 10],
                "Semantic (FAISS)": [sem_m["recall@1"], sem_m["recall@3"], sem_m["recall@5"], sem_m["recall@10"]],
                "Keyword (BM25)": [kw_m["recall@1"], kw_m["recall@3"], kw_m["recall@5"], kw_m["recall@10"]],
            }).set_index("k")

            st.bar_chart(chart_df)

        with col_summary:
            st.markdown("#### 🎯 Evaluation Takeaway")
            win_counts = {"Semantic": 0, "Keyword": 0, "Tie": 0, "Neither": 0}
            for d in metrics_data["query_details"]:
                win_counts[d["winner"]] += 1

            st.markdown(f"""
            - **Semantic Wins:** `{win_counts['Semantic']}` queries ({win_counts['Semantic']/total_q*100:.0f}%)
            - **Keyword Wins:** `{win_counts['Keyword']}` queries ({win_counts['Keyword']/total_q*100:.0f}%)
            - **Ties / Equal Rank:** `{win_counts['Tie']}` queries ({win_counts['Tie']/total_q*100:.0f}%)
            - **Unretrieved (Both Missed):** `{win_counts['Neither']}` queries
            """)

            if win_counts["Semantic"] >= win_counts["Keyword"]:
                st.success("🧠 **Semantic Search performs higher** overall on this corpus due to capturing paraphrases & domain synonyms.")
            else:
                st.info("🔤 **Keyword Search performs higher** overall on this corpus because queries use exact document terminology.")

        st.markdown("---")
        st.markdown("#### 📑 Query-by-Query Detailed Diagnostic Table")

        # Query Diagnostic Table
        filter_winner = st.radio(
            "Filter queries by winner:",
            ["All", "Semantic", "Keyword", "Tie", "Neither"],
            horizontal=True
        )

        table_rows = []
        for qd in metrics_data["query_details"]:
            if filter_winner != "All" and qd["winner"] != filter_winner:
                continue

            table_rows.append({
                "Query": qd["query"],
                "Ground Truth Target": qd["target_label"][:60] + "...",
                "Winner": qd["winner"],
                "Semantic Rank": f"#{qd['semantic_rank']}" if qd['semantic_rank'] else "Not in Top 10",
                "BM25 Rank": f"#{qd['keyword_rank']}" if qd['keyword_rank'] else "Not in Top 10",
                "Semantic MRR": f"{qd['semantic_mrr']:.2f}",
                "BM25 MRR": f"{qd['keyword_mrr']:.2f}",
            })

        if table_rows:
            st.dataframe(pd.DataFrame(table_rows), use_container_width=True)
        else:
            st.info("No queries match the selected filter.")


# ---------------------------------------------------------
# TAB 3: Corpus & Chunk Explorer
# ---------------------------------------------------------
with tab_corpus:
    st.subheader(f"📦 Chunks & Document Browser — {selected_corpus_label}")
    st.caption("Inspect how source documents were split into overlapping chunks.")

    search_filter = st.text_input("Filter chunks by text keyword:", placeholder="Type word to filter chunks...")

    chunks = retriever.chunks
    filtered_chunks = [c for c in chunks if search_filter.lower() in c.text.lower()] if search_filter else chunks

    st.markdown(f"Showing **{len(filtered_chunks)}** of **{len(chunks)}** total chunks")

    for c in filtered_chunks[:15]:
        with st.expander(f"Chunk `{c.chunk_id}` — Doc: `{c.source_file}` (Index {c.chunk_index})"):
            st.markdown(f"**Word count:** {len(c.text.split())} words")
            st.text_area("Chunk Content", c.text, height=120, disabled=True, key=f"chunk_{c.chunk_id}")
