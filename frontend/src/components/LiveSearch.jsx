import React, { useState, useEffect } from 'react';
import { Search, Sparkles, Cpu, Code, HelpCircle, FileText, CheckCircle2 } from 'lucide-react';

const SAMPLE_QUERIES = {
  ecology_abstracts: [
    "how climate change affects species migration",
    "biodiversity loss in tropical rainforest ecosystems",
    "mitochondrial and nuclear genomes in cellular respiration",
    "population viability analysis models",
  ],
  mobile_networks_abstracts: [
    "energy efficiency in 5G network slicing",
    "massive MIMO beamforming optimization techniques",
    "deep reinforcement learning for radio resource management",
    "ultra-reliable low latency communications URLLC",
  ],
  faq_squad: [
    "what is superluminal motion in astronomy",
    "how does photosynthesis work in green plants",
    "history of quantum mechanics and wave particle duality",
    "structure of eukaryotic cell membrane",
  ]
};

export default function LiveSearch({ selectedCorpus, topK, setTopK, searchResults, onExecuteSearch, isSearching }) {
  const [query, setQuery] = useState('');

  const samples = SAMPLE_QUERIES[selectedCorpus] || [
    "quantum computing algorithms overview",
    "machine learning model evaluation metrics",
    "deep neural networks optimization strategies"
  ];

  useEffect(() => {
    if (samples.length > 0) {
      setQuery(samples[0]);
      onExecuteSearch(samples[0]);
    }
  }, [selectedCorpus]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onExecuteSearch(query);
    }
  };

  const handleSampleClick = (sampleText) => {
    setQuery(sampleText);
    onExecuteSearch(sampleText);
  };

  const highlightTokens = (text, q) => {
    if (!q) return text;
    const words = new Set(q.toLowerCase().split(/\s+/).filter(w => w.length > 2));
    const tokens = text.split(/\s+/);

    return tokens.map((token, i) => {
      const clean = token.toLowerCase().replace(/[^a-z0-9]/g, '');
      if (words.has(clean)) {
        return <span key={i} className="match-tag mr-1">{token}</span>;
      }
      return token + ' ';
    });
  };

  return (
    <div className="space-y-6">
      {/* Search Input Section */}
      <div className="glass-panel p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative flex items-center">
            <Search className="w-5 h-5 absolute left-4 text-slate-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your natural language query or exact keyword phrase..."
              className="w-full bg-slate-900/90 text-white placeholder-slate-500 pl-12 pr-32 py-4 rounded-2xl border border-white/15 text-base focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all shadow-inner"
            />
            <button
              type="submit"
              disabled={isSearching}
              className="absolute right-3 px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-sm shadow-md transition-all disabled:opacity-50"
            >
              {isSearching ? 'Searching...' : 'Search'}
            </button>
          </div>

          {/* Sample Queries */}
          <div className="flex flex-wrap items-center gap-2 pt-2">
            <span className="text-xs font-semibold text-slate-400 flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" /> Sample Queries:
            </span>
            {samples.map((s, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSampleClick(s)}
                className="sample-pill"
              >
                {s}
              </button>
            ))}
          </div>
        </form>
      </div>

      {/* Top-K Slider & Overlap Bar */}
      {searchResults && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-xl bg-slate-900/60 border border-white/10">
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <span className="text-sm font-semibold text-slate-300">Top-K Results:</span>
            <input
              type="range"
              min="1"
              max="10"
              value={topK}
              onChange={(e) => {
                const val = parseInt(e.target.value);
                setTopK(val);
                if (query) onExecuteSearch(query, val);
              }}
              className="w-32 accent-indigo-500 cursor-pointer"
            />
            <span className="badge badge-semantic">{topK}</span>
          </div>

          <div className="flex items-center gap-2 text-sm font-medium text-slate-300">
            <span>Result Overlap:</span>
            <span className="px-3 py-1 rounded-lg bg-indigo-950/80 border border-indigo-500/30 text-indigo-300 font-bold font-mono">
              {searchResults.overlap_count} common ({searchResults.overlap_percentage}%)
            </span>
          </div>
        </div>
      )}

      {/* Side-by-Side Results Columns */}
      {searchResults && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* SEMANTIC COLUMN */}
          <div className="space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-purple-500/20">
              <div className="flex items-center gap-2">
                <Cpu className="w-5 h-5 text-purple-400" />
                <h3 className="text-lg font-bold text-purple-300">Semantic Search (FAISS)</h3>
              </div>
              <span className="text-xs text-slate-400">Dense Embedding Vector Cosine Sim</span>
            </div>

            {searchResults.semantic_results.map((res) => {
              const simPercent = Math.max(Math.min(Math.round(res.score * 100), 100), 5);
              return (
                <div key={res.chunk_id} className="glass-panel semantic-border p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-extrabold text-purple-400 font-mono">
                      #{res.rank} · {res.chunk_id}
                    </span>
                    <span className="badge badge-semantic">
                      Sim: {res.score.toFixed(3)}
                    </span>
                  </div>

                  <div className="progress-track">
                    <div className="progress-semantic" style={{ width: `${simPercent}%` }} />
                  </div>

                  <div className="text-xs text-slate-400 flex items-center gap-1">
                    <FileText className="w-3.5 h-3.5" />
                    <span>Doc ID:</span>
                    <code className="text-slate-200 font-mono">{res.source_file}</code>
                  </div>

                  <p className="text-sm text-slate-200 leading-relaxed italic">
                    "{res.text}"
                  </p>
                </div>
              );
            })}
          </div>

          {/* KEYWORD COLUMN */}
          <div className="space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-emerald-500/20">
              <div className="flex items-center gap-2">
                <Code className="w-5 h-5 text-emerald-400" />
                <h3 className="text-lg font-bold text-emerald-300">Keyword Search (BM25)</h3>
              </div>
              <span className="text-xs text-slate-400">Sparse Term Frequency BM25 Score</span>
            </div>

            {searchResults.keyword_results.map((res) => {
              const maxBm25 = searchResults.keyword_results[0]?.score || 1.0;
              const barPercent = Math.max(Math.min(Math.round((res.score / maxBm25) * 100), 100), 5);
              return (
                <div key={res.chunk_id} className="glass-panel keyword-border p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-extrabold text-emerald-400 font-mono">
                      #{res.rank} · {res.chunk_id}
                    </span>
                    <span className="badge badge-keyword">
                      BM25: {res.score.toFixed(2)}
                    </span>
                  </div>

                  <div className="progress-track">
                    <div className="progress-keyword" style={{ width: `${barPercent}%` }} />
                  </div>

                  <div className="text-xs text-slate-400 flex items-center gap-1">
                    <FileText className="w-3.5 h-3.5" />
                    <span>Doc ID:</span>
                    <code className="text-slate-200 font-mono">{res.source_file}</code>
                  </div>

                  <p className="text-sm text-slate-200 leading-relaxed">
                    "{highlightTokens(res.text, query)}"
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
