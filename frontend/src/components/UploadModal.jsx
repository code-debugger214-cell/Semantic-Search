import React, { useState } from 'react';
import { X, UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

const CATEGORIES = [
  { id: 'Research Papers', label: '📄 Research Papers (PDF/TXT)', desc: 'Multi-page academic papers & abstracts (400w chunk size)' },
  { id: 'FAQs & Web', label: '🌐 FAQs & Web Knowledge (JSON/TXT)', desc: 'Q&A pairs, web scrapes & documentation (200w chunk size)' },
  { id: 'Personal Notes', label: '📝 Personal Notes (MD/TXT)', desc: 'Notion/Obsidian markdown & plain notes (300w chunk size)' },
  { id: 'General', label: '⚡ General Documents', desc: 'Any general text, docx, csv or code files' },
];

export default function UploadModal({ isOpen, onClose, onUploadSuccess }) {
  const [corpusName, setCorpusName] = useState('');
  const [category, setCategory] = useState('General');
  const [files, setFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  if (!isOpen) return null;

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFiles(Array.from(e.target.files));
      setErrorMsg('');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFiles(Array.from(e.dataTransfer.files));
      setErrorMsg('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!corpusName.trim()) {
      setErrorMsg('Please enter a name for your new corpus.');
      return;
    }
    if (files.length === 0) {
      setErrorMsg('Please select at least one document file.');
      return;
    }

    setIsUploading(true);
    setErrorMsg('');
    setSuccessMsg('');

    const formData = new FormData();
    formData.append('corpus_name', corpusName);
    formData.append('category', category);
    files.forEach((f) => formData.append('files', f));

    try {
      const res = await fetch('http://127.0.0.1:8000/api/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Upload failed');
      }

      setSuccessMsg(`Corpus '${data.details.corpus_name}' created with ${data.details.total_chunks} chunks!`);
      setTimeout(() => {
        setIsUploading(false);
        onUploadSuccess(data.details.corpus_name);
        onClose();
      }, 1500);
    } catch (err) {
      setIsUploading(false);
      setErrorMsg(err.message || 'An error occurred during file ingestion.');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md">
      <div className="glass-panel w-full max-w-xl p-6 space-y-6 relative border border-white/20 shadow-2xl">
        {/* Close Button */}
        <button
          onClick={onClose}
          disabled={isUploading}
          className="absolute top-4 right-4 p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition-all"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="space-y-1">
          <h2 className="text-xl font-extrabold text-white flex items-center gap-2">
            <UploadCloud className="w-6 h-6 text-emerald-400" />
            Universal Document Ingestion
          </h2>
          <p className="text-xs text-slate-400">
            Upload PDF, DOCX, Markdown, Text, JSON or CSV files to build FAISS + BM25 indexes on-the-fly.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Corpus Name */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Corpus Name / Title
            </label>
            <input
              type="text"
              value={corpusName}
              onChange={(e) => setCorpusName(e.target.value)}
              placeholder="e.g. My Research Papers, Company FAQs"
              className="w-full bg-slate-900 text-white placeholder-slate-500 px-4 py-3 rounded-xl border border-white/15 text-sm focus:outline-none focus:border-emerald-500 font-medium"
            />
          </div>

          {/* Category Selection */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Document Category
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat.id}
                  type="button"
                  onClick={() => setCategory(cat.id)}
                  className={`p-3 rounded-xl text-left border text-xs transition-all ${
                    category === cat.id
                      ? 'bg-emerald-950/80 border-emerald-500 text-emerald-200 shadow-md'
                      : 'bg-slate-900/60 border-white/10 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <div className="font-bold mb-0.5">{cat.label}</div>
                  <div className="text-[10px] opacity-75">{cat.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Drag & Drop Dropzone */}
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            className="border-2 border-dashed border-white/20 hover:border-emerald-500/50 rounded-2xl p-6 text-center space-y-3 bg-slate-900/40 transition-colors cursor-pointer"
          >
            <input
              type="file"
              multiple
              accept=".pdf,.docx,.doc,.txt,.md,.json,.csv"
              onChange={handleFileChange}
              className="hidden"
              id="file-input-upload"
            />
            <label htmlFor="file-input-upload" className="cursor-pointer space-y-2 block">
              <UploadCloud className="w-10 h-10 mx-auto text-emerald-400" />
              <div className="text-sm font-semibold text-slate-200">
                Click to browse files or drag & drop here
              </div>
              <div className="text-xs text-slate-400">
                Supports <code className="text-emerald-300">.pdf</code>, <code className="text-emerald-300">.docx</code>, <code className="text-emerald-300">.md</code>, <code className="text-emerald-300">.txt</code>, <code className="text-emerald-300">.json</code>, <code className="text-emerald-300">.csv</code>
              </div>
            </label>

            {files.length > 0 && (
              <div className="pt-2 text-left border-t border-white/10 space-y-1">
                <div className="text-xs font-bold text-slate-300">Selected Files ({files.length}):</div>
                <div className="max-h-24 overflow-y-auto space-y-1 pr-1">
                  {files.map((f, i) => (
                    <div key={i} className="text-xs text-emerald-300 flex items-center gap-1 font-mono">
                      <FileText className="w-3 h-3 text-slate-400" />
                      {f.name} ({(f.size / 1024).toFixed(1)} KB)
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Feedback Messages */}
          {errorMsg && (
            <div className="p-3 rounded-xl bg-rose-950/80 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              {errorMsg}
            </div>
          )}

          {successMsg && (
            <div className="p-3 rounded-xl bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
              {successMsg}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isUploading}
            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-sm shadow-lg shadow-emerald-900/30 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {isUploading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Parsing, Embedding & Building FAISS Index...
              </>
            ) : (
              <>⚡ Process & Build Index</>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
