import React from 'react';
import { Zap, Database, Upload, Search, BarChart2, Layers, Brain } from 'lucide-react';

export default function Navbar({
  corpora,
  selectedCorpus,
  setSelectedCorpus,
  activeTab,
  setActiveTab,
  onOpenUpload
}) {
  return (
    <header className="sticky top-0 z-40 backdrop-blur-xl bg-[#0b0f19]/90 border-b border-white/10 px-6 py-4">
      <div className="max-w-7xl mx-auto flex flex-col lg:flex-row items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-emerald-500 text-white shadow-lg shadow-purple-500/20">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-extrabold tracking-tight bg-gradient-to-r from-purple-400 via-indigo-200 to-emerald-400 bg-clip-text text-transparent">
              RAG & IR Evaluation Studio
            </h1>
            <p className="text-xs text-slate-400 font-medium">
              Multi-Format Document Retrieval & Semantic Explainer
            </p>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap items-center gap-1.5 p-1.5 rounded-xl bg-slate-900/90 border border-white/10">
          <button
            onClick={() => setActiveTab('sentence')}
            className={`nav-tab ${activeTab === 'sentence' ? 'active' : ''}`}
          >
            <Brain className="w-4 h-4 text-purple-400" />
            Sentence & Meaning
          </button>
          <button
            onClick={() => setActiveTab('search')}
            className={`nav-tab ${activeTab === 'search' ? 'active' : ''}`}
          >
            <Search className="w-4 h-4" />
            Side-by-Side Search
          </button>
          <button
            onClick={() => setActiveTab('eval')}
            className={`nav-tab ${activeTab === 'eval' ? 'active' : ''}`}
          >
            <BarChart2 className="w-4 h-4" />
            IR Benchmarks
          </button>
          <button
            onClick={() => setActiveTab('chunks')}
            className={`nav-tab ${activeTab === 'chunks' ? 'active' : ''}`}
          >
            <Layers className="w-4 h-4" />
            Chunks
          </button>
        </div>

        {/* Actions & Corpus Dropdown */}
        <div className="flex items-center gap-3 w-full lg:w-auto justify-end">
          {/* Corpus Dropdown */}
          <div className="relative flex items-center">
            <Database className="w-4 h-4 absolute left-3 text-indigo-400 pointer-events-none" />
            <select
              value={selectedCorpus}
              onChange={(e) => setSelectedCorpus(e.target.value)}
              className="bg-slate-900 text-slate-200 pl-9 pr-8 py-2 rounded-xl border border-white/15 text-xs font-medium focus:outline-none focus:border-indigo-500 cursor-pointer shadow-inner"
            >
              {corpora.map((c) => (
                <option key={c.corpus_name} value={c.corpus_name}>
                  {c.display_name} ({c.total_chunks} chunks)
                </option>
              ))}
            </select>
          </div>

          {/* Upload Button */}
          <button
            onClick={onOpenUpload}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold shadow-md transition-all hover:scale-105"
          >
            <Upload className="w-4 h-4" />
            Upload Document
          </button>
        </div>
      </div>
    </header>
  );
}
