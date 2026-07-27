import React, { useState, useEffect } from 'react';
import { Search, Sparkles, Brain, FileText, ChevronDown, ChevronUp, Tag, HelpCircle, Layers } from 'lucide-react';

export default function SentenceSearch({ selectedCorpus }) {
  const [querySentence, setQuerySentence] = useState('how does climate change influence the movement of wild species');
  const [documents, setDocuments] = useState([]);
  const [selectedDocId, setSelectedDocId] = useState('all');
  const [topK, setTopK] = useState(5);
  const [results, setResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [expandedContexts, setExpandedContexts] = useState({});

  // Fetch unique documents in selected corpus
  useEffect(() => {
    if (selectedCorpus) {
      fetch(`http://127.0.0.1:8000/api/documents/${selectedCorpus}`)
        .then(res => res.json())
        .then(data => {
          setDocuments(data.documents || []);
          setSelectedDocId('all');
        })
        .catch(err => console.error("Failed to load documents:", err));
    }
  }, [selectedCorpus]);

  const handleExecuteSearch = async (e) => {
    if (e) e.preventDefault();
    if (!querySentence.trim() || !selectedCorpus) return;

    setIsSearching(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/search-sentence', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          corpus_name: selectedCorpus,
          query_sentence: querySentence,
          target_doc_id: selectedDocId,
          top_k: topK
        }),
      });
      const data = await res.json();
      setResults(data.sentence_matches || []);
    } catch (err) {
      console.error("Sentence search error:", err);
    } finally {
      setIsSearching(false);
    }
  };

  useEffect(() => {
    if (selectedCorpus) {
      handleExecuteSearch();
    }
  }, [selectedCorpus]);

  const toggleContext = (idx) => {
    setExpandedContexts(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <div className="space-y-6">
      {/* Top Search Controls */}
      <div className="glass-panel p-6 space-y-4 border border-white/10">
        <div className="flex items-center justify-between pb-2 border-b border-white/10">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Brain className="w-5 h-5 text-purple-400" />
              In-Document Sentence & Semantic Meaning Finder
            </h2>
            <p className="text-xs text-slate-400">
              Find exact sentences in documents matching your query's meaning, accompanied by an AI semantic relationship explanation.
            </p>
          </div>
        </div>

        <form onSubmit={handleExecuteSearch} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            {/* Query Input */}
            <div className="md:col-span-3 relative flex items-center">
              <Search className="w-5 h-5 absolute left-4 text-slate-400" />
              <input
                type="text"
                value={querySentence}
                onChange={(e) => setQuerySentence(e.target.value)}
                placeholder="Enter any sentence or question to search..."
                className="w-full bg-slate-900 text-white placeholder-slate-500 pl-12 pr-4 py-3.5 rounded-xl border border-white/15 text-sm focus:outline-none focus:border-purple-500 font-medium"
              />
            </div>

            {/* Document Filter Dropdown */}
            <div>
              <select
                value={selectedDocId}
                onChange={(e) => setSelectedDocId(e.target.value)}
                className="w-full bg-slate-900 text-slate-200 px-3 py-3.5 rounded-xl border border-white/15 text-xs font-medium focus:outline-none focus:border-purple-500 cursor-pointer"
              >
                <option value="all">🌐 All Documents in Corpus</option>
                {documents.map((d) => (
                  <option key={d.doc_id} value={d.doc_id}>
                    📄 {d.doc_id}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex items-center justify-between pt-1">
            <div className="flex items-center gap-3">
              <span className="text-xs font-semibold text-slate-400">Top-K Sentence Matches:</span>
              <input
                type="range"
                min="1"
                max="10"
                value={topK}
                onChange={(e) => setTopK(parseInt(e.target.value))}
                className="w-28 accent-purple-500 cursor-pointer"
              />
              <span className="badge badge-semantic">{topK}</span>
            </div>

            <button
              type="submit"
              disabled={isSearching}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-sm shadow-md transition-all disabled:opacity-50"
            >
              {isSearching ? 'Analyzing Meaning...' : 'Find Sentence & Meaning'}
            </button>
          </div>
        </form>
      </div>

      {/* Results Section */}
      {results && results.length > 0 && (
        <div className="space-y-4">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider px-1">
            Found {results.length} Semantically Matched Sentence(s):
          </div>

          {results.map((item, idx) => {
            const exp = item.semantic_explanation;
            const isExpanded = !!expandedContexts[idx];

            return (
              <div key={idx} className="glass-panel p-6 space-y-4 border-l-4 border-purple-500 hover:border-purple-400 transition-all">
                {/* Header Badge */}
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 pb-3 border-b border-white/10">
                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-1 rounded-lg bg-purple-950/80 border border-purple-500/40 text-purple-300 font-mono font-bold text-xs">
                      Match #{item.rank}
                    </span>
                    <span className="text-xs text-slate-400 flex items-center gap-1 font-mono">
                      <FileText className="w-3.5 h-3.5 text-slate-500" />
                      Doc ID: <code className="text-slate-200 font-bold">{item.doc_id}</code>
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-slate-400">Semantic Sim:</span>
                    <span className="px-3 py-1 rounded-lg bg-purple-900/40 text-purple-300 font-mono font-extrabold text-sm border border-purple-500/30">
                      {item.similarity_pct}%
                    </span>
                  </div>
                </div>

                {/* Matched Sentence Text */}
                <div className="space-y-1">
                  <div className="text-[11px] font-bold text-purple-400 uppercase tracking-wider">
                    🎯 Matched Sentence in Document:
                  </div>
                  <p className="text-base font-semibold text-white leading-relaxed bg-purple-950/30 p-4 rounded-xl border border-purple-500/20 shadow-inner">
                    "{item.matched_sentence}"
                  </p>
                </div>

                {/* Semantic Meaning Explanation Card */}
                <div className="p-4 rounded-xl bg-slate-900/90 border border-purple-500/30 space-y-2">
                  <div className="flex items-center gap-2 text-xs font-bold text-amber-400">
                    <Sparkles className="w-4 h-4" />
                    <span>Semantic Meaning & Relationship Insight:</span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed font-medium">
                    {exp.explanation}
                  </p>

                  {exp.overlapping_concepts && exp.overlapping_concepts.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5 pt-1">
                      <span className="text-[10px] text-slate-400 font-semibold">Matched Concepts:</span>
                      {exp.overlapping_concepts.map((term, tIdx) => (
                        <span key={tIdx} className="px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-500/30 text-[10px] font-mono">
                          {term}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Paragraph Context Accordion */}
                <div>
                  <button
                    onClick={() => toggleContext(idx)}
                    className="flex items-center gap-1.5 text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors"
                  >
                    <Layers className="w-3.5 h-3.5" />
                    {isExpanded ? 'Hide Paragraph Context' : 'Show Full Paragraph Context'}
                    {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>

                  {isExpanded && (
                    <div className="mt-2 p-3 rounded-xl bg-slate-950 text-xs text-slate-300 leading-relaxed border border-white/10 font-mono">
                      {item.paragraph_context}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
