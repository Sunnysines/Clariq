import { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Loader2, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react';
import { useAnalysis } from '../hooks/useAnalysis';

const STAGES = [
  'understanding',
  'planning',
  'searching_jobs',
  'searching_web',
  'searching_news',
  'searching_trends',
  'normalizing',
  'resolving_entities',
  'analyzing_signals',
  'detecting_conflicts',
  'scoring',
  'explaining',
  'recommending',
];

const STAGE_LABELS: Record<string, string> = {
  understanding: 'Understanding your question',
  planning: 'Building search plan',
  searching_jobs: 'Searching Google Jobs',
  searching_web: 'Searching Google Search',
  searching_news: 'Searching Google News',
  searching_trends: 'Searching Google Trends',
  normalizing: 'Normalizing evidence',
  resolving_entities: 'Resolving entities',
  analyzing_signals: 'Analyzing signals',
  detecting_conflicts: 'Detecting conflicts',
  scoring: 'Calculating confidence',
  explaining: 'Generating explanations',
  recommending: 'Building recommendation',
};

function getStageStatus(stage: string, currentStage: string | null | undefined) {
  if (!currentStage) return 'pending';
  const ci = STAGES.indexOf(currentStage);
  const si = STAGES.indexOf(stage);
  if (si < ci) return 'done';
  if (si === ci) return 'active';
  return 'pending';
}

export default function AnalyzePage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const question = params.get('q') || '';
  const analysisId = params.get('id');
  const { analysis, loading, error, startAnalysis, loadAnalysis } = useAnalysis();

  useEffect(() => {
    if (analysisId) {
      loadAnalysis(analysisId);
    } else if (question) {
      startAnalysis(question).then((id) => {
        if (id) {
          const newParams = new URLSearchParams(params);
          newParams.set('id', id);
          navigate(`/analyze?${newParams.toString()}`, { replace: true });
        }
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Navigate to dashboard on completion
  useEffect(() => {
    if (analysis?.status === 'completed' || analysis?.status === 'partial') {
      const timer = setTimeout(() => {
        navigate(`/dashboard?id=${analysis.id}`);
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [analysis?.status, analysis?.id, navigate]);

  const stats = analysis?.result_data as Record<string, unknown> | null;

  return (
    <div className="flex min-h-[calc(100vh-60px)] items-center justify-center px-4">
      <div className="w-full max-w-2xl animate-fade-in-up">
        {/* Title */}
        <div className="mb-10 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-accent/10">
            {analysis?.status === 'completed' ? (
              <CheckCircle2 size={32} className="text-success" />
            ) : analysis?.status === 'failed' ? (
              <XCircle size={32} className="text-danger" />
            ) : (
              <Loader2 size={32} className="animate-spin-slow text-accent" />
            )}
          </div>
          <h1 className="mb-2 text-2xl font-bold text-text-primary">
            {analysis?.status === 'completed'
              ? 'ANALYSIS COMPLETE'
              : analysis?.status === 'failed'
              ? 'ANALYSIS FAILED'
              : 'CLARIQ IS INVESTIGATING'}
          </h1>
          {question && (
            <p className="text-sm text-text-secondary">"{question}"</p>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 rounded-xl border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger">
            <AlertTriangle size={16} className="mr-2 inline" />
            {error}
          </div>
        )}

        {/* Stage list */}
        {loading && (
          <div className="card mb-8 p-6">
            <div className="space-y-3">
              {STAGES.map((stage) => {
                const status = getStageStatus(stage, analysis?.current_stage);
                return (
                  <div key={stage} className="flex items-center gap-3">
                    {status === 'done' ? (
                      <CheckCircle2 size={18} className="text-success" />
                    ) : status === 'active' ? (
                      <Loader2 size={18} className="animate-spin text-accent" />
                    ) : (
                      <div className="h-[18px] w-[18px] rounded-full border border-border" />
                    )}
                    <span
                      className={`text-sm ${
                        status === 'done'
                          ? 'text-text-primary'
                          : status === 'active'
                          ? 'font-medium text-accent'
                          : 'text-text-muted'
                      }`}
                    >
                      {STAGE_LABELS[stage] || stage}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Live Stats */}
        {stats && (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
            {[
              { label: 'Evidence', value: (stats as Record<string, unknown>)?.total_evidence ?? '—' },
              { label: 'Searches', value: (stats as Record<string, unknown>)?.total_searches ?? '—' },
              { label: 'Entities', value: (stats as Record<string, unknown>)?.total_entities ?? '—' },
              { label: 'Signals', value: (stats as Record<string, unknown>)?.total_signals ?? '—' },
              { label: 'Conflicts', value: (stats as Record<string, unknown>)?.total_contradictions ?? '—' },
            ].map(({ label, value }) => (
              <div key={label} className="card p-4 text-center">
                <div className="text-2xl font-bold text-accent">{String(value)}</div>
                <div className="text-xs text-text-muted">{label}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
