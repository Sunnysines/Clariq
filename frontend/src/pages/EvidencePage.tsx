import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { 
  FileSearch, 
  ExternalLink, 
  Search as SearchIcon, 
  Briefcase, 
  Newspaper, 
  Globe, 
  TrendingUp, 
  MapPin 
} from 'lucide-react';
import type { EvidenceItem, SourceType } from '../types';
import * as api from '../services/api';

const SOURCE_ICONS: Record<SourceType, any> = {
  job: Briefcase,
  news: Newspaper,
  web: Globe,
  trend: TrendingUp,
  local: MapPin,
};

export default function EvidencePage() {
  const [params] = useSearchParams();
  const id = params.get('id');
  const entityFilter = params.get('entity');

  const [activeTab, setActiveTab] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [items, setItems] = useState<EvidenceItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (id) {
      setLoading(true);
      api.getEvidence(id)
        .then((res) => setItems(res.items || []))
        .catch(() => setItems([]))
        .finally(() => setLoading(false));
    }
  }, [id]);

  const filteredItems = items.filter((item) => {
    if (activeTab !== 'ALL' && item.source_type.toUpperCase() !== activeTab) {
      return false;
    }
    if (entityFilter && item.entity && !item.entity.toLowerCase().includes(entityFilter.toLowerCase())) {
      return false;
    }
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const titleMatch = item.title?.toLowerCase().includes(q);
      const snippetMatch = item.snippet?.toLowerCase().includes(q);
      const sourceMatch = item.source?.toLowerCase().includes(q);
      return titleMatch || snippetMatch || sourceMatch;
    }
    return true;
  });

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      {/* Header */}
      <div className="mb-8 border-b border-border pb-6">
        <div className="flex items-center gap-2 mb-2">
          <span className="rounded bg-accent/20 px-2.5 py-0.5 text-xs font-semibold text-accent uppercase">
            Evidence Explorer
          </span>
          {entityFilter && (
            <span className="rounded bg-bg-secondary border border-border px-2 py-0.5 text-xs text-text-secondary">
              Entity: {entityFilter}
            </span>
          )}
        </div>
        <h1 className="text-2xl font-bold md:text-3xl">Retrieved Evidence Records</h1>
        <p className="mt-1 text-sm text-text-secondary">
          Raw and normalized signals collected directly through SerpApi engines with traceable citations.
        </p>
      </div>

      {/* Controls: Search & Tabs */}
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        {/* Source Tabs */}
        <div className="flex flex-wrap gap-2">
          {['ALL', 'JOB', 'NEWS', 'WEB', 'TREND', 'LOCAL'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                activeTab === tab
                  ? 'bg-accent text-white'
                  : 'border border-border bg-bg-card text-text-secondary hover:text-text-primary'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="relative min-w-[260px]">
          <SearchIcon size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search within evidence..."
            className="w-full rounded-xl border border-border bg-bg-card py-2 pl-9 pr-4 text-xs text-text-primary outline-none focus:border-accent"
          />
        </div>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="py-16 text-center">
          <div className="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-2 border-accent border-t-transparent" />
          <p className="text-xs text-text-muted">Loading evidence items...</p>
        </div>
      )}

      {/* Empty State */}
      {!loading && filteredItems.length === 0 && (
        <div className="card p-12 text-center">
          <FileSearch className="mx-auto mb-3 text-text-muted" size={36} />
          <h3 className="text-base font-semibold">No evidence matched your filters</h3>
          <p className="mt-1 text-xs text-text-secondary">
            {id
              ? 'Try relaxing search keywords or choosing ALL channels.'
              : 'Execute an analysis first to populate live SerpApi evidence items.'}
          </p>
        </div>
      )}

      {/* Evidence Cards Grid */}
      <div className="grid gap-4 md:grid-cols-2">
        {filteredItems.map((item) => {
          const IconComponent = SOURCE_ICONS[item.source_type] || Globe;
          return (
            <div key={item.id} className="card p-5 flex flex-col justify-between">
              <div>
                <div className="mb-2 flex items-center justify-between">
                  <span className="inline-flex items-center gap-1.5 rounded bg-bg-secondary px-2 py-0.5 text-xs font-medium text-text-muted">
                    <IconComponent size={12} className="text-accent" />
                    {item.source_type.toUpperCase()}
                  </span>
                  <div className="flex items-center gap-2 text-xs">
                    <span className="text-text-muted">Strength:</span>
                    <span className="font-semibold text-accent">
                      {Math.round(item.evidence_strength ?? 0)}%
                    </span>
                  </div>
                </div>

                <h4 className="text-sm font-bold text-text-primary mb-1 line-clamp-2">
                  {item.title || 'Untitled Evidence Record'}
                </h4>

                <p className="text-xs text-text-secondary line-clamp-3 mb-4">
                  {item.snippet || 'No description provided.'}
                </p>
              </div>

              <div className="border-t border-border pt-3 flex items-center justify-between text-xs text-text-muted">
                <span>{item.source || 'Direct Search'}</span>
                {item.url && (
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-accent hover:underline font-medium"
                  >
                    Open Source
                    <ExternalLink size={12} />
                  </a>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
