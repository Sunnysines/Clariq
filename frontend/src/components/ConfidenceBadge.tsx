import { ShieldCheck, ShieldAlert, Shield } from 'lucide-react';
import type { ConfidenceLevel } from '../types';

interface ConfidenceBadgeProps {
  level: ConfidenceLevel | string;
  score?: number | null;
}

export default function ConfidenceBadge({ level, score }: ConfidenceBadgeProps) {
  const norm = (level || 'MEDIUM').toUpperCase();

  const isHigh = norm === 'HIGH';
  const isMed = norm === 'MEDIUM';

  const Icon = isHigh ? ShieldCheck : isMed ? Shield : ShieldAlert;
  const colorClass = isHigh
    ? 'bg-success/15 text-success border-success/30'
    : isMed
    ? 'bg-warning/15 text-warning border-warning/30'
    : 'bg-danger/15 text-danger border-danger/30';

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-bold tracking-wide uppercase ${colorClass}`}
    >
      <Icon size={14} />
      <span>
        {norm} CONFIDENCE {score !== undefined && score !== null ? `(${Math.round(score)}%)` : ''}
      </span>
    </span>
  );
}
