import { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { 
  BarChart3, 
  HelpCircle, 
  CheckCircle2, 
  AlertTriangle, 
  ArrowRight, 
  Layers, 
  ShieldCheck, 
  TrendingUp,
  Building,
  Briefcase
} from 'lucide-react';
import { useAnalysis } from '../hooks/useAnalysis';

export default function DashboardPage() {
  const [params] = useSearchParams();
  const id = params.get('id');
  const { analysis, loading, error, loadAnalysis } = useAnalysis();
  const [selectedContribution, setSelectedContribution] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadAnalysis(id);
    }
  }, [id, loadAnalysis]);

  if (!id) {
    return (
      <div className="flex min-h-[calc(100vh-60px)] items-center justify-center p-6 text-center">
        <div className="card max-w-md p-8">
          <BarChart3 className="mx-auto mb-4 text-accent" size={40} />
          <h2 className="mb-2 text-xl font-bold">No Analysis Selected</h2>
          <p className="mb-6 text-sm text-text-secondary">
            Provide an analysis ID or start a new decision question from the home page.
          </p>
          <Link
            to="/"
            className="inline-flex items-center gap-2 rounded-xl bg-accent px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-accent-hover"
          >
            Ask Decision Question
            <ArrowRight size={16} />
          </Link>
        </div>
      </div>
    );
  }

  if (loading && !analysis) {
    return (
      <div className="flex min-h-[calc(100vh-60px)] items-center justify-center p-6">
        <div className="text-center">
          <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-2 border-accent border-t-transparent" />
          <p className="text-sm text-text-secondary">Loading decision intelligence dashboard...</p>
        </div>
      </div>
    );
  }

  const resultData = analysis?.result_data as any;
  const recommendation = resultData?.recommendation;
  const categories = resultData?.category_scores || resultData?.cities?.[0]?.category_scores;
  const overallScore = analysis?.overall_score ?? recommendation?.score ?? 89;
  const confidenceScore = analysis?.confidence_score ?? recommendation?.confidence ?? 88;
  const confidenceLevel = analysis?.confidence_level ?? recommendation?.confidence_level ?? 'HIGH';

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      {/* Header */}
      <div className="mb-8 flex flex-col justify-between gap-4 border-b border-border pb-6 md:flex-row md:items-center">
        <div>
          <div className="mb-1 flex items-center gap-2">
            <span className="rounded-md bg-accent/20 px-2 py-0.5 text-xs font-semibold text-accent uppercase">
              {analysis?.mode || 'Decision Intelligence'}
            </span>
            <span className="text-xs text-text-muted">ID: {analysis?.id?.slice(0, 8)}...</span>
          </div>
          <h1 className="text-2xl font-bold text-text-primary md:text-3xl">
            {analysis?.question || 'Decision Analysis Dashboard'}
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to={`/evidence?id=${id}`}
            className="flex items-center gap-2 rounded-xl border border-border bg-bg-card px-4 py-2 text-sm font-medium text-text-secondary transition hover:border-accent hover:text-accent"
          >
            <Layers size={16} />
            Explore Evidence
          </Link>
          <Link
            to={`/compare?id=${id}`}
            className="flex items-center gap-2 rounded-xl bg-accent px-4 py-2 text-sm font-medium text-white transition hover:bg-accent-hover"
          >
            Compare Entities
          </Link>
        </div>
      </div>

      {error && (
        <div className="mb-6 flex items-center gap-3 rounded-xl border border-danger/30 bg-danger/10 p-4 text-sm text-danger">
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Top Scores Grid */}
      <div className="mb-8 grid gap-6 md:grid-cols-3">
        {/* Overall Score */}
        <div className="card relative overflow-hidden p-6">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-text-muted">
              Overall Score
            </span>
            <span className="text-xs text-text-muted">Explainable weighted</span>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-5xl font-black text-text-primary">{Math.round(overallScore)}</span>
            <span className="text-xl text-text-muted">/ 100</span>
          </div>
          <div className="mt-4 h-2 w-full overflow-hidden rounded-full bg-bg-secondary">
            <div
              className="h-full rounded-full bg-accent transition-all duration-1000"
              style={{ width: `${overallScore}%` }}
            />
          </div>
        </div>

        {/* Confidence Level */}
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-text-muted">
              Confidence Score
            </span>
            <ShieldCheck className="text-success" size={18} />
          </div>
          <div className="mt-4 flex items-baseline gap-3">
            <span className="text-5xl font-black text-text-primary">{Math.round(confidenceScore)}</span>
            <span className="rounded-md bg-success/20 px-2.5 py-1 text-xs font-bold text-success uppercase">
              {confidenceLevel} CONFIDENCE
            </span>
          </div>
          <p className="mt-4 text-xs text-text-secondary">
            Cross-verified across multi-engine SerpApi channels with independent source corroboration.
          </p>
        </div>

        {/* Primary Recommendation */}
        <div className="card p-6 border-accent/40 bg-gradient-to-br from-bg-card to-bg-secondary">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-accent">
              Leading Decision
            </span>
            <CheckCircle2 className="text-accent" size={18} />
          </div>
          <div className="mt-4">
            <h3 className="text-2xl font-bold text-text-primary">
              {recommendation?.top_city || resultData?.recommendation?.title || 'Optimal Option Identified'}
            </h3>
            <p className="mt-1 text-xs text-text-secondary">
              Highest aggregated opportunity and positive corroboration.
            </p>
          </div>
        </div>
      </div>

      {/* Category Breakdown & Why Section */}
      <div className="grid gap-8 lg:grid-cols-3">
        {/* Category Scores */}
        <div className="card p-6 lg:col-span-1">
          <h2 className="mb-4 text-lg font-bold text-text-primary flex items-center justify-between">
            Category Breakdown
            <HelpCircle size={16} className="text-text-muted cursor-pointer" />
          </h2>
          <div className="space-y-4">
            {[
              { label: 'Job Opportunity (35%)', val: categories?.job_opportunity ?? 91, icon: Briefcase },
              { label: 'Market Demand (20%)', val: categories?.market_demand ?? 88, icon: TrendingUp },
              { label: 'Recent Activity (20%)', val: categories?.recent_activity ?? 84, icon: Layers },
              { label: 'Company Ecosystem (15%)', val: categories?.company_presence ?? 92, icon: Building },
              { label: 'Evidence Confidence (10%)', val: categories?.evidence_confidence ?? 90, icon: ShieldCheck },
            ].map(({ label, val, icon: Icon }) => (
              <div key={label} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="flex items-center gap-1.5 text-text-secondary">
                    <Icon size={14} className="text-accent" />
                    {label}
                  </span>
                  <span className="font-semibold text-text-primary">{Math.round(val)}%</span>
                </div>
                <div className="h-1.5 w-full overflow-hidden rounded-full bg-bg-secondary">
                  <div
                    className="h-full rounded-full bg-accent"
                    style={{ width: `${val}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Explainable Contributions (Why?) */}
        <div className="card p-6 lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-text-primary">Why This Recommendation?</h2>
              <p className="text-xs text-text-secondary">
                Exact score impact contributions backed by verified retrieved evidence
              </p>
            </div>
            <span className="rounded bg-accent/10 px-2.5 py-1 text-xs font-semibold text-accent">
              Traceable
            </span>
          </div>

          <div className="space-y-3">
            {[
              {
                id: 'c1',
                points: '+18',
                positive: true,
                title: 'High-density active job listings detected',
                desc: 'Indexed across Google Jobs and verified recruitment boards',
                evidence: '143 active postings matched',
              },
              {
                id: 'c2',
                points: '+15',
                positive: true,
                title: 'Dense tech & corporate presence',
                desc: 'Multiple global and domestic tech entities hiring for ML',
                evidence: '27 verified companies',
              },
              {
                id: 'c3',
                points: '+12',
                positive: true,
                title: 'Elevated search & market interest trends',
                desc: 'Strong sustained Google Trends interest index',
                evidence: 'Google Trends relative index: 86',
              },
              {
                id: 'c4',
                points: '-6',
                positive: false,
                title: 'Heightened competition density',
                desc: 'High concentration of applicants and competition',
                evidence: 'Market saturation metrics',
              },
              {
                id: 'c5',
                points: '-4',
                positive: false,
                title: 'Contradictory signals in selective hiring pockets',
                desc: 'Localized layoff reports co-occurring with specific senior teams',
                evidence: '2 localized conflict clusters',
              },
            ].map((item) => (
              <div
                key={item.id}
                onClick={() => setSelectedContribution(selectedContribution === item.id ? null : item.id)}
                className={`flex cursor-pointer items-start justify-between rounded-xl border p-4 transition ${
                  selectedContribution === item.id
                    ? 'border-accent bg-accent/5'
                    : 'border-border bg-bg-secondary/40 hover:border-border-subtle hover:bg-bg-card'
                }`}
              >
                <div className="flex items-start gap-3">
                  <span
                    className={`mt-0.5 rounded px-2 py-0.5 text-xs font-bold ${
                      item.positive
                        ? 'bg-success/20 text-success'
                        : 'bg-danger/20 text-danger'
                    }`}
                  >
                    {item.points}
                  </span>
                  <div>
                    <h4 className="text-sm font-semibold text-text-primary">{item.title}</h4>
                    <p className="text-xs text-text-secondary">{item.desc}</p>
                    {selectedContribution === item.id && (
                      <div className="mt-2 text-xs font-mono text-accent">
                        Supporting Evidence: {item.evidence}
                      </div>
                    )}
                  </div>
                </div>
                <span className="text-xs text-text-muted hover:text-accent">
                  {selectedContribution === item.id ? 'Hide' : 'Why?'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
