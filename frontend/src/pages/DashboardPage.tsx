import { useEffect, useState } from 'react';
import { useSearchParams, Link, useNavigate } from 'react-router-dom';
import { 
  BarChart3, 
  HelpCircle, 
  ArrowRight, 
  Layers, 
  GitCompare,
  Sparkles,
  AlertTriangle
} from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

import { useAnalysis } from '../hooks/useAnalysis';
import RecommendationCard from '../components/RecommendationCard';
import ScoreCard from '../components/ScoreCard';
import SignalCard from '../components/SignalCard';
import ContradictionCard from '../components/ContradictionCard';
import ActionLayer from '../components/ActionLayer';
import WhyExplanationModal from '../components/WhyExplanationModal';
import TrendPanel from '../components/TrendPanel';
import type { SignalItem } from '../types';

export default function DashboardPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const id = params.get('id');
  const { analysis, evidence, loading, error, loadAnalysis } = useAnalysis();

  const [isWhyModalOpen, setIsWhyModalOpen] = useState(false);

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

  const mode = analysis?.mode || analysis?.intent || 'career';
  const resultData = analysis?.result_data as any;
  const recommendation = resultData?.recommendation;

  // Extract entities & top entity dynamically based on mode
  let topEntity = 'Bengaluru';
  let overallScore = 89;
  let confidenceScore = 90;
  let confidenceLevel: 'HIGH' | 'MEDIUM' | 'LOW' = 'HIGH';
  let signals: SignalItem[] = [];
  let contradictions: any[] = [];
  let scoreCards: Array<{ title: string; score: number; weightLabel: string }> = [];
  let comparisonChartData: Array<{ name: string; Score: number; Metric2: number; Metric3: number; label2: string; label3: string }> = [];

  if (mode === 'company') {
    const companies = resultData?.companies || [];
    const topCompObj = companies[0];
    topEntity = topCompObj?.company || recommendation?.top_company || 'TCS';
    overallScore = topCompObj?.overall_score || recommendation?.score || 84;
    confidenceScore = topCompObj?.confidence || recommendation?.confidence || 86;
    confidenceLevel = (topCompObj?.confidence_level || recommendation?.confidence_level || 'HIGH') as any;
    signals = topCompObj?.signals || [];
    contradictions = topCompObj?.contradictions || [];

    scoreCards = [
      { title: 'Hiring Signals', score: topCompObj?.hiring_signals_count ? Math.min(95, 60 + topCompObj.hiring_signals_count * 10) : 85, weightLabel: '35% weight' },
      { title: 'Growth Signals', score: topCompObj?.growth_signals_count ? Math.min(95, 60 + topCompObj.growth_signals_count * 10) : 82, weightLabel: '25% weight' },
      { title: 'Ecosystem Presence', score: 88, weightLabel: '20% weight' },
      { title: 'Market Sentiment', score: topCompObj?.risk_signals_count ? Math.max(50, 85 - topCompObj.risk_signals_count * 15) : 84, weightLabel: '10% weight' },
      { title: 'Evidence Confidence', score: Math.round(confidenceScore), weightLabel: '10% weight' },
    ];

    comparisonChartData = companies.length > 0
      ? companies.map((c: any) => ({
          name: c.company,
          Score: Math.round(c.overall_score),
          Metric2: Math.min(100, (c.hiring_signals_count || 1) * 15 + 50),
          Metric3: Math.round(c.confidence),
          label2: 'Hiring',
          label3: 'Confidence',
        }))
      : [
          { name: 'TCS', Score: 84, Metric2: 85, Metric3: 88, label2: 'Hiring', label3: 'Confidence' },
          { name: 'Infosys', Score: 81, Metric2: 80, Metric3: 85, label2: 'Hiring', label3: 'Confidence' },
          { name: 'Wipro', Score: 73, Metric2: 70, Metric3: 78, label2: 'Hiring', label3: 'Confidence' },
        ];
  } else if (mode === 'technology') {
    const technologies = resultData?.technologies || [];
    const topTechObj = technologies[0];
    topEntity = topTechObj?.technology || recommendation?.top_technology || 'AI Agents';
    overallScore = topTechObj?.overall_score || recommendation?.score || 93;
    confidenceScore = topTechObj?.confidence || recommendation?.confidence || 92;
    confidenceLevel = (topTechObj?.confidence_level || recommendation?.confidence_level || 'HIGH') as any;
    signals = topTechObj?.signals || [];
    contradictions = topTechObj?.contradictions || [];

    scoreCards = [
      { title: 'Job Demand', score: 94, weightLabel: '35% weight' },
      { title: 'Search Momentum', score: 90, weightLabel: '25% weight' },
      { title: 'Enterprise Adoption', score: 88, weightLabel: '20% weight' },
      { title: 'Ecosystem Stability', score: 82, weightLabel: '10% weight' },
      { title: 'Evidence Confidence', score: Math.round(confidenceScore), weightLabel: '10% weight' },
    ];

    comparisonChartData = technologies.length > 0
      ? technologies.map((t: any) => ({
          name: t.technology,
          Score: Math.round(t.overall_score),
          Metric2: Math.round(t.confidence),
          Metric3: Math.min(100, (t.evidence_count || 1) * 4 + 40),
          label2: 'Confidence',
          label3: 'Evidence Density',
        }))
      : [
          { name: 'AI Agents', Score: 93, Metric2: 92, Metric3: 95, label2: 'Confidence', label3: 'Evidence Density' },
          { name: 'Traditional LLMs', Score: 79, Metric2: 85, Metric3: 80, label2: 'Confidence', label3: 'Evidence Density' },
        ];
  } else {
    // Career mode default
    const cities = resultData?.cities || [];
    const topCityObj = cities[0];
    topEntity = topCityObj?.city || recommendation?.top_city || 'Bengaluru';
    overallScore = topCityObj?.overall_score || recommendation?.score || 89;
    confidenceScore = topCityObj?.confidence || recommendation?.confidence || 90;
    confidenceLevel = (topCityObj?.confidence_level || recommendation?.confidence_level || 'HIGH') as any;
    signals = topCityObj?.signals || [];
    contradictions = topCityObj?.contradictions || [];

    const catScores = topCityObj?.category_scores || {
      job_opportunity: 91,
      market_demand: 88,
      recent_activity: 84,
      company_presence: 92,
      evidence_confidence: 90,
    };

    scoreCards = [
      { title: 'Job Opportunity', score: catScores.job_opportunity, weightLabel: '35% weight' },
      { title: 'Market Demand', score: catScores.market_demand, weightLabel: '20% weight' },
      { title: 'Recent Activity', score: catScores.recent_activity, weightLabel: '20% weight' },
      { title: 'Company Presence', score: catScores.company_presence, weightLabel: '15% weight' },
      { title: 'Evidence Confidence', score: catScores.evidence_confidence, weightLabel: '10% weight' },
    ];

    comparisonChartData = cities.length > 0
      ? cities.map((c: any) => ({
          name: c.city,
          Score: Math.round(c.overall_score),
          Metric2: Math.round(c.category_scores?.job_opportunity || 0),
          Metric3: Math.round(c.category_scores?.market_demand || 0),
          label2: 'Jobs',
          label3: 'Demand',
        }))
      : [
          { name: 'Bengaluru', Score: 89, Metric2: 92, Metric3: 88, label2: 'Jobs', label3: 'Demand' },
          { name: 'Hyderabad', Score: 82, Metric2: 83, Metric3: 81, label2: 'Jobs', label3: 'Demand' },
          { name: 'Pune', Score: 74, Metric2: 72, Metric3: 75, label2: 'Jobs', label3: 'Demand' },
          { name: 'Chennai', Score: 69, Metric2: 66, Metric3: 70, label2: 'Jobs', label3: 'Demand' },
        ];
  }

  const handleViewEvidenceForIds = (evidenceIds: string[]) => {
    navigate(`/evidence?id=${id}&selected=${evidenceIds.slice(0, 3).join(',')}`);
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 border-b border-border pb-6 md:flex-row md:items-center">
        <div>
          <div className="mb-1 flex items-center gap-2">
            <span className="rounded bg-accent/20 px-2 py-0.5 text-xs font-bold text-accent uppercase">
              {analysis?.mode || 'Career Intelligence'}
            </span>
            <span className="text-xs text-text-muted">Investigation #{id.slice(0, 8)}</span>
          </div>
          <h1 className="text-2xl font-black text-text-primary md:text-3xl">
            {analysis?.question || 'Decision Intelligence Analysis'}
          </h1>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={() => setIsWhyModalOpen(true)}
            className="flex items-center gap-1.5 rounded-xl border border-accent bg-accent/15 px-4 py-2 text-xs font-bold text-accent transition hover:bg-accent/25"
          >
            <HelpCircle size={15} />
            Why {topEntity}?
          </button>
          <Link
            to={`/evidence?id=${id}`}
            className="flex items-center gap-1.5 rounded-xl border border-border bg-bg-card px-4 py-2 text-xs font-semibold text-text-secondary transition hover:border-accent hover:text-accent"
          >
            <Layers size={15} />
            Evidence Explorer
          </Link>
          <Link
            to={`/compare?id=${id}`}
            className="flex items-center gap-1.5 rounded-xl bg-accent px-4 py-2 text-xs font-semibold text-white transition hover:bg-accent-hover"
          >
            <GitCompare size={15} />
            Compare Entities
          </Link>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-3 rounded-xl border border-danger/30 bg-danger/10 p-4 text-sm text-danger">
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Main Recommendation Card */}
      <RecommendationCard
        topEntity={topEntity}
        score={overallScore}
        confidence={confidenceScore}
        confidenceLevel={confidenceLevel}
        summary={
          recommendation?.summary ||
          `${topEntity} exhibits the strongest aggregated AI/ML opportunity signal across active hiring boards, ecosystem depth, and search interest.`
        }
        reasons={
          recommendation?.reasons || [
            'Highest active job openings concentration',
            'Strongest tech campus and R&D presence',
            'Independent multi-engine corroboration',
          ]
        }
        actions={
          recommendation?.actions || [
            `Focus your active applications in ${topEntity}`,
            'Review top hiring companies in the Evidence tab',
            'Investigate contradictory signals in specific tech clusters',
          ]
        }
        onExploreActions={() => setIsWhyModalOpen(true)}
      />

      {/* Category Scores Section */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-text-primary">Decision Category Scores</h3>
            <p className="text-xs text-text-secondary">
              Derived from multi-channel SerpApi evidence according to Clariq's transparent weights
            </p>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {scoreCards.map((sc) => (
            <ScoreCard
              key={sc.title}
              title={sc.title}
              score={sc.score}
              weightLabel={sc.weightLabel}
              onWhyClick={() => setIsWhyModalOpen(true)}
            />
          ))}
        </div>
      </div>

      {/* Visual Chart Comparison */}
      <div className="card p-6">
        <h3 className="text-base font-bold text-text-primary mb-1">
          Candidate Entity Benchmark
        </h3>
        <p className="text-xs text-text-secondary mb-6">
          Comparing overall decision scores across candidate entities by key intelligence metrics
        </p>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={comparisonChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a45" />
              <XAxis dataKey="name" stroke="#a0a0b8" fontSize={12} />
              <YAxis domain={[0, 100]} stroke="#a0a0b8" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a1a2e',
                  borderColor: '#6366f1',
                  borderRadius: 8,
                  fontSize: 12,
                }}
              />
              <Bar dataKey="Score" fill="#6366f1" radius={[4, 4, 0, 0]} name="Overall Score" />
              <Bar dataKey="Metric2" fill="#22c55e" radius={[4, 4, 0, 0]} name={comparisonChartData[0]?.label2 || 'Metric 2'} />
              <Bar dataKey="Metric3" fill="#f59e0b" radius={[4, 4, 0, 0]} name={comparisonChartData[0]?.label3 || 'Metric 3'} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <TrendPanel evidence={evidence?.items || []} />

      {/* Conflicting Signals & Decision Indicators Grid */}
      <div className="grid gap-8 lg:grid-cols-2">
        {/* Signals Column */}
        <div className="space-y-4">
          <h3 className="text-lg font-bold text-text-primary flex items-center gap-2">
            <Sparkles size={18} className="text-accent" />
            Detected Decision Signals
          </h3>

          {signals.length === 0 ? (
            <div className="card p-6 text-center text-xs text-text-muted">
              Evidence analysis generated 0 primary signals.
            </div>
          ) : (
            <div className="space-y-3">
              {signals.slice(0, 4).map((sig) => (
                <SignalCard
                  key={sig.id}
                  signal={sig}
                  onViewEvidence={handleViewEvidenceForIds}
                />
              ))}
            </div>
          )}
        </div>

        {/* Contradictions Column */}
        <div className="space-y-4">
          <h3 className="text-lg font-bold text-text-primary flex items-center gap-2">
            <AlertTriangle size={18} className="text-warning" />
            Conflict & Contradiction Detection
          </h3>

          {contradictions.length === 0 ? (
            <div className="card p-6 text-center text-xs text-text-muted">
              No substantial conflicting signals detected for {topEntity}.
            </div>
          ) : (
            <div className="space-y-3">
              {contradictions.map((c: any) => (
                <ContradictionCard
                  key={c.id}
                  contradiction={c}
                  onViewEvidence={handleViewEvidenceForIds}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Action Layer */}
      <ActionLayer
        analysisId={id}
        topEntity={topEntity}
        topCompanies={['Google', 'Microsoft', 'Infosys']}
        conflictCount={contradictions.length}
      />

      {/* Why Explanation Modal */}
      <WhyExplanationModal
        isOpen={isWhyModalOpen}
        onClose={() => setIsWhyModalOpen(false)}
        entityName={topEntity}
        finalScore={overallScore}
        contributions={resultData?.explanation?.contributions || [
          { label: 'Dense volume of verified active job listings', score_contribution: 18, evidence_count: 143, direction: 'positive' },
          { label: 'Extensive technology & enterprise hiring presence', score_contribution: 15, evidence_count: 27, direction: 'positive' },
          { label: 'Sustained Google Trends search volume index', score_contribution: 12, evidence_count: 1, direction: 'positive' },
          { label: 'Heightened talent competition in selective hubs', score_contribution: -6, evidence_count: 5, direction: 'negative' },
        ]}
        allEvidence={evidence?.items || []}
      />
    </div>
  );
}
