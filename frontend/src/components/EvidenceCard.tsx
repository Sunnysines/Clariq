import { ExternalLink, Calendar, MapPin, Building } from 'lucide-react';
import type { EvidenceItem } from '../types';
import SourceBadge from './SourceBadge';

interface EvidenceCardProps {
  evidence: EvidenceItem;
}

export default function EvidenceCard({ evidence }: EvidenceCardProps) {
  const publishedDate = evidence.published_at
    ? new Date(evidence.published_at).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    : null;

  return (
    <div className="card p-5 flex flex-col justify-between hover:border-accent transition-all">
      <div>
        <div className="flex items-center justify-between mb-3">
          <SourceBadge sourceType={evidence.source_type} sourceName={evidence.source} />
          <div className="flex items-center gap-1.5 text-xs">
            <span className="text-text-muted">Strength:</span>
            <span className="font-bold text-accent">
              {Math.round(evidence.evidence_strength ?? 70)}%
            </span>
          </div>
        </div>

        <h4 className="text-base font-bold text-text-primary mb-2 line-clamp-2">
          {evidence.title || 'Untitled Evidence Record'}
        </h4>

        <p className="text-xs text-text-secondary line-clamp-3 mb-4 leading-relaxed">
          {evidence.snippet || 'No descriptive excerpt provided.'}
        </p>

        {/* Metadata badges */}
        <div className="flex flex-wrap gap-2 text-[11px] text-text-muted mb-4">
          {evidence.entity && (
            <span className="inline-flex items-center gap-1 rounded bg-bg-secondary px-2 py-0.5 border border-border">
              <Building size={11} />
              {evidence.entity}
            </span>
          )}
          {evidence.location && (
            <span className="inline-flex items-center gap-1 rounded bg-bg-secondary px-2 py-0.5 border border-border">
              <MapPin size={11} />
              {evidence.location}
            </span>
          )}
          {publishedDate && (
            <span className="inline-flex items-center gap-1 rounded bg-bg-secondary px-2 py-0.5 border border-border">
              <Calendar size={11} />
              {publishedDate}
            </span>
          )}
        </div>
      </div>

      <div className="border-t border-border pt-3 flex items-center justify-between text-xs">
        <div className="flex items-center gap-3 text-text-muted">
          <span>Rel: <strong className="text-text-primary">{Math.round(evidence.relevance_score ?? 0)}%</strong></span>
          <span>Fresh: <strong className="text-text-primary">{Math.round(evidence.freshness_score ?? 0)}%</strong></span>
          <span>Trust: <strong className="text-text-primary">{Math.round(evidence.reliability_score ?? 0)}%</strong></span>
        </div>

        {evidence.url ? (
          <a
            href={evidence.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-accent hover:underline font-semibold"
          >
            Open Source
            <ExternalLink size={12} />
          </a>
        ) : (
          <span className="text-[11px] text-text-muted italic">Verified Engine Record</span>
        )}
      </div>
    </div>
  );
}
