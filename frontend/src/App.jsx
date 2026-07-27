import React, { useState, useEffect, useCallback } from 'react';
import {
  Search, Sparkles, Gauge, UploadCloud, List, ChevronDown, Loader2,
  AlertTriangle, CheckCircle2, Circle, ArrowRight, FileText, X, Radio,
  Database, FileStack, PlugZap, PlugZap as Plug, Trash2, SlidersHorizontal
} from 'lucide-react';

const API_BASE = typeof window !== 'undefined' && window.location.origin.includes('5173')
  ? 'http://127.0.0.1:8000'
  : (typeof window !== 'undefined' ? window.location.origin : 'http://127.0.0.1:8000');

const TABS = [
  { id: 'compare', label: 'Compare', sub: 'Semantic vs BM25', icon: Radio },
  { id: 'sentence', label: 'Sentence', sub: 'Meaning search', icon: Sparkles },
  { id: 'eval', label: 'Evaluate', sub: 'Recall / MRR / NDCG', icon: Gauge },
  { id: 'upload', label: 'Ingest', sub: 'Add a corpus', icon: UploadCloud },
  { id: 'chunks', label: 'Chunks', sub: 'Raw index browser', icon: List },
];

async function apiFetch(path, opts = {}) {
  const res = await fetch(`${API_BASE}${path}`, opts);
  if (!res.ok) {
    let detail = res.statusText;
    try { const j = await res.json(); detail = j.detail || detail; } catch (_) {}
    throw new Error(detail || `Request failed (${res.status})`);
  }
  return res.json();
}

function classNames(...xs) { return xs.filter(Boolean).join(' '); }

// ---------------------------------------------------------------
// Small UI atoms
// ---------------------------------------------------------------

function Pulse({ status }) {
  const map = {
    checking: { dot: 'bg-slate-500', ring: 'ring-slate-500/30', label: 'checking backend' },
    online: { dot: 'bg-emerald-400', ring: 'ring-emerald-400/30', label: 'backend online' },
    offline: { dot: 'bg-rose-400', ring: 'ring-rose-400/30', label: 'backend unreachable' },
  };
  const s = map[status] || map.checking;
  return (
    <div className="flex items-center gap-2">
      <span className={classNames('relative flex h-2.5 w-2.5')}>
        {status === 'online' && (
          <span className={classNames('animate-ping absolute inline-flex h-full w-full rounded-full opacity-75', s.dot)} />
        )}
        <span className={classNames('relative inline-flex rounded-full h-2.5 w-2.5', s.dot)} />
      </span>
      <span className="text-[11px] font-mono uppercase tracking-widest text-slate-500">{s.label}</span>
    </div>
  );
}

function ScoreBar({ score, max, tone = 'cyan' }) {
  const pct = max > 0 ? Math.max(4, Math.min(100, (score / max) * 100)) : 4;
  const bar = tone === 'cyan' ? 'bg-cyan-400' : 'bg-amber-400';
  return (
    <div className="flex items-center gap-2 w-full">
      <div className="h-1.5 flex-1 rounded-full bg-slate-800 overflow-hidden">
        <div className={classNames('h-full rounded-full transition-all duration-500', bar)} style={{ width: `${pct}%` }} />
      </div>
      <span className="font-mono text-[11px] text-slate-400 w-14 text-right tabular-nums">{score.toFixed(3)}</span>
    </div>
  );
}

function OverlapGauge({ overlapPct, overlapCount, topK }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/60 px-5 py-4">
      <div className="flex items-baseline justify-between mb-2">
        <span className="text-[11px] font-mono uppercase tracking-widest text-slate-500">Result-set overlap</span>
        <span className="font-mono text-sm text-slate-200 tabular-nums">
          {overlapCount}/{topK} · {overlapPct.toFixed(1)}%
        </span>
      </div>
      <div className="h-3 w-full rounded-full bg-slate-800 overflow-hidden flex">
        <div className="h-full bg-gradient-to-r from-cyan-500 to-cyan-300" style={{ width: `${overlapPct / 2}%` }} />
        <div className="h-full w-px bg-slate-950" />
        <div className="h-full bg-gradient-to-l from-amber-500 to-amber-300" style={{ width: `${overlapPct / 2}%` }} />
      </div>
      <div className="flex justify-between mt-1.5">
        <span className="text-[10px] font-mono text-cyan-400/70">SEMANTIC</span>
        <span className="text-[10px] font-mono text-amber-400/70">KEYWORD</span>
      </div>
    </div>
  );
}

