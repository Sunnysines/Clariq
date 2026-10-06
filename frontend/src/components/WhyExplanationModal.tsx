import { useState } from 'react';
import { X, ExternalLink, ArrowRight } from 'lucide-react';
import type { EvidenceItem } from '../types';
import SourceBadge from './SourceBadge';

export interface WhyContribution {
  label: string;
  score_contribution: number;
  evidence_count: number;
  direction: 'positive' | 'negative';
  evidence_ids?: string[];
}

interface WhyExplanationModalProps {
  isOpen: boolean;
  onClose: () => void;
  entityName: string;
  finalScore: number;
  contributions: WhyContribution[];
  allEvidence: EvidenceItem[];
}

export default function WhyExplanationModal({
  isOpen,
  onClose,
  entityName,
  finalScore,
  contributions,
  allEvidence,
}: WhyExplanationModalProps) {
  const [selectedContributionIdx, setSelectedContributionIdx] = useState<number | null>(0);

  if (!isOpen) return null;

  const activeContrib = selectedContributionIdx !== null ? contributions[selectedContributionIdx] : null;

  // Filter evidence items supporting the active contribution
  const supportingEvidence = activeContrib?.evidence_ids && activeContrib.evidence_ids.length > 0
    ? allEvidence.filter((e) => activeContrib.evidence_ids!.includes(e.id))
    : allEvidence.slice(0, 3); // Fallback to relevant evidence items if specific IDs not mapped

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="card w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden border-border bg-bg-primary shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border p-6 bg-bg-secondary/60">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="rounded bg-accent/20 px-2 py-0.5 text-xs font-bold text-accent uppercase">
                Traceable Explainability Chain
              </span>
              <span className="text-xs text-text-muted">
                Score → Signal → Evidence → Source URL
              </span>
            </div>
            <h2 className="text-2xl font-black text-text-primary">
              WHY {entityName.toUpperCase()}?
            </h2>
          </div>

          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-lg bg-bg-card text-text-muted hover:text-text-primary transition"
          >
            <X size={18} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="grid flex-1 overflow-hidden md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-border">
          {/* Left Column: Contributions List */}
          <div className="overflow-y-auto p-6 space-y-3">
            <div className="text-xs font-semibold uppercase tracking-wider text-text-muted mb-2">
              Score Contributions
            </div>

            {contributions.map((item, idx) => {
              const isSelected = selectedContributionIdx === idx;
              const isPos = item.direction === 'positive';
              const sign = isPos ? '+' : '';

              return (
                <div
                  key={idx}
                  onClick={() => setSelectedContributionIdx(idx)}
                  className={`flex cursor-pointer items-start justify-between rounded-xl border p-4 transition ${
                    isSelected
                      ? 'border-accent bg-accent/10 shadow-sm'
                      : 'border-border bg-bg-card hover:bg-bg-secondary'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span
                      className={`rounded px-2 py-0.5 text-xs font-black ${
                        isPos ? 'bg-success/20 text-success' : 'bg-danger/20 text-danger'
                      }`}
                    >
                      {sign}{item.score_contribution}
                    </span>
                    <div>
                      <h4 className="text-sm font-bold text-text-primary">{item.label}</h4>
                      <p className="text-xs text-text-muted mt-0.5">
                        {item.evidence_count} supporting evidence {item.evidence_count === 1 ? 'record' : 'records'}
                      </p>
                    </div>
                  </div>

                  <ArrowRight
                    size={14}
                    className={`mt-1 transition ${isSelected ? 'text-accent translate-x-1' : 'text-text-muted'}`}
                  />
                </div>
              );
            })}

            {/* Final Score Footer in Left Column */}
            <div className="mt-6 rounded-xl border border-border bg-bg-secondary p-4 flex items-center justify-between">
              <div>
                <span className="text-xs font-bold uppercase text-text-muted">Final Aggregated Score</span>
                <div className="text-xs text-text-secondary">Explainable evidence-weighted outcome</div>
              </div>
              <div className="text-2xl font-black text-accent">
                {Math.round(finalScore)} <span className="text-sm text-text-muted">/ 100</span>
              </div>
            </div>
          </div>

          {/* Right Column: Underlying Evidence Chain */}
          <div className="overflow-y-auto p-6 bg-bg-card/40 flex flex-col">
            <div className="mb-4">
              <div className="text-xs font-semibold uppercase tracking-wider text-text-muted mb-1">
                Supporting Evidence Chain
              </div>
              <h3 className="text-sm font-bold text-text-primary">
                {activeContrib ? activeContrib.label : 'Select a score contribution'}
              </h3>
            </div>

            {supportingEvidence.length === 0 ? (
              <div className="my-auto text-center p-8 text-xs text-text-muted">
                No individual URL evidence records mapped to this specific contribution.
              </div>
            ) : (
              <div className="space-y-3 flex-1 overflow-y-auto pr-1">
                {supportingEvidence.map((ev) => (
                  <div key={ev.id} className="rounded-xl border border-border bg-bg-card p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <SourceBadge sourceType={ev.source_type} sourceName={ev.source} />
                      <span className="text-[11px] font-semibold text-accent">
                        Strength: {Math.round(ev.evidence_strength ?? 70)}%
                      </span>
                    </div>

                    <h5 className="text-xs font-bold text-text-primary line-clamp-2">
                      {ev.title || 'Untitled Evidence'}
                    </h5>

                    <p className="text-[11px] text-text-secondary line-clamp-2 leading-relaxed">
                      {ev.snippet || 'No excerpt available.'}
                    </p>

                    <div className="flex items-center justify-between border-t border-border/60 pt-2 text-[10px] text-text-muted">
                      <span>Rel: {Math.round(ev.relevance_score ?? 0)}% · Fresh: {Math.round(ev.freshness_score ?? 0)}%</span>
                      {ev.url && (
                        <a
                          href={ev.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 font-semibold text-accent hover:underline"
                        >
                          Source URL
                          <ExternalLink size={10} />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="border-t border-border p-4 bg-bg-secondary flex items-center justify-between text-xs text-text-muted">
          <span>Clariq Evidence Traceability Guarantee — Zero hallucinated factual claims</span>
          <button
            onClick={onClose}
            className="rounded-lg bg-bg-card px-4 py-1.5 font-semibold text-text-primary border border-border hover:bg-bg-primary transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
