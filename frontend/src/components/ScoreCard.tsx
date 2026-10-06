import { HelpCircle } from 'lucide-react';

interface ScoreCardProps {
  title: string;
  score: number;
  maxScore?: number;
  weightLabel?: string;
  onWhyClick?: () => void;
  color?: string;
}

export default function ScoreCard({
  title,
  score,
  maxScore = 100,
  weightLabel,
  onWhyClick,
  color = 'bg-accent',
}: ScoreCardProps) {
  const percentage = Math.round((score / maxScore) * 100);

  return (
    <div className="card p-5 relative overflow-hidden flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between text-xs mb-2">
          <span className="font-semibold uppercase tracking-wider text-text-muted">{title}</span>
          {weightLabel && (
            <span className="rounded bg-bg-secondary px-2 py-0.5 text-[11px] text-text-secondary">
              {weightLabel}
            </span>
          )}
        </div>

        <div className="flex items-baseline gap-2 my-2">
          <span className="text-4xl font-extrabold text-text-primary">{Math.round(score)}</span>
          <span className="text-sm text-text-muted">/ {maxScore}</span>
        </div>

        <div className="h-1.5 w-full rounded-full bg-bg-secondary overflow-hidden my-3">
          <div
            className={`h-full rounded-full ${color} transition-all duration-700`}
            style={{ width: `${Math.min(100, Math.max(0, percentage))}%` }}
          />
        </div>
      </div>

      {onWhyClick && (
        <button
          onClick={onWhyClick}
          className="mt-2 flex items-center gap-1.5 text-xs text-accent hover:text-accent-hover font-semibold transition self-start"
        >
          <HelpCircle size={13} />
          Why?
        </button>
      )}
    </div>
  );
}