function MetricGauge({ label, value, tone = 'cyan' }) {
  const pct = Math.max(0, Math.min(100, value * 100));
  const ring = tone === 'cyan' ? '#22d3ee' : tone === 'amber' ? '#fbbf24' : '#34d399';
  const r = 42;
  const circumference = 2 * Math.PI * r;
  const offset = circumference - (pct / 100) * circumference;
  return (
    <div className="flex flex-col items-center gap-3 rounded-lg border border-slate-800 bg-slate-900/60 p-6">
      <div className="relative h-28 w-28">
        <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90">
          <circle cx="50" cy="50" r={r} fill="none" stroke="#1e293b" strokeWidth="8" />
          <circle
            cx="50" cy="50" r={r} fill="none" stroke={ring} strokeWidth="8"
            strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 700ms ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="font-mono text-xl font-semibold text-slate-100 tabular-nums">{value.toFixed(3)}</span>
        </div>
      </div>
      <span className="text-[11px] font-mono uppercase tracking-widest text-slate-400">{label}</span>
    </div>
  );
}

function EmptyState({ icon: Icon, title, hint }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-16 text-center">
      <Icon className="h-8 w-8 text-slate-700" strokeWidth={1.5} />
      <p className="text-sm font-medium text-slate-400">{title}</p>
      {hint && <p className="text-xs text-slate-600 max-w-xs">{hint}</p>}
    </div>
  );
}

function ErrorNote({ message }) {
  return (
    <div className="flex items-start gap-2 rounded-md border border-rose-900/60 bg-rose-950/40 px-3 py-2.5">
      <AlertTriangle className="h-4 w-4 text-rose-400 mt-0.5 shrink-0" />
      <p className="text-xs text-rose-300 font-mono leading-relaxed">{message}</p>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-[11px] font-mono uppercase tracking-widest text-slate-500">{label}</span>
      {children}
    </label>
  );
}

const inputCls = "bg-slate-900 border border-slate-800 rounded-md px-3 py-2 text-sm text-slate-100 placeholder-slate-600 outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/40 transition-colors font-mono";

// ---------------------------------------------------------------
// Compare Search tab
// ---------------------------------------------------------------

function CompareTab({ corpus }) {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const run = async (e) => {
    e.preventDefault();
    if (!query.trim() || !corpus) return;
    setLoading(true); setError(null);
    try {
      const res = await apiFetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ corpus_name: corpus, query, top_k: Number(topK) }),
      });
      setData(res);
    } catch (err) {
      setError(err.message);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const semMax = data ? Math.max(...data.semantic_results.map(r => r.score), 1e-6) : 1;
  const kwMax = data ? Math.max(...data.keyword_results.map(r => r.score), 1e-6) : 1;

  return (
    <div className="flex flex-col gap-5">
      <form onSubmit={run} className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-600" />
          <input
            className={classNames(inputCls, 'w-full pl-9')}
            placeholder="Enter a query to compare retrieval methods…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <div className="flex gap-3">
          <Field label="top_k">
            <input type="number" min={1} max={50} value={topK} onChange={(e) => setTopK(e.target.value)}
              className={classNames(inputCls, 'w-20')} />
          </Field>
          <button
            type="submit"
            disabled={loading || !corpus}
            className="self-end inline-flex items-center gap-2 rounded-md bg-cyan-500 hover:bg-cyan-400 disabled:bg-slate-800 disabled:text-slate-600 text-slate-950 font-semibold text-sm px-4 py-2 transition-colors"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ArrowRight className="h-4 w-4" />}
            Run
          </button>
        </div>
      </form>

      {error && <ErrorNote message={error} />}

      {!data && !error && !loading && (
        <EmptyState icon={Radio} title="No comparison yet" hint="Run a query to see semantic and keyword results side by side, with overlap between the two ranked lists." />
      )}

      {loading && (
        <div className="flex items-center justify-center py-16 gap-2 text-slate-500">
          <Loader2 className="h-4 w-4 animate-spin" /> <span className="text-sm font-mono">retrieving…</span>
        </div>
      )}

      {data && !loading && (
        <>
          <OverlapGauge overlapPct={data.overlap_percentage} overlapCount={data.overlap_count} topK={topK} />
          <div className="grid md:grid-cols-2 gap-4">
            <ResultColumn title="Semantic · FAISS" tone="cyan" results={data.semantic_results} max={semMax} />
            <ResultColumn title="Keyword · BM25" tone="amber" results={data.keyword_results} max={kwMax} />
          </div>
        </>
      )}
    </div>
  );
}

