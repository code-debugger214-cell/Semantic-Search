import React, { useState } from 'react';
import { Award, CheckCircle, XCircle, MinusCircle, BarChart3, Filter } from 'lucide-react';

export default function EvalDashboard({ metrics, selectedCorpus }) {
  const [filterWinner, setFilterWinner] = useState('All');

  if (!metrics || metrics.error) {
    return (
      <div className="glass-panel p-8 text-center space-y-3">
        <p className="text-slate-400">No evaluation benchmark dataset found for this corpus.</p>
      </div>
    );
  }

  const sem = metrics.semantic || {};
  const kw = metrics.keyword || {};
  const total = metrics.total_queries || 0;
  const details = metrics.query_details || [];

  const filteredDetails = details.filter(d => filterWinner === 'All' || d.winner === filterWinner);

  return (
    <div className="space-y-8">
      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* MRR */}
        <div className="glass-panel p-5 text-center space-y-2">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400">MRR (Mean Recip. Rank)</div>
          <div className="text-3xl font-extrabold font-mono text-purple-400">{(sem.mrr || 0).toFixed(3)}</div>
          <div className="text-xs font-semibold text-emerald-400">BM25: {(kw.mrr || 0).toFixed(3)}</div>
        </div>

        {/* NDCG@5 */}
        <div className="glass-panel p-5 text-center space-y-2">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400">NDCG @ 5</div>
          <div className="text-3xl font-extrabold font-mono text-purple-400">{(sem['ndcg@5'] || 0).toFixed(3)}</div>
          <div className="text-xs font-semibold text-emerald-400">BM25: {(kw['ndcg@5'] || 0).toFixed(3)}</div>
        </div>

        {/* Recall@5 */}
        <div className="glass-panel p-5 text-center space-y-2">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400">Recall @ 5 (Hit Rate)</div>
          <div className="text-3xl font-extrabold font-mono text-purple-400">{((sem['recall@5'] || 0) * 100).toFixed(1)}%</div>
          <div className="text-xs font-semibold text-emerald-400">BM25: {((kw['recall@5'] || 0) * 100).toFixed(1)}%</div>
        </div>

        {/* Recall@1 */}
        <div className="glass-panel p-5 text-center space-y-2">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400">Recall @ 1 (Top-1 Accuracy)</div>
          <div className="text-3xl font-extrabold font-mono text-purple-400">{((sem['recall@1'] || 0) * 100).toFixed(1)}%</div>
          <div className="text-xs font-semibold text-emerald-400">BM25: {((kw['recall@1'] || 0) * 100).toFixed(1)}%</div>
        </div>
      </div>

      {/* Visual Chart Comparison */}
      <div className="glass-panel p-6 space-y-4">
        <h3 className="text-lg font-bold text-slate-200 flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-indigo-400" />
          Recall@K Curve Comparison
        </h3>

        <div className="space-y-4">
          {[1, 3, 5, 10].map(k => {
            const semVal = (sem[`recall@${k}`] || 0) * 100;
            const kwVal = (kw[`recall@${k}`] || 0) * 100;
            return (
              <div key={k} className="space-y-1.5">
                <div className="flex justify-between text-xs font-bold text-slate-300">
                  <span>Recall @ {k}</span>
                  <span>Semantic: {semVal.toFixed(0)}% | BM25: {kwVal.toFixed(0)}%</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div className="progress-track">
                    <div className="progress-semantic" style={{ width: `${semVal}%` }} />
                  </div>
                  <div className="progress-track">
                    <div className="progress-keyword" style={{ width: `${kwVal}%` }} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Query Diagnostics Table */}
      <div className="glass-panel p-6 space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <h3 className="text-lg font-bold text-slate-200 flex items-center gap-2">
            <Award className="w-5 h-5 text-amber-400" />
            Query-by-Query Evaluation Breakdown ({total} queries)
          </h3>

          {/* Winner Filters */}
          <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900 border border-white/10 text-xs">
            <Filter className="w-3.5 h-3.5 ml-2 text-slate-400" />
            {['All', 'Semantic', 'Keyword', 'Tie'].map(w => (
              <button
                key={w}
                onClick={() => setFilterWinner(w)}
                className={`px-3 py-1 rounded-lg font-semibold transition-all ${
                  filterWinner === w ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'
                }`}
              >
                {w}
              </button>
            ))}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-white/10 text-xs font-bold text-slate-400 uppercase tracking-wider">
                <th className="py-3 px-4">Query</th>
                <th className="py-3 px-4">Target Document</th>
                <th className="py-3 px-4">Winner</th>
                <th className="py-3 px-4 text-center">Semantic Rank</th>
                <th className="py-3 px-4 text-center">BM25 Rank</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 text-sm">
              {filteredDetails.map((q, idx) => (
                <tr key={idx} className="hover:bg-white/[0.02] transition-colors">
                  <td className="py-3 px-4 font-medium text-slate-200">{q.query}</td>
                  <td className="py-3 px-4 text-xs text-slate-400 truncate max-w-xs">{q.target_label}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2.5 py-1 rounded-lg text-xs font-bold ${
                      q.winner === 'Semantic' ? 'bg-purple-950 text-purple-300 border border-purple-500/30' :
                      q.winner === 'Keyword' ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/30' :
                      'bg-amber-950 text-amber-300 border border-amber-500/30'
                    }`}>
                      {q.winner}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center font-mono text-purple-400 font-bold">
                    {q.semantic_rank ? `#${q.semantic_rank}` : '—'}
                  </td>
                  <td className="py-3 px-4 text-center font-mono text-emerald-400 font-bold">
                    {q.keyword_rank ? `#${q.keyword_rank}` : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
