import { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { 
  FileSearch, 
  Search as SearchIcon, 
  ArrowUpDown, 
  Filter, 
  ArrowRight,
  AlertCircle
} from 'lucide-react';
import type { EvidenceItem } from '../types';
import * as api from '../services/api';
import EvidenceCard from '../components/EvidenceCard';

type SortOption = 'strength' | 'relevance' | 'freshness';

export default function EvidencePage() {
  const [params] = useSearchParams();
  const id = params.get('id');
  const entityParam = params.get('entity');

  const [activeTab, setActiveTab] = useState<string>('ALL');
  const [sortBy, setSortBy] = useState<SortOption>('strength');
  const [searchQuery, setSearchQuery] = useState('');
  const [entityFilter, setEntityFilter] = useState(entityParam || '');
  const [items, setItems] = useState<EvidenceItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      setLoading(true);
      setError(null);
      api.getEvidence(id)
        .then((res) => {
          setItems(res.items || []);
        })
        .catch((err) => {
          setError(err instanceof Error ? err.message : 'Failed to retrieve evidence items');
          setItems([]);
        })
        .finally(() => setLoading(false));
    }
  }, [id]);

  // Derive distinct entities present in evidence
  const distinctEntities = Array.from(
    new Set(items.map((i) => i.entity).filter((ent): ent is string => Boolean(ent)))
  );

  const filteredItems = items
    .filter((item) => {
      // Source Tab filter
      if (activeTab !== 'ALL') {
        const itemType = item.source_type.toLowerCase();
        const tabType = activeTab.toLowerCase();
        if (itemType !== tabType && !(itemType === 'job' && tabType === 'jobs')) {
          return false;
        }
      }

      // Entity filter
      if (entityFilter && entityFilter !== 'ALL') {
        if (!item.entity || !item.entity.toLowerCase().includes(entityFilter.toLowerCase())) {
          return false;
        }
      }

      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        const titleMatch = item.title?.toLowerCase().includes(q);
        const snippetMatch = item.snippet?.toLowerCase().includes(q);
        const sourceMatch = item.source?.toLowerCase().includes(q);
        const entityMatch = item.entity?.toLowerCase().includes(q);
        return titleMatch || snippetMatch || sourceMatch || entityMatch;
      }

      return true;
    })
    .sort((a, b) => {
      if (sortBy === 'relevance') {
        return (b.relevance_score ?? 0) - (a.relevance_score ?? 0);
      }
      if (sortBy === 'freshness') {
        return (b.freshness_score ?? 0) - (a.freshness_score ?? 0);
      }
      // default: evidence strength
      return (b.evidence_strength ?? 0) - (a.evidence_strength ?? 0);
    });

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 border-b border-border pb-6 md:flex-row md:items-center">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="rounded bg-accent/20 px-2.5 py-0.5 text-xs font-bold text-accent uppercase">
              Unified Evidence Engine
            </span>
            {id && (
              <span className="text-xs text-text-muted">
                Analysis #{id.slice(0, 8)}
              </span>
            )}
          </div>
          <h1 className="text-2xl md:text-3xl font-black text-text-primary">
            Evidence Explorer
          </h1>
          <p className="mt-1 text-xs md:text-sm text-text-secondary">
            Cross-engine evidence records with preserved URLs, relevance scores, and verifiable provenance.
          </p>
        </div>

        {id && (
          <Link
            to={`/dashboard?id=${id}`}
            className="inline-flex items-center gap-2 rounded-xl border border-border bg-bg-card px-4 py-2 text-xs font-semibold text-text-primary hover:border-accent hover:text-accent transition self-start md:self-auto"
          >
            Back to Dashboard
            <ArrowRight size={14} />
          </Link>
        )}
      </div>

      {error && (
        <div className="flex items-center gap-3 rounded-xl border border-danger/30 bg-danger/10 p-4 text-xs text-danger">
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* Control Bar: Tabs, Search, Entity Filter, Sorting */}
      <div className="card p-4 space-y-4">
        {/* Source Engine Tabs */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border pb-3">
          <div className="flex flex-wrap gap-1.5">
            {[
              { id: 'ALL', label: 'ALL' },
              { id: 'JOB', label: 'JOBS' },
              { id: 'NEWS', label: 'NEWS' },
              { id: 'WEB', label: 'WEB' },
              { id: 'TREND', label: 'TRENDS' },
              { id: 'LOCAL', label: 'LOCAL' },
            ].map(({ id: tabId, label }) => (
              <button
                key={tabId}
                onClick={() => setActiveTab(tabId)}
                className={`rounded-lg px-3 py-1.5 text-xs font-bold transition ${
                  activeTab === tabId
                    ? 'bg-accent text-white shadow-sm'
                    : 'border border-border bg-bg-secondary text-text-secondary hover:text-text-primary hover:bg-bg-card'
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          <div className="text-xs font-semibold text-text-muted">
            Showing <span className="text-accent font-bold">{filteredItems.length}</span> of {items.length} records
          </div>
        </div>

        {/* Filter Controls Row */}
        <div className="grid gap-3 sm:grid-cols-3">
          {/* Search Input */}
          <div className="relative">
            <SearchIcon size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter by title, snippet, or keyword..."
              className="w-full rounded-xl border border-border bg-bg-secondary py-2 pl-9 pr-3 text-xs text-text-primary outline-none focus:border-accent"
            />
          </div>

          {/* Entity Filter Dropdown */}
          <div className="relative">
            <Filter size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
            <select
              value={entityFilter}
              onChange={(e) => setEntityFilter(e.target.value)}
              className="w-full rounded-xl border border-border bg-bg-secondary py-2 pl-9 pr-3 text-xs text-text-primary outline-none focus:border-accent"
            >
              <option value="">All Detected Entities</option>
              {distinctEntities.map((ent) => (
                <option key={ent} value={ent}>
                  {ent}
                </option>
              ))}
            </select>
          </div>

          {/* Sort By Dropdown */}
          <div className="relative">
            <ArrowUpDown size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortOption)}
              className="w-full rounded-xl border border-border bg-bg-secondary py-2 pl-9 pr-3 text-xs text-text-primary outline-none focus:border-accent"
            >
              <option value="strength">Sort by Evidence Strength</option>
              <option value="relevance">Sort by Relevance Score</option>
              <option value="freshness">Sort by Freshness Score</option>
            </select>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="py-20 text-center">
          <div className="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-2 border-accent border-t-transparent" />
          <p className="text-xs text-text-muted">Loading verified SerpApi evidence records...</p>
        </div>
      )}

      {/* Empty State */}
      {!loading && filteredItems.length === 0 && (
        <div className="card p-16 text-center">
          <FileSearch className="mx-auto mb-3 text-text-muted" size={40} />
          <h3 className="text-base font-bold text-text-primary">No evidence matched your filters</h3>
          <p className="mt-1 text-xs text-text-secondary max-w-sm mx-auto">
            {id
              ? 'Try clearing your search keyword, resetting the entity filter, or selecting the ALL tab.'
              : 'Provide an active analysis ID to explore live multi-engine evidence.'}
          </p>
          {(searchQuery || entityFilter || activeTab !== 'ALL') && (
            <button
              onClick={() => {
                setSearchQuery('');
                setEntityFilter('');
                setActiveTab('ALL');
              }}
              className="mt-4 rounded-lg bg-bg-secondary px-4 py-2 text-xs font-bold text-accent border border-border hover:bg-bg-card transition"
            >
              Reset Filters
            </button>
          )}
        </div>
      )}

      {/* Evidence Cards Grid */}
      <div className="grid gap-4 md:grid-cols-2">
        {filteredItems.map((evidenceItem) => (
          <EvidenceCard key={evidenceItem.id} evidence={evidenceItem} />
        ))}
      </div>
    </div>
  );
}
