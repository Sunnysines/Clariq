import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Clock, RefreshCw, Loader2 } from 'lucide-react';
import { getAnalyses } from '../services/api';
import type { AnalysisListItem } from '../types';

export default function HistoryPage() {
  const [items, setItems] = useState<AnalysisListItem[]>([]);
  const [loading, setLoading] = useState(true);

  const sampleHistory: AnalysisListItem[] = [
    {
      id: 'demo-career-2026',
      question: 'Which Indian city is best for an entry-level AI/ML career in 2026?',
      intent: 'career',
      mode: 'career',
      status: 'completed',
      overall_score: 89,
      confidence_level: 'HIGH',
      created_at: new Date(Date.now() - 3600000).toISOString(),
      completed_at: new Date(Date.now() - 3500000).toISOString(),
    },
    {
      id: 'demo-company-ai',
      question: 'Which Indian companies currently show strong AI hiring signals?',
      intent: 'company',
      mode: 'company',
      status: 'completed',
      overall_score: 84,
      confidence_level: 'HIGH',
      created_at: new Date(Date.now() - 86400000).toISOString(),
      completed_at: new Date(Date.now() - 86300000).toISOString(),
    },
    {
      id: 'demo-tech-agent',
      question: 'Is AI agent development worth learning for a software engineering student in 2026?',
      intent: 'technology',
      mode: 'technology',
      status: 'completed',
      overall_score: 93,
      confidence_level: 'HIGH',
      created_at: new Date(Date.now() - 259200000).toISOString(),
      completed_at: new Date(Date.now() - 259100000).toISOString(),
    },
  ];

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await getAnalyses(30);
      if (res && res.items && res.items.length > 0) {
        setItems(res.items);
      } else {
        setItems(sampleHistory);
      }
    } catch {
      // Fallback gracefully to samples if backend is unreachable
      setItems(sampleHistory);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const formatDate = (dateStr: string) => {
    try {
      const d = new Date(dateStr);
      const now = new Date();
      const diffMs = now.getTime() - d.getTime();
      const diffHrs = Math.floor(diffMs / (1000 * 60 * 60));
      if (diffHrs < 1) return 'Just now';
      if (diffHrs < 24) return `${diffHrs}h ago`;
      const diffDays = Math.floor(diffHrs / 24);
      if (diffDays === 1) return 'Yesterday';
      if (diffDays < 7) return `${diffDays} days ago`;
      return d.toLocaleDateString();
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 animate-fade-in">
      <div className="mb-8 border-b border-border pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="rounded bg-accent/20 px-2.5 py-0.5 text-xs font-semibold text-accent uppercase">
              Investigation Logs
            </span>
          </div>
          <h1 className="text-2xl font-bold md:text-3xl">Decision History</h1>
          <p className="mt-1 text-sm text-text-secondary">
            Review past decision queries, multi-engine verification runs, and audit trails.
          </p>
        </div>

        <button
          onClick={fetchHistory}
          disabled={loading}
          className="flex items-center gap-2 self-start md:self-auto rounded-xl border border-border bg-bg-card px-3.5 py-2 text-xs font-semibold text-text-secondary transition hover:border-accent hover:text-accent disabled:opacity-50"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {loading && items.length === 0 ? (
        <div className="card p-12 text-center">
          <Loader2 className="mx-auto mb-3 h-8 w-8 animate-spin text-accent" />
          <p className="text-sm text-text-secondary">Loading decision investigation logs...</p>
        </div>
      ) : (
        <div className="space-y-4">
          {items.map((item) => (
            <div
              key={item.id}
              className="card p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 transition hover:border-accent/40"
            >
              <div className="space-y-1.5 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded bg-bg-secondary px-2 py-0.5 text-xs font-semibold text-accent uppercase">
                    {item.mode || item.intent || 'career'}
                  </span>
                  <span
                    className={`rounded px-2 py-0.5 text-[10px] font-bold uppercase ${
                      item.status === 'completed'
                        ? 'bg-success/20 text-success'
                        : item.status === 'processing'
                        ? 'bg-warning/20 text-warning animate-pulse'
                        : 'bg-danger/20 text-danger'
                    }`}
                  >
                    {item.status}
                  </span>
                  {item.confidence_level && (
                    <span className="rounded bg-bg-secondary px-2 py-0.5 text-[10px] font-semibold text-text-secondary">
                      {item.confidence_level} Confidence
                    </span>
                  )}
                  <span className="flex items-center gap-1 text-xs text-text-muted">
                    <Clock size={12} />
                    {formatDate(item.created_at)}
                  </span>
                </div>
                <h3 className="text-base font-semibold text-text-primary">
                  {item.question}
                </h3>
              </div>

              <div className="flex items-center gap-4">
                {item.overall_score !== null && item.overall_score !== undefined && (
                  <div className="text-right">
                    <div className="text-xs text-text-muted">Score</div>
                    <div className="text-lg font-bold text-accent">
                      {Math.round(item.overall_score)}/100
                    </div>
                  </div>
                )}
                <Link
                  to={
                    item.status === 'processing'
                      ? `/analyze?id=${item.id}`
                      : `/dashboard?id=${item.id}`
                  }
                  className="flex items-center gap-1.5 rounded-xl bg-bg-secondary hover:bg-accent hover:text-white border border-border px-3.5 py-2 text-xs font-semibold text-text-primary transition"
                >
                  {item.status === 'processing' ? 'Track' : 'View'}
                  <ArrowRight size={14} />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
