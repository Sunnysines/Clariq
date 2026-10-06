import { Link } from 'react-router-dom';
import { ArrowRight, Clock } from 'lucide-react';

export default function HistoryPage() {
  const sampleHistory = [
    {
      id: 'demo-career-2026',
      question: 'Which Indian city is best for an entry-level AI/ML career in 2026?',
      mode: 'career',
      status: 'completed',
      date: 'Today',
      score: 89,
    },
    {
      id: 'demo-company-ai',
      question: 'Which Indian companies currently show strong AI hiring signals?',
      mode: 'company',
      status: 'completed',
      date: 'Yesterday',
      score: 84,
    },
    {
      id: 'demo-tech-agent',
      question: 'Is AI agent development worth learning for a software engineering student in 2026?',
      mode: 'technology',
      status: 'completed',
      date: '3 days ago',
      score: 93,
    },
  ];

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="mb-8 border-b border-border pb-6">
        <div className="flex items-center gap-2 mb-2">
          <span className="rounded bg-accent/20 px-2.5 py-0.5 text-xs font-semibold text-accent uppercase">
            Investigation Logs
          </span>
        </div>
        <h1 className="text-2xl font-bold md:text-3xl">Decision History</h1>
        <p className="mt-1 text-sm text-text-secondary">
          Review past decisions, comparative runs, and audit trails.
        </p>
      </div>

      <div className="space-y-4">
        {sampleHistory.map((item) => (
          <div
            key={item.id}
            className="card p-5 flex flex-col md:flex-row md:items-center justify-between gap-4"
          >
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="rounded bg-bg-secondary px-2 py-0.5 text-xs font-semibold text-accent uppercase">
                  {item.mode}
                </span>
                <span className="flex items-center gap-1 text-xs text-text-muted">
                  <Clock size={12} />
                  {item.date}
                </span>
              </div>
              <h3 className="text-base font-semibold text-text-primary">
                {item.question}
              </h3>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-xs text-text-muted">Score</div>
                <div className="text-lg font-bold text-accent">{item.score}/100</div>
              </div>
              <Link
                to={`/dashboard?id=${item.id}`}
                className="flex items-center gap-1.5 rounded-xl bg-bg-secondary hover:bg-accent/20 border border-border px-3.5 py-2 text-xs font-semibold text-text-primary transition"
              >
                View
                <ArrowRight size={14} />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