function ResultColumn({ title, tone, results, max }) {
  const accent = tone === 'cyan' ? 'text-cyan-400 border-cyan-900/50' : 'text-amber-400 border-amber-900/50';
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/40 overflow-hidden">
      <div className={classNames('px-4 py-2.5 border-b bg-slate-900/80 font-mono text-xs uppercase tracking-widest', accent)}>
        {title}
      </div>
      <div className="divide-y divide-slate-800/80">
        {results.length === 0 && <p className="px-4 py-6 text-xs text-slate-600 font-mono">no results</p>}
        {results.map((r) => (
          <div key={`${r.method}-${r.chunk_id}`} className="px-4 py-3 flex flex-col gap-2">
            <div className="flex items-start gap-3">
              <span className={classNames('font-mono text-xs shrink-0 mt-0.5', tone === 'cyan' ? 'text-cyan-500' : 'text-amber-500')}>
                {String(r.rank).padStart(2, '0')}
              </span>
              <p className="text-sm text-slate-300 leading-snug line-clamp-3">{r.text}</p>
            </div>
            <p className="text-[11px] font-mono text-slate-600 pl-7 truncate">{r.source_file}</p>
            <div className="pl-7">
              <ScoreBar score={r.score} max={max} tone={tone} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------
// Sentence Search tab
// ---------------------------------------------------------------

function SentenceTab({ corpus }) {
  const [sentence, setSentence] = useState('');
  const [targetDoc, setTargetDoc] = useState('all');
  const [docs, setDocs] = useState([]);
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  useEffect(() => {
    if (!corpus) return;
    apiFetch(`/api/documents/${encodeURIComponent(corpus)}`)
      .then((res) => setDocs(res.documents || []))
      .catch(() => setDocs([]));
    setTargetDoc('all');
  }, [corpus]);

  const run = async (e) => {
    e.preventDefault();
    if (!sentence.trim() || !corpus) return;
    setLoading(true); setError(null);
    try {
      const res = await apiFetch('/api/search-sentence', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          corpus_name: corpus,
          query_sentence: sentence,
          target_doc_id: targetDoc,
          top_k: Number(topK),
        }),
      });
      setResults(res);
    } catch (err) {
      setError(err.message);
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-5">
      <form onSubmit={run} className="flex flex-col gap-3">
        <Field label="query sentence">
          <textarea
            rows={2}
            className={classNames(inputCls, 'w-full resize-none')}
            placeholder="Type a full sentence to find semantically related sentences…"
            value={sentence}
            onChange={(e) => setSentence(e.target.value)}
          />
        </Field>
        <div className="flex flex-wrap items-end gap-3">
          <Field label="target document">
            <select value={targetDoc} onChange={(e) => setTargetDoc(e.target.value)}
              className={classNames(inputCls, 'min-w-[220px]')}>
              <option value="all">All documents</option>
              {docs.map((d) => (
                <option key={d.doc_id} value={d.doc_id}>{d.doc_id}</option>
              ))}
            </select>
          </Field>
          <Field label="top_k">
            <input type="number" min={1} max={50} value={topK} onChange={(e) => setTopK(e.target.value)}
              className={classNames(inputCls, 'w-20')} />
          </Field>
          <button
            type="submit"
            disabled={loading || !corpus}
            className="inline-flex items-center gap-2 rounded-md bg-cyan-500 hover:bg-cyan-400 disabled:bg-slate-800 disabled:text-slate-600 text-slate-950 font-semibold text-sm px-4 py-2 transition-colors"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
            Find meaning matches
          </button>
        </div>
      </form>

      {error && <ErrorNote message={error} />}

      {!results && !error && !loading && (
        <EmptyState icon={Sparkles} title="No sentence matches yet" hint="Enter a sentence to surface the most semantically related sentences in the corpus, each with a similarity explanation." />
      )}

      {loading && (
        <div className="flex items-center justify-center py-16 gap-2 text-slate-500">
          <Loader2 className="h-4 w-4 animate-spin" /> <span className="text-sm font-mono">matching meaning…</span>
        </div>
      )}

      {results && !loading && (
        <div className="flex flex-col gap-3">
          <p className="text-[11px] font-mono uppercase tracking-widest text-slate-500">
            {results.results_count} match{results.results_count === 1 ? '' : 'es'}
          </p>
          <div className="grid sm:grid-cols-2 gap-3">
            {(results.sentence_matches || []).map((m, i) => (
              <SentenceCard key={i} rank={i + 1} item={m} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function SentenceCard({ rank, item }) {
  const text = item.sentence || item.text || item.matched_sentence || JSON.stringify(item);
  const score = item.score ?? item.similarity ?? item.similarity_score;
  const doc = item.source_file || item.doc_id || item.document;
  const explanation = item.semantic_explanation?.explanation || item.explanation || item.reason || item.semantic_relationship;

  return (
    <div className="rounded-lg border border-slate-800 bg-gradient-to-b from-slate-900/70 to-slate-900/30 p-4 flex flex-col gap-2.5">
      <div className="flex items-center justify-between">
        <span className="font-mono text-xs text-cyan-500">{String(rank).padStart(2, '0')}</span>
        {typeof score === 'number' && (
          <span className="font-mono text-[11px] text-slate-400 tabular-nums">sim {score.toFixed(3)}</span>
        )}
      </div>
      <p className="text-sm text-slate-200 leading-snug">{text}</p>
      {explanation && (
        <p className="text-xs text-slate-500 border-l-2 border-cyan-900/60 pl-2.5 italic leading-snug">{explanation}</p>
      )}
      {doc && <p className="text-[11px] font-mono text-slate-600 truncate">{doc}</p>}
    </div>
  );
}

// ---------------------------------------------------------------
// Evaluation tab
// ---------------------------------------------------------------

function EvalTab({ corpus }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    if (!corpus) { setMetrics(null); return; }
    setLoading(true); setError(null);
    apiFetch(`/api/eval/${encodeURIComponent(corpus)}`)
      .then(setMetrics)
      .catch((err) => { setError(err.message); setMetrics(null); })
      .finally(() => setLoading(false));
  }, [corpus]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16 gap-2 text-slate-500">
        <Loader2 className="h-4 w-4 animate-spin" /> <span className="text-sm font-mono">scoring corpus…</span>
      </div>
    );
  }
  if (error) return <ErrorNote message={error} />;
  if (!metrics) return <EmptyState icon={Gauge} title="No corpus selected" hint="Select a corpus to view Recall@k, MRR, and NDCG@5 against its evaluation set." />;

  const sem = metrics.semantic || {};
  const kw = metrics.keyword || {};

  return (
    <div className="flex flex-col gap-5">
      <div className="grid sm:grid-cols-3 gap-4">
        <MetricGauge label="MRR (Semantic)" value={sem.mrr || 0} tone="cyan" />
        <MetricGauge label="NDCG @ 5 (Semantic)" value={sem['ndcg@5'] || 0} tone="amber" />
        <MetricGauge label="Recall @ 5 (Semantic)" value={sem['recall@5'] || 0} tone="emerald" />
      </div>
      <div className="grid sm:grid-cols-3 gap-4">
        <MetricGauge label="MRR (Keyword)" value={kw.mrr || 0} tone="cyan" />
        <MetricGauge label="NDCG @ 5 (Keyword)" value={kw['ndcg@5'] || 0} tone="amber" />
        <MetricGauge label="Recall @ 5 (Keyword)" value={kw['recall@5'] || 0} tone="emerald" />
      </div>
      <details className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
        <summary className="cursor-pointer text-[11px] font-mono uppercase tracking-widest text-slate-500">Raw metrics payload</summary>
        <pre className="mt-3 text-xs font-mono text-slate-400 overflow-x-auto">{JSON.stringify(metrics, null, 2)}</pre>
      </details>
    </div>
  );
}

// ---------------------------------------------------------------
// Upload tab
// ---------------------------------------------------------------

function UploadTab({ onIndexed }) {
  const [files, setFiles] = useState([]);
  const [dragOver, setDragOver] = useState(false);
  const [corpusName, setCorpusName] = useState('');
  const [category, setCategory] = useState('General');
  const [chunkSize, setChunkSize] = useState('');
  const [overlap, setOverlap] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const addFiles = (list) => setFiles((prev) => [...prev, ...Array.from(list)]);
  const removeFile = (idx) => setFiles((prev) => prev.filter((_, i) => i !== idx));

  const submit = async (e) => {
    e.preventDefault();
    if (!files.length || !corpusName.trim()) return;
    setLoading(true); setError(null); setResult(null);
    try {
      const form = new FormData();
      form.append('corpus_name', corpusName);
      form.append('category', category);
      if (chunkSize) form.append('chunk_size', chunkSize);
      if (overlap) form.append('overlap', overlap);
      files.forEach((f) => form.append('files', f));

      const res = await fetch(`${API_BASE}/api/upload`, { method: 'POST', body: form });
      if (!res.ok) {
        let detail = res.statusText;
        try { const j = await res.json(); detail = j.detail || detail; } catch (_) {}
        throw new Error(detail);
      }
      const json = await res.json();
      setResult(json);
      setFiles([]);
      onIndexed && onIndexed();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid lg:grid-cols-2 gap-6">
      <form onSubmit={submit} className="flex flex-col gap-4">
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => { e.preventDefault(); setDragOver(false); addFiles(e.dataTransfer.files); }}
          className={classNames(
            'rounded-lg border-2 border-dashed px-6 py-10 flex flex-col items-center justify-center gap-2 text-center transition-colors',
            dragOver ? 'border-cyan-400 bg-cyan-950/20' : 'border-slate-800 bg-slate-900/30'
          )}
        >
          <UploadCloud className={classNames('h-7 w-7', dragOver ? 'text-cyan-400' : 'text-slate-600')} />
          <p className="text-sm text-slate-400">Drop files here, or</p>
          <label className="text-sm font-medium text-cyan-400 hover:text-cyan-300 cursor-pointer">
            browse files
            <input type="file" multiple className="hidden" onChange={(e) => addFiles(e.target.files)}
              accept=".pdf,.docx,.txt,.md,.json,.csv" />
          </label>
          <p className="text-[11px] font-mono text-slate-600 mt-1">.pdf · .docx · .txt · .md · .json · .csv</p>
        </div>

        {files.length > 0 && (
          <div className="flex flex-col gap-1.5">
            {files.map((f, i) => (
              <div key={i} className="flex items-center justify-between rounded-md bg-slate-900/60 border border-slate-800 px-3 py-1.5">
                <div className="flex items-center gap-2 min-w-0">
                  <FileText className="h-3.5 w-3.5 text-slate-600 shrink-0" />
                  <span className="text-xs text-slate-300 truncate">{f.name}</span>
                </div>
                <button type="button" onClick={() => removeFile(i)} className="text-slate-600 hover:text-rose-400 shrink-0">
                  <X className="h-3.5 w-3.5" />
                </button>
              </div>
            ))}
          </div>
        )}

        <div className="grid grid-cols-2 gap-3">
          <Field label="corpus name">
            <input className={inputCls} value={corpusName} onChange={(e) => setCorpusName(e.target.value)} placeholder="my_corpus" />
          </Field>
          <Field label="category">
            <input className={inputCls} value={category} onChange={(e) => setCategory(e.target.value)} placeholder="General" />
          </Field>
          <Field label="chunk size (optional)">
            <input type="number" className={inputCls} value={chunkSize} onChange={(e) => setChunkSize(e.target.value)} placeholder="default" />
          </Field>
          <Field label="overlap (optional)">
            <input type="number" className={inputCls} value={overlap} onChange={(e) => setOverlap(e.target.value)} placeholder="default" />
          </Field>
        </div>

        <button
          type="submit"
          disabled={loading || !files.length || !corpusName.trim()}
          className="inline-flex items-center justify-center gap-2 rounded-md bg-cyan-500 hover:bg-cyan-400 disabled:bg-slate-800 disabled:text-slate-600 text-slate-950 font-semibold text-sm px-4 py-2.5 transition-colors"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Database className="h-4 w-4" />}
          {loading ? 'Indexing…' : 'Build index'}
        </button>
      </form>

      <div className="flex flex-col gap-3">
        {error && <ErrorNote message={error} />}
        {!error && !result && (
          <EmptyState icon={Database} title="Nothing indexed yet" hint="Uploaded files are chunked and embedded on the fly, then become searchable as a new corpus." />
        )}
        {result && (
          <div className="rounded-lg border border-emerald-900/50 bg-emerald-950/20 p-4 flex flex-col gap-2">
            <div className="flex items-center gap-2 text-emerald-400">
              <CheckCircle2 className="h-4 w-4" />
              <span className="text-sm font-medium">{result.message}</span>
            </div>
            <pre className="text-xs font-mono text-slate-400 overflow-x-auto">{JSON.stringify(result.details, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------
// Chunks tab
// ---------------------------------------------------------------

function ChunksTab({ corpus }) {
  const [search, setSearch] = useState('');
  const [limit, setLimit] = useState(50);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const load = useCallback(() => {
    if (!corpus) return;
    setLoading(true); setError(null);
    const params = new URLSearchParams();
    if (search) params.set('search', search);
    params.set('limit', String(limit));
    apiFetch(`/api/chunks/${encodeURIComponent(corpus)}?${params.toString()}`)
      .then(setData)
      .catch((err) => { setError(err.message); setData(null); })
      .finally(() => setLoading(false));
  }, [corpus, search, limit]);

  useEffect(() => { load(); }, [corpus]); // eslint-disable-line

  return (
    <div className="flex flex-col gap-4">
      <form onSubmit={(e) => { e.preventDefault(); load(); }} className="flex flex-wrap items-end gap-3">
        <Field label="filter text">
          <input className={classNames(inputCls, 'w-64')} value={search} onChange={(e) => setSearch(e.target.value)} placeholder="substring match…" />
        </Field>
        <Field label="limit">
          <input type="number" className={classNames(inputCls, 'w-24')} value={limit} onChange={(e) => setLimit(e.target.value)} />
        </Field>
        <button type="submit" disabled={!corpus}
          className="inline-flex items-center gap-2 rounded-md border border-slate-700 hover:border-cyan-500/60 text-slate-200 text-sm px-4 py-2 transition-colors">
          <Search className="h-3.5 w-3.5" /> Filter
        </button>
      </form>

      {error && <ErrorNote message={error} />}
      {loading && (
        <div className="flex items-center justify-center py-16 gap-2 text-slate-500">
          <Loader2 className="h-4 w-4 animate-spin" /> <span className="text-sm font-mono">loading chunks…</span>
        </div>
      )}
      {!loading && !error && !data && (
        <EmptyState icon={FileStack} title="No corpus selected" hint="Pick a corpus to browse its indexed chunks." />
      )}
      {data && !loading && (
        <>
          <p className="text-[11px] font-mono uppercase tracking-widest text-slate-500">
            showing {data.returned} of {data.total_matches}
          </p>
          <div className="rounded-lg border border-slate-800 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-900/80 border-b border-slate-800 text-left">
                  <th className="px-3 py-2 font-mono text-[11px] uppercase tracking-widest text-slate-500 w-14">#</th>
                  <th className="px-3 py-2 font-mono text-[11px] uppercase tracking-widest text-slate-500">Text</th>
                  <th className="px-3 py-2 font-mono text-[11px] uppercase tracking-widest text-slate-500 hidden md:table-cell">Source</th>
                  <th className="px-3 py-2 font-mono text-[11px] uppercase tracking-widest text-slate-500 text-right">Words</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/70">
                {data.chunks.map((c, i) => (
                  <tr key={c.chunk_id} className="hover:bg-slate-900/40">
                    <td className="px-3 py-2.5 font-mono text-xs text-slate-600 align-top">{String(c.chunk_index ?? i).padStart(2, '0')}</td>
                    <td className="px-3 py-2.5 text-slate-300 align-top max-w-md">
                      <span className="line-clamp-2" title={c.text}>{c.text}</span>
                    </td>
                    <td className="px-3 py-2.5 font-mono text-xs text-slate-500 align-top hidden md:table-cell truncate max-w-[160px]">{c.source_file}</td>
                    <td className="px-3 py-2.5 font-mono text-xs text-slate-500 align-top text-right tabular-nums">{c.word_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

// ---------------------------------------------------------------
// App shell
// ---------------------------------------------------------------

export default function RetrievalStudio() {
  const [connStatus, setConnStatus] = useState('checking');
  const [corpora, setCorpora] = useState([]);
  const [corpus, setCorpus] = useState('');
  const [activeTab, setActiveTab] = useState('compare');
  const [corporaError, setCorporaError] = useState(null);

  const loadCorpora = useCallback(() => {
    apiFetch('/api/corpora')
      .then((res) => {
        setCorpora(res.corpora || []);
        setConnStatus('online');
        setCorporaError(null);
        if (res.corpora && res.corpora.length && !corpus) setCorpus(res.corpora[0].corpus_name);
      })
      .catch((err) => {
        setConnStatus('offline');
        setCorporaError(err.message);
      });
  }, [corpus]);

  useEffect(() => { loadCorpora(); }, []); // eslint-disable-line

  const activeCorpusMeta = corpora.find((c) => c.corpus_name === corpus);

  return (
    <div className="min-h-screen w-full bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/95 backdrop-blur sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-5 py-3.5 flex items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <div className="h-7 w-7 rounded bg-gradient-to-br from-cyan-400 to-amber-400 flex items-center justify-center">
              <span className="text-slate-950 font-black text-xs">R</span>
            </div>
            <div className="flex flex-col leading-none">
              <span className="font-black tracking-tight text-sm">RETRIEVAL STUDIO</span>
              <span className="text-[10px] font-mono text-slate-600 tracking-widest">SEMANTIC · BM25 · IR EVAL</span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="relative">
              <select
                value={corpus}
                onChange={(e) => setCorpus(e.target.value)}
                className="appearance-none bg-slate-900 border border-slate-800 rounded-md pl-3 pr-8 py-1.5 text-xs font-mono text-slate-200 outline-none focus:border-cyan-500/60 max-w-[180px] truncate"
              >
                {corpora.length === 0 && <option value="">no corpora</option>}
                {corpora.map((c) => (
                  <option key={c.corpus_name} value={c.corpus_name}>{c.display_name}</option>
                ))}
              </select>
              <ChevronDown className="h-3.5 w-3.5 text-slate-600 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
            <Pulse status={connStatus} />
          </div>
        </div>

        {/* Tabs */}
        <nav className="max-w-7xl mx-auto px-5 flex gap-1 overflow-x-auto">
          {TABS.map((t) => {
            const Icon = t.icon;
            const active = activeTab === t.id;
            return (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id)}
                className={classNames(
                  'flex items-center gap-2 px-3.5 py-2.5 border-b-2 text-xs font-medium whitespace-nowrap transition-colors',
                  active ? 'border-cyan-400 text-slate-100' : 'border-transparent text-slate-500 hover:text-slate-300'
                )}
              >
                <Icon className={classNames('h-3.5 w-3.5', active && 'text-cyan-400')} />
                {t.label}
              </button>
            );
          })}
        </nav>
      </header>

      {/* Body */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-5 py-6">
        {connStatus === 'offline' && (
          <div className="mb-5">
            <ErrorNote message={`Can't reach ${API_BASE} — start the FastAPI server and refresh. (${corporaError || ''})`} />
          </div>
        )}

        {activeCorpusMeta && (
          <div className="flex flex-wrap items-center gap-x-5 gap-y-1 mb-5 text-[11px] font-mono text-slate-500">
            <span>{activeCorpusMeta.total_chunks} chunks</span>
            <span>{activeCorpusMeta.total_documents} documents</span>
            <span>{activeCorpusMeta.embedding_model} · {activeCorpusMeta.vector_dimension}d</span>
            <span className={activeCorpusMeta.has_eval_set ? 'text-emerald-500' : 'text-slate-600'}>
              {activeCorpusMeta.has_eval_set ? 'eval set present' : 'no eval set'}
            </span>
          </div>
        )}

        {!corpus && connStatus === 'online' && (
          <EmptyState icon={Circle} title="No corpus indexed" hint="Head to the Ingest tab to upload files and build your first corpus." />
        )}

        {corpus && (
          <>
            {activeTab === 'compare' && <CompareTab corpus={corpus} />}
            {activeTab === 'sentence' && <SentenceTab corpus={corpus} />}
            {activeTab === 'eval' && <EvalTab corpus={corpus} />}
            {activeTab === 'chunks' && <ChunksTab corpus={corpus} />}
          </>
        )}
        {activeTab === 'upload' && <UploadTab onIndexed={loadCorpora} />}
      </main>

      <footer className="border-t border-slate-900 px-5 py-3">
        <p className="max-w-7xl mx-auto text-[10px] font-mono text-slate-700 tracking-wider">
          {API_BASE} · FAISS + MiniLM vs BM25
        </p>
      </footer>
    </div>
  );
}
