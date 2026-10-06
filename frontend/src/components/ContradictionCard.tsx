import { AlertTriangle, ArrowRight } from 'lucide-react';
import type { ContradictionItem } from '../types';

interface ContradictionCardProps {
  contradiction: ContradictionItem;
  onViewEvidence?: (evidenceIds: string[]) => void;
}

export default function ContradictionCard({ contradiction, onViewEvidence }: ContradictionCardProps) {
  const sev = (contradiction.severity || 'medium').toLowerCase();
  const sevColor =
    sev === 'high'
      ? 'border-danger/40 bg-danger/10 text-danger'
      : 'border-warning/40 bg-warning/10 text-warning';

  return (
    <div className={`card p-5 border ${sevColor}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <AlertTriangle size={16} />
          <span className="text-xs font-bold uppercase tracking-wider">
            Conflict Detected: {contradiction.entity_name || 'Entity'}
          </span>
        </div>
        <span className="rounded-md border border-current px-2 py-0.5 text-[10px] font-bold uppercase">
          {sev} Severity
        </span>
      </div>

      <p className="text-sm font-semibold text-text-primary mb-3 leading-snug">
        {contradiction.description}
      </p>

      <div className="grid gap-2 sm:grid-cols-2 text-xs my-3 bg-bg-secondary/60 p-3 rounded-lg border border-border">
        <div>
          <span className="font-bold text-success block mb-0.5">Positive Signal</span>
          <span className="text-text-secondary">{contradiction.positive_signal || 'Hiring/Growth signals'}</span>
        </div>
        <div>
          <span className="font-bold text-danger block mb-0.5">Opposing Signal</span>
          <span className="text-text-secondary">{contradiction.negative_signal || 'Workforce reductions/freezes'}</span>
        </div>
      </div>

      {contradiction.evidence_ids && contradiction.evidence_ids.length > 0 && onViewEvidence && (
        <button
          onClick={() => onViewEvidence(contradiction.evidence_ids!)}
          className="mt-2 inline-flex items-center gap-1 text-xs text-accent hover:underline font-semibold"
        >
          Inspect conflicting evidence sources
          <ArrowRight size={12} />
        </button>
      )}
    </div>
  );
}
