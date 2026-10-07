import { useNavigate } from 'react-router-dom';
import { 
  Building2, 
  Briefcase, 
  Layers, 
  GitCompare, 
  RotateCcw, 
  Sparkles
} from 'lucide-react';

interface ActionLayerProps {
  analysisId: string;
  topEntity: string;
  topCompanies?: string[];
  conflictCount?: number;
}

export default function ActionLayer({
  analysisId,
  topEntity,
  topCompanies = [],
  conflictCount = 0,
}: ActionLayerProps) {
  const navigate = useNavigate();

  const actions = [
    `Focus your primary application pipeline and portfolio alignment on ${topEntity}.`,
    topCompanies.length > 0
      ? `Prioritize applications at detected hiring firms: ${topCompanies.slice(0, 3).join(', ')}.`
      : `Prioritize the strongest verified employer entities identified in ${topEntity}.`,
    'Review the highest-confidence job opportunities in the Evidence Explorer.',
    conflictCount > 0
      ? `Investigate the ${conflictCount} conflicting signal clusters before signing offers or relocating.`
      : 'Review salary and role requirements against current market indices.',
    'Monitor emerging search interest and hiring volume as 2026 projections evolve.',
  ];

  return (
    <div className="card p-6 md:p-8 border-accent/30 bg-bg-card relative overflow-hidden">
      <div className="flex items-center justify-between mb-4 border-b border-border pb-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Sparkles size={14} className="text-accent" />
            <span className="text-xs font-bold uppercase tracking-wider text-accent">
              Actionable Intelligence
            </span>
          </div>
          <h3 className="text-xl font-bold text-text-primary">
            RECOMMENDED ACTIONS
          </h3>
        </div>
        <span className="text-xs text-text-muted">
          Navigational & Analytical Next Steps
        </span>
      </div>

      {/* Action Checklist */}
      <div className="space-y-3 mb-8">
        {actions.map((act, idx) => (
          <div key={idx} className="flex items-start gap-3 text-sm text-text-secondary">
            <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-accent/20 text-xs font-bold text-accent">
              {idx + 1}
            </span>
            <p className="leading-snug">{act}</p>
          </div>
        ))}
      </div>

      {/* Action Navigation Buttons */}
      <div className="border-t border-border pt-6">
        <div className="text-xs font-semibold uppercase tracking-wider text-text-muted mb-3">
          Instant Navigation Actions
        </div>
        <div className="flex flex-wrap gap-3">
          {topCompanies.length > 0 && (
            <button
              onClick={() =>
                navigate(`/evidence?id=${analysisId}&entity=${encodeURIComponent(topCompanies[0])}`)
              }
              className="inline-flex items-center gap-2 rounded-xl border border-border bg-bg-secondary px-4 py-2.5 text-xs font-semibold text-text-primary hover:border-accent hover:text-accent transition"
            >
              <Building2 size={14} className="text-accent" />
              Explore Companies
            </button>
          )}

          <button
            onClick={() => navigate(`/evidence?id=${analysisId}`)}
            className="inline-flex items-center gap-2 rounded-xl border border-border bg-bg-secondary px-4 py-2.5 text-xs font-semibold text-text-primary hover:border-accent hover:text-accent transition"
          >
            <Briefcase size={14} className="text-accent" />
            View Jobs
          </button>

          <button
            onClick={() => navigate(`/evidence?id=${analysisId}`)}
            className="inline-flex items-center gap-2 rounded-xl border border-border bg-bg-secondary px-4 py-2.5 text-xs font-semibold text-text-primary hover:border-accent hover:text-accent transition"
          >
            <Layers size={14} className="text-accent" />
            View Evidence
          </button>

          <button
            onClick={() => navigate(`/compare?id=${analysisId}`)}
            className="inline-flex items-center gap-2 rounded-xl border border-border bg-bg-secondary px-4 py-2.5 text-xs font-semibold text-text-primary hover:border-accent hover:text-accent transition"
          >
            <GitCompare size={14} className="text-accent" />
            Compare Again
          </button>

          <button
            onClick={() => navigate('/')}
            className="inline-flex items-center gap-2 rounded-xl bg-accent px-4 py-2.5 text-xs font-bold text-white hover:bg-accent-hover transition ml-auto"
          >
            <RotateCcw size={14} />
            Start New Analysis
          </button>
        </div>
      </div>
    </div>
  );
}
