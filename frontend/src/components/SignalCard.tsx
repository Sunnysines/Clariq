import { TrendingUp, TrendingDown, Minus, CheckCircle2 } from 'lucide-react';
import type { SignalItem } from '../types';

interface SignalCardProps {
  signal: SignalItem;
  onViewEvidence?: (evidenceIds: string[]) => void;
}

export default function SignalCard({ signal, onViewEvidence }: SignalCardProps) {
  const isPos = signal.direction === 'positive';
  const isNeg = signal.direction === 'negative';

  const DirIcon = isPos ? TrendingUp : isNeg ? TrendingDown : Minus;
  const badgeColor = isPos
    ? 'bg-success/15 text-success border-success/30'
    : isNeg
    ? 'bg-danger/15 text-danger border-danger/30'
    : 'bg-text-muted/15 text-text-secondary border-border';

  return (
    <div className="card p-4 flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className={`inline-flex items-center gap-1 rounded border px-2 py-0.5 text-xs font-bold uppercase tracking-wider ${badgeColor}`}>
            <DirIcon size={12} />
            {signal.type}
          </span>
          <span className="text-xs font-bold text-accent">
            Strength: {Math.round(signal.strength)}%
          </span>
        </div>

        <p className="text-sm font-medium text-text-primary mb-2">
          {signal.description || `${signal.type} signal detected for ${signal.entity || 'entity'}.`}
        </p>
      </div>

      <div className="border-t border-border pt-2.5 mt-2 flex items-center justify-between text-xs text-text-muted">
        <span className="flex items-center gap-1">
          <CheckCircle2 size={12} className="text-accent" />
          {signal.evidence_count} evidence {signal.evidence_count === 1 ? 'item' : 'items'}
        </span>

        {signal.evidence_ids && signal.evidence_ids.length > 0 && onViewEvidence && (
          <button
            onClick={() => onViewEvidence(signal.evidence_ids!)}
            className="text-xs text-accent hover:underline font-semibold"
          >
            Inspect Evidence →
          </button>
        )}
      </div>
    </div>
  );
}
