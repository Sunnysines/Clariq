import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';
import { TrendingUp, TrendingDown, Minus, Info } from 'lucide-react';
import type { EvidenceItem, TrendData } from '../types';

const PALETTE = ['#6366f1', '#22c55e', '#f59e0b', '#ec4899'];

interface TrendPanelProps {
  evidence: EvidenceItem[];
}

function DirectionBadge({ direction }: { direction: TrendData['trend_direction'] }) {
  if (direction === 'rising')
    return (
      <span className="inline-flex items-center gap-1 text-success">
        <TrendingUp size={12} aria-hidden /> Rising
      </span>
    );
  if (direction === 'falling')
    return (
      <span className="inline-flex items-center gap-1 text-danger">
        <TrendingDown size={12} aria-hidden /> Falling
      </span>
    );
  if (direction === 'stable')
    return (
      <span className="inline-flex items-center gap-1 text-text-secondary">
        <Minus size={12} aria-hidden /> Stable
      </span>
    );
  return <span className="text-text-muted">Insufficient data</span>;
}

export default function TrendPanel({ evidence }: TrendPanelProps) {
  const trends = evidence
    .filter((e) => e.source_type === 'trend' && e.trend_data && e.trend_data.timeline_data?.length)
    .map((e) => e.trend_data as TrendData)
    // de-duplicate by query
    .filter((t, i, arr) => arr.findIndex((x) => x.query === t.query) === i)
    .slice(0, 4);

  if (trends.length === 0) return null;

  // Merge timelines on index so multiple terms share one x-axis
  const maxLen = Math.max(...trends.map((t) => t.timeline_data.length));
  const base = trends.reduce((a, b) => (a.timeline_data.length >= b.timeline_data.length ? a : b));
  const chartData = Array.from({ length: maxLen }, (_, i) => {
    const row: Record<string, string | number> = { date: base.timeline_data[i]?.date ?? `${i + 1}` };
    trends.forEach((t) => {
      const pt = t.timeline_data[i];
      if (pt) row[t.query] = pt.value;
    });
    return row;
  });

  const geo = trends[0].geo;
  const range = trends[0].time_range;

  return (
    <section className="card p-6" aria-labelledby="trend-panel-title">
      <div className="mb-1 flex flex-wrap items-center gap-2">
        <h3 id="trend-panel-title" className="text-base font-bold text-text-primary">
          Search Momentum
        </h3>
        <span className="rounded-md bg-accent/15 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-accent">
          Search Interest
        </span>
      </div>
      <p className="mb-4 text-xs text-text-secondary">
        Google Trends · {geo} · {range}
      </p>

      <div className="h-56 w-full" role="img" aria-label={`Search interest over time for ${trends.map((t) => t.query).join(', ')}`}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              {trends.map((t, i) => (
                <linearGradient key={t.query} id={`trendFill${i}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={PALETTE[i % PALETTE.length]} stopOpacity={0.45} />
                  <stop offset="100%" stopColor={PALETTE[i % PALETTE.length]} stopOpacity={0} />
                </linearGradient>
              ))}
            </defs>
            <CartesianGrid strokeDasharray="3 6" stroke="#26263f" vertical={false} />
            <XAxis dataKey="date" stroke="#70708c" fontSize={10} minTickGap={50} tickLine={false} axisLine={false} />
            <YAxis domain={[0, 100]} stroke="#70708c" fontSize={11} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={{ backgroundColor: '#13131f', borderColor: '#6d6ff5', borderRadius: 12, fontSize: 12 }} />
            {trends.length > 1 && <Legend wrapperStyle={{ fontSize: 11 }} />}
            {trends.map((t, i) => (
              <Area
                key={t.query}
                type="monotone"
                dataKey={t.query}
                stroke={PALETTE[i % PALETTE.length]}
                strokeWidth={2.5}
                fill={`url(#trendFill${i})`}
                dot={false}
              />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 grid gap-2 sm:grid-cols-2">
        {trends.map((t, i) => (
          <div key={t.query} className="flex items-center justify-between rounded-lg border border-border px-3 py-2 text-xs">
            <span className="flex items-center gap-2 font-medium text-text-primary">
              <span className="h-2 w-2 rounded-full" style={{ backgroundColor: PALETTE[i % PALETTE.length] }} />
              {t.query}
            </span>
            <span className="flex items-center gap-3 text-text-secondary">
              avg {t.average_interest ?? '—'}/100
              <DirectionBadge direction={t.trend_direction} />
            </span>
          </div>
        ))}
      </div>

      <p className="mt-4 flex items-start gap-2 text-[11px] leading-relaxed text-text-muted">
        <Info size={12} className="mt-0.5 shrink-0" aria-hidden />
        Search interest measures relative public attention, not job availability or hiring demand. It is one signal among multiple evidence channels.
      </p>
    </section>
  );
}
