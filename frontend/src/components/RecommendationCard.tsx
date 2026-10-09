import { CheckCircle2, ArrowRight, Trophy, Sparkles } from 'lucide-react';
import ConfidenceBadge from './ConfidenceBadge';

interface RecommendationCardProps {
  topEntity: string;
  score: number;
  confidence: number;
  confidenceLevel: string;
  summary: string;
  reasons: string[];
  actions: string[];
  onExploreActions?: () => void;
}

export default function RecommendationCard({
  topEntity,
  score,
  confidence,
  confidenceLevel,
  summary,
  reasons,
  actions,
  onExploreActions,
}: RecommendationCardProps) {
  const pct = Math.min(100, Math.max(0, Math.round(score)));
  const r = 44;
  const circ = 2 * Math.PI * r;

  return (
    <section
      aria-label="Primary recommendation"
      className="card relative overflow-hidden border-accent/40 p-6 md:p-8"
      style={{ background: 'linear-gradient(135deg, rgba(109,111,245,0.16) 0%, rgba(19,19,31,0.92) 45%, rgba(34,211,238,0.07) 100%)' }}
    >
      <div className="pointer-events-none absolute -left-24 -top-24 h-64 w-64 rounded-full bg-accent/20 blur-3xl" aria-hidden="true" />
      <div className="pointer-events-none absolute -bottom-24 right-0 h-56 w-56 rounded-full bg-cyan/10 blur-3xl" aria-hidden="true" />

      <div className="relative mb-6 flex flex-col justify-between gap-6 border-b border-border/70 pb-6 md:flex-row md:items-center">
        <div>
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-accent/40 bg-accent/10 px-3 py-1">
            <Trophy size={13} className="text-accent-hover" aria-hidden="true" />
            <span className="text-[11px] font-bold uppercase tracking-[0.14em] text-accent-hover">Primary Recommendation</span>
          </div>
          <h2 className="gradient-text text-4xl font-bold md:text-6xl">{topEntity}</h2>
        </div>

        <div className="flex items-center gap-5">
          <div className="relative h-28 w-28 shrink-0" role="img" aria-label={`Recommendation score ${pct} out of 100`}>
            <svg viewBox="0 0 100 100" className="-rotate-90">
              <defs>
                <linearGradient id="recRing" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stopColor="#6d6ff5" />
                  <stop offset="100%" stopColor="#22d3ee" />
                </linearGradient>
              </defs>
              <circle cx="50" cy="50" r={r} fill="none" stroke="#1e1e38" strokeWidth="8" />
              <circle
                cx="50"
                cy="50"
                r={r}
                fill="none"
                stroke="url(#recRing)"
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={circ}
                strokeDashoffset={circ * (1 - pct / 100)}
                className="ring-animated"
                style={{ ['--ring-circ' as string]: circ, filter: 'drop-shadow(0 0 8px rgba(109,111,245,0.6))' }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="font-display text-3xl font-bold leading-none text-text-primary">{pct}</span>
              <span className="mt-0.5 text-[10px] uppercase tracking-wider text-text-muted">/ 100</span>
            </div>
          </div>
          <ConfidenceBadge level={confidenceLevel} score={confidence} />
        </div>
      </div>

      <p className="relative mb-6 text-sm font-medium leading-relaxed text-text-secondary md:text-base">{summary}</p>

      <div className="relative grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-border bg-bg-primary/50 p-5">
          <h3 className="mb-3 flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-text-muted">
            <CheckCircle2 size={14} className="text-success" aria-hidden="true" />
            Core Decision Drivers
          </h3>
          <ul className="space-y-2.5 text-xs text-text-secondary">
            {reasons.map((r, i) => (
              <li key={i} className="flex items-start gap-2.5">
                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-success" aria-hidden="true" />
                <span className="leading-relaxed">{r}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="flex flex-col justify-between rounded-2xl border border-accent/25 bg-accent/5 p-5">
          <div>
            <h3 className="mb-3 flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-accent-hover">
              <Sparkles size={14} aria-hidden="true" />
              Recommended Next Actions
            </h3>
            <ul className="space-y-2.5 text-xs text-text-secondary">
              {actions.map((act, i) => (
                <li key={i} className="flex items-start gap-2.5">
                  <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-accent/25 text-[10px] font-bold text-accent-hover">
                    {i + 1}
                  </span>
                  <span className="leading-relaxed">{act}</span>
                </li>
              ))}
            </ul>
          </div>

          {onExploreActions && (
            <button onClick={onExploreActions} className="btn-primary mt-5 self-start !px-4 !py-2 text-xs">
              Action Layer
              <ArrowRight size={14} aria-hidden="true" />
            </button>
          )}
        </div>
      </div>
    </section>
  );
}
