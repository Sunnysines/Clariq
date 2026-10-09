import { HelpCircle } from 'lucide-react';

interface ScoreCardProps {
  title: string;
  score: number;
  maxScore?: number;
  weightLabel?: string;
  onWhyClick?: () => void;
  color?: string;
}

function toneFor(pct: number) {
  if (pct >= 75) return { stroke: '#34d399', glow: 'rgba(52,211,153,0.35)' };
  if (pct >= 50) return { stroke: '#fbbf24', glow: 'rgba(251,191,36,0.30)' };
  return { stroke: '#f87171', glow: 'rgba(248,113,113,0.30)' };
}

export default function ScoreCard({
  title,
  score,
  maxScore = 100,
  weightLabel,
  onWhyClick,
}: ScoreCardProps) {
  const percentage = Math.min(100, Math.max(0, Math.round((score / maxScore) * 100)));
  const tone = toneFor(percentage);
  const r = 30;
  const circ = 2 * Math.PI * r;
  const offset = circ * (1 - percentage / 100);

  return (
    <div className="card relative flex flex-col justify-between overflow-hidden p-5">
      <div
        className="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full blur-2xl"
        style={{ background: tone.glow }}
        aria-hidden="true"
      />
      <div className="relative">
        <div className="mb-3 flex items-start justify-between gap-2">
          <span className="text-[11px] font-semibold uppercase leading-tight tracking-wider text-text-muted">{title}</span>
          {weightLabel && (
            <span className="shrink-0 rounded-md border border-border-subtle bg-bg-secondary px-1.5 py-0.5 text-[10px] text-text-secondary">
              {weightLabel}
            </span>
          )}
        </div>

        <div className="flex items-center gap-4">
          <div className="relative h-[76px] w-[76px] shrink-0" role="img" aria-label={`${title}: ${Math.round(score)} out of ${maxScore}`}>
            <svg viewBox="0 0 76 76" className="-rotate-90">
              <circle cx="38" cy="38" r={r} fill="none" stroke="#1e1e38" strokeWidth="7" />
              <circle
                cx="38"
                cy="38"
                r={r}
                fill="none"
                stroke={tone.stroke}
                strokeWidth="7"
                strokeLinecap="round"
                strokeDasharray={circ}
                strokeDashoffset={offset}
                className="ring-animated"
                style={{ ['--ring-circ' as string]: circ, filter: `drop-shadow(0 0 6px ${tone.glow})` }}
              />
            </svg>
            <span className="font-display absolute inset-0 flex items-center justify-center text-xl font-bold text-text-primary">
              {Math.round(score)}
            </span>
          </div>
          <div className="text-xs text-text-muted">
            <span className="font-display text-sm font-semibold" style={{ color: tone.stroke }}>
              {percentage}%
            </span>
            <div>of {maxScore}</div>
          </div>
        </div>
      </div>

      {onWhyClick && (
        <button
          onClick={onWhyClick}
          className="relative mt-4 flex items-center gap-1.5 self-start text-xs font-semibold text-accent-hover transition hover:text-white"
        >
          <HelpCircle size={13} aria-hidden="true" />
          Why?
        </button>
      )}
    </div>
  );
}
