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
  return (
    <div className="card p-6 md:p-8 border-accent/50 bg-gradient-to-br from-bg-card via-bg-secondary to-bg-card relative overflow-hidden">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 border-b border-border pb-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-accent text-white">
              <Trophy size={14} />
            </span>
            <span className="text-xs font-bold uppercase tracking-wider text-accent">
              Primary Recommendation
            </span>
          </div>
          <h2 className="text-3xl md:text-4xl font-black text-text-primary">
            {topEntity}
          </h2>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-xs text-text-muted">Recommendation Score</div>
            <div className="text-3xl font-extrabold text-accent">{Math.round(score)}<span className="text-base text-text-muted">/100</span></div>
          </div>
          <ConfidenceBadge level={confidenceLevel} score={confidence} />
        </div>
      </div>

      <p className="text-sm md:text-base text-text-secondary leading-relaxed mb-6 font-medium">
        {summary}
      </p>

      {/* Grid of Key Reasons and Recommended Next Actions */}
      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded-xl border border-border bg-bg-primary/50 p-4">
          <h4 className="text-xs font-bold uppercase tracking-wider text-text-muted mb-3 flex items-center gap-1.5">
            <CheckCircle2 size={14} className="text-success" />
            Core Decision Drivers
          </h4>
          <ul className="space-y-2 text-xs text-text-secondary">
            {reasons.map((r, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-accent font-bold">•</span>
                <span>{r}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="rounded-xl border border-accent/20 bg-accent/5 p-4 flex flex-col justify-between">
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-accent mb-3 flex items-center gap-1.5">
              <Sparkles size={14} className="text-accent" />
              Recommended Next Actions
            </h4>
            <ul className="space-y-2 text-xs text-text-secondary">
              {actions.map((act, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-accent font-bold">{i + 1}.</span>
                  <span>{act}</span>
                </li>
              ))}
            </ul>
          </div>

          {onExploreActions && (
            <button
              onClick={onExploreActions}
              className="mt-4 inline-flex items-center justify-center gap-2 rounded-lg bg-accent px-4 py-2 text-xs font-bold text-white hover:bg-accent-hover transition self-start"
            >
              Action Layer
              <ArrowRight size={14} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
