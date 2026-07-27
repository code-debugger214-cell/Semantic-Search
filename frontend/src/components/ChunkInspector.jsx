import React, { useState, useEffect } from 'react';
import { Layers, Search, FileText } from 'lucide-react';

export default function ChunkInspector({ selectedCorpus }) {
  const [chunks, setChunks] = useState([]);
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const fetchChunks = async (q = '') => {
    setIsLoading(true);
    try {
      const url = `http://127.0.0.1:8000/api/chunks/${selectedCorpus}?limit=50` + (q ? `&search=${encodeURIComponent(q)}` : '');
      const res = await fetch(url);
      const data = await res.json();
      setChunks(data.chunks || []);
    } catch (err) {
      console.error("Failed to load chunks:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchChunks(search);
  }, [selectedCorpus]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchChunks(search);
  };

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-bold text-slate-200 flex items-center gap-2">
              <Layers className="w-5 h-5 text-indigo-400" />
              Corpus Chunk Inspector
            </h3>
            <p className="text-xs text-slate-400">
              Browse raw document chunks extracted during indexing.
            </p>
          </div>

          <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Filter chunks..."
              className="w-full bg-slate-900 text-white placeholder-slate-500 pl-9 pr-3 py-2 rounded-xl border border-white/15 text-xs focus:outline-none focus:border-indigo-500"
            />
          </form>
        </div>

        {isLoading ? (
          <div className="py-8 text-center text-xs text-slate-400">Loading chunks...</div>
        ) : chunks.length === 0 ? (
          <div className="py-8 text-center text-xs text-slate-400">No chunks found matching search query.</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            {chunks.map((c) => (
              <div key={c.chunk_id} className="glass-panel p-4 space-y-2 border border-white/10 hover:border-indigo-500/40 transition-all">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-indigo-300">
                    {c.chunk_id}
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">
                    {c.word_count} words
                  </span>
                </div>

                <div className="text-[11px] text-slate-400 flex items-center gap-1">
                  <FileText className="w-3 h-3 text-slate-500" />
                  <span>Doc ID:</span>
                  <code className="text-slate-300 font-mono">{c.source_file}</code>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed font-sans bg-slate-900/60 p-3 rounded-lg border border-white/5">
                  "{c.text}"
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
