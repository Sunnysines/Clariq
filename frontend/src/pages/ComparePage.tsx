import { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { GitCompare, ArrowRight, ShieldCheck, Trophy, Sparkles } from 'lucide-react';

interface CityComparison {
  name: string;
  total: number;
  jobs: number;
  demand: number;
  activity: number;
  ecosystem: number;
  confidence: number;
  level: string;
}

const DEFAULT_COMPARISON: CityComparison[] = [
  { name: 'Bengaluru', total: 89, jobs: 92, demand: 88, activity: 85, ecosystem: 94, confidence: 91, level: 'HIGH' },
  { name: 'Hyderabad', total: 82, jobs: 83, demand: 81, activity: 84, ecosystem: 80, confidence: 85, level: 'HIGH' },
  { name: 'Pune', total: 74, jobs: 72, demand: 75, activity: 71, ecosystem: 78, confidence: 78, level: 'MEDIUM' },
  { name: 'Chennai', total: 69, jobs: 66, demand: 70, activity: 68, ecosystem: 72, confidence: 73, level: 'MEDIUM' },
];

export default function ComparePage() {
  const [params] = useSearchParams();
  const id = params.get('id');
  const [data] = useState<CityComparison[]>(DEFAULT_COMPARISON);

  useEffect(() => {
    // When API data is hooked up, it can load dynamically from backend
  }, [id]);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      {/* Header */}
      <div className="mb-8 border-b border-border pb-6">
        <div className="flex items-center gap-2 mb-2">
          <span className="rounded bg-accent/20 px-2.5 py-0.5 text-xs font-semibold text-accent uppercase">
            Side-by-Side Comparison
          </span>
          {id && <span className="text-xs text-text-muted">Linked to Analysis: {id.slice(0, 8)}...</span>}
        </div>
        <h1 className="text-2xl font-bold md:text-3xl">Comparative Entity Intelligence</h1>
        <p className="mt-1 text-sm text-text-secondary">
          Normalized performance indices across key evidence dimensions with multi-source corroboration.
        </p>
      </div>

      {/* Comparison Grid Table */}
      <div className="card overflow-x-auto mb-8">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-border bg-bg-secondary/70 text-xs uppercase text-text-muted">
            <tr>
              <th className="p-4">Rank & Entity</th>
              <th className="p-4">Overall Score</th>
              <th className="p-4">Jobs (35%)</th>
              <th className="p-4">Demand (20%)</th>
              <th className="p-4">Activity (20%)</th>
              <th className="p-4">Ecosystem (15%)</th>
              <th className="p-4">Confidence</th>
              <th className="p-4 text-right">Evidence</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {data.map((c, idx) => (
              <tr key={c.name} className="hover:bg-bg-secondary/40 transition">
                <td className="p-4 font-semibold text-text-primary">
                  <div className="flex items-center gap-2">
                    {idx === 0 ? (
                      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-accent text-xs font-bold text-white">
                        <Trophy size={12} />
                      </span>
                    ) : (
                      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-bg-secondary text-xs text-text-muted">
                        #{idx + 1}
                      </span>
                    )}
                    <span>{c.name}</span>
                  </div>
                </td>
                <td className="p-4">
                  <span className="font-bold text-base text-accent">{c.total}</span>
                  <span className="text-xs text-text-muted"> / 100</span>
                </td>
                <td className="p-4 text-text-secondary">{c.jobs}%</td>
                <td className="p-4 text-text-secondary">{c.demand}%</td>
                <td className="p-4 text-text-secondary">{c.activity}%</td>
                <td className="p-4 text-text-secondary">{c.ecosystem}%</td>
                <td className="p-4">
                  <span className="inline-flex items-center gap-1 rounded bg-success/15 px-2 py-0.5 text-xs font-medium text-success">
                    <ShieldCheck size={12} />
                    {c.confidence}% ({c.level})
                  </span>
                </td>
                <td className="p-4 text-right">
                  <Link
                    to={`/evidence?entity=${encodeURIComponent(c.name)}${id ? `&id=${id}` : ''}`}
                    className="inline-flex items-center gap-1 text-xs text-accent hover:underline"
                  >
                    Inspect
                    <ArrowRight size={12} />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Visual Bars Breakdown */}
      <div className="grid gap-6 md:grid-cols-2">
        <div className="card p-6">
          <h3 className="mb-4 text-base font-bold flex items-center gap-2">
            <Sparkles size={16} className="text-accent" />
            Relative Score Distribution
          </h3>
          <div className="space-y-4">
            {data.map((item) => (
              <div key={item.name} className="space-y-1">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-text-primary">{item.name}</span>
                  <span className="text-accent font-bold">{item.total}/100</span>
                </div>
                <div className="h-2 w-full rounded-full bg-bg-secondary overflow-hidden">
                  <div
                    className="h-full rounded-full bg-accent"
                    style={{ width: `${item.total}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card p-6">
          <h3 className="mb-4 text-base font-bold flex items-center gap-2">
            <GitCompare size={16} className="text-accent" />
            Recommendation Summary
          </h3>
          <p className="text-sm text-text-secondary leading-relaxed mb-4">
            Bengaluru demonstrates the strongest current opportunity density with 92% in job openings and 94% in company presence, maintaining high evidence corroboration across SerpApi engines.
          </p>
          <div className="rounded-xl border border-border bg-bg-secondary p-4 text-xs text-text-muted">
            <p className="font-semibold text-text-secondary mb-1">Clariq Scoring Transparency</p>
            Evidence-weighted multi-engine aggregation prevents skew from solitary job boards or news spikes.
          </div>
        </div>
      </div>
    </div>
  );
}
