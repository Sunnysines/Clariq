import { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { 
  Loader2, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Info,
  Layers,
  Search,
  Users,
  Radio,
  Flame
} from 'lucide-react';
import { useAnalysis } from '../hooks/useAnalysis';

const STAGES = [
  'understanding',
  'planning',
  'searching_jobs',
  'searching_web',
  'searching_news',
  'searching_trends',
  'resolving_entities',
  'detecting_conflicts',
  'calculating_confidence',
];

const STAGE_LABELS: Record<string, string> = {
  understanding: 'Understanding your question',
  planning: 'Building search plan',
  searching_jobs: 'Searching Google Jobs',
  searching_web: 'Searching Google Search',
  searching_news: 'Searching Google News',
  searching_trends: 'Searching Google Trends',
  resolving_entities: 'Resolving entities',
  detecting_conflicts: 'Detecting conflicts',
  calculating_confidence: 'Calculating confidence',
};

function getStageStatus(stage: string, currentStage: string | null | undefined) {
  if (!currentStage) return 'pending';
  if (currentStage === 'completed') return 'done';
  const ci = STAGES.indexOf(currentStage);
  const si = STAGES.indexOf(stage);
  if (ci === -1) return 'done';
  if (si < ci) return 'done';
  if (si === ci) return 'active';
  return 'pending';
}

export default function AnalyzePage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const question = params.get('q') || '';
  const analysisId = params.get('id');
  const { analysis, error, startAnalysis, loadAnalysis } = useAnalysis();

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

  const resultData = analysis?.result_data as any;
  const stats = resultData?.statistics;

  // Check if any engine reported partial failure
  const engineWarning = resultData?.engine_warning;

  return (
    <div className="flex min-h-[calc(100vh-60px)] items-center justify-center px-4 py-12">
      <div className="w-full max-w-2xl animate-fade-in-up">
        {/* Title */}
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-accent/15 border border-accent/30 shadow-lg shadow-accent/10">
            {analysis?.status === 'completed' ? (
              <CheckCircle2 size={32} className="text-success" />
            ) : analysis?.status === 'failed' ? (
              <XCircle size={32} className="text-danger" />
            ) : (
              <Loader2 size={32} className="animate-spin-slow text-accent" />
            )}
          </div>
          <h1 className="mb-2 text-3xl font-extrabold tracking-tight text-text-primary">
            {analysis?.status === 'completed'
              ? 'ANALYSIS COMPLETE'
              : analysis?.status === 'failed'
              ? 'ANALYSIS FAILED'
              : 'CLARIQ IS INVESTIGATING'}
          </h1>
          {question && (
            <p className="mx-auto max-w-xl text-sm text-text-secondary leading-relaxed">
              "{question}"
            </p>
          )}
        </div>

        {/* Engine Warning Banner if an engine was unavailable */}
        {engineWarning && (
          <div className="mb-6 flex items-center gap-3 rounded-xl border border-warning/30 bg-warning/10 p-4 text-xs text-warning">
            <Info size={16} className="shrink-0" />
            <span>{engineWarning}</span>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mb-6 rounded-xl border border-danger/30 bg-danger/10 p-4 text-sm text-danger flex items-center gap-3">
            <AlertTriangle size={18} className="shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Stage List */}
        <div className="card mb-6 p-6">
          <div className="mb-4 flex items-center justify-between border-b border-border pb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-text-muted">
              Live Investigation Pipeline
            </span>
            <span className="text-xs font-mono text-accent">
              {analysis?.status === 'completed' ? '100% Verified' : 'Executing...'}
            </span>
          </div>

          <div className="space-y-3.5">
            {STAGES.map((stage) => {
              const status = getStageStatus(stage, analysis?.current_stage);
              return (
                <div key={stage} className="flex items-center justify-between transition-colors">
                  <div className="flex items-center gap-3">
                    {status === 'done' ? (
                      <CheckCircle2 size={18} className="text-success" />
                    ) : status === 'active' ? (
                      <Loader2 size={18} className="animate-spin text-accent" />
                    ) : (
                      <div className="h-[18px] w-[18px] rounded-full border border-border bg-bg-secondary/50" />
                    )}
                    <span
                      className={`text-sm ${
                        status === 'done'
                          ? 'text-text-primary font-medium'
                          : status === 'active'
                          ? 'font-semibold text-accent'
                          : 'text-text-muted'
                      }`}
                    >
                      {STAGE_LABELS[stage]}
                    </span>
                  </div>

                  {status === 'active' && (
                    <span className="rounded bg-accent/15 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-accent animate-pulse">
                      In Progress
                    </span>
                  )}
                  {status === 'done' && (
                    <span className="text-xs text-success">✓ Verified</span>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Live Statistics Cards */}
        {stats && (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
            <div className="card p-4 text-center">
              <Layers size={16} className="mx-auto mb-1 text-accent" />
              <div className="text-2xl font-black text-text-primary">{stats.total_evidence ?? 0}</div>
              <div className="text-[11px] text-text-muted">Evidence Items</div>
            </div>
            <div className="card p-4 text-center">
              <Search size={16} className="mx-auto mb-1 text-accent" />
              <div className="text-2xl font-black text-text-primary">{stats.total_searches ?? 0}</div>
              <div className="text-[11px] text-text-muted">Searches Executed</div>
            </div>
            <div className="card p-4 text-center">
              <Users size={16} className="mx-auto mb-1 text-accent" />
              <div className="text-2xl font-black text-text-primary">{stats.total_entities ?? 0}</div>
              <div className="text-[11px] text-text-muted">Entities Detected</div>
            </div>
            <div className="card p-4 text-center">
              <Radio size={16} className="mx-auto mb-1 text-accent" />
              <div className="text-2xl font-black text-text-primary">{stats.total_signals ?? 0}</div>
              <div className="text-[11px] text-text-muted">Signals Detected</div>
            </div>
            <div className="card p-4 text-center">
              <Flame size={16} className="mx-auto mb-1 text-warning" />
              <div className="text-2xl font-black text-text-primary">{stats.total_contradictions ?? 0}</div>
              <div className="text-[11px] text-text-muted">Conflicts Analyzed</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
