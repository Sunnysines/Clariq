import { Briefcase, Newspaper, Globe, TrendingUp, MapPin } from 'lucide-react';
import type { SourceType } from '../types';

interface SourceBadgeProps {
  sourceType: SourceType | string;
  sourceName?: string | null;
}

const CONFIG: Record<string, { icon: any; label: string; color: string }> = {
  job: { icon: Briefcase, label: 'Google Jobs', color: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30' },
  news: { icon: Newspaper, label: 'Google News', color: 'bg-blue-500/15 text-blue-400 border-blue-500/30' },
  web: { icon: Globe, label: 'Google Search', color: 'bg-purple-500/15 text-purple-400 border-purple-500/30' },
  trend: { icon: TrendingUp, label: 'Google Trends', color: 'bg-amber-500/15 text-amber-400 border-amber-500/30' },
  local: { icon: MapPin, label: 'Google Local', color: 'bg-rose-500/15 text-rose-400 border-rose-500/30' },
};

export default function SourceBadge({ sourceType, sourceName }: SourceBadgeProps) {
  const norm = sourceType.toLowerCase();
  const meta = CONFIG[norm] || CONFIG.web;
  const Icon = meta.icon;

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-[11px] font-semibold tracking-wide ${meta.color}`}
    >
      <Icon size={12} />
      <span>{sourceName || meta.label}</span>
    </span>
  );
}
