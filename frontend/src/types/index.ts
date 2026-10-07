/* ─── Analysis Types ─── */

export type AnalysisStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'partial';
export type ConfidenceLevel = 'HIGH' | 'MEDIUM' | 'LOW';
export type SourceType = 'job' | 'news' | 'web' | 'trend' | 'local';
export type SignalDirection = 'positive' | 'negative' | 'neutral';
export type SignalType =
  | 'HIRING'
  | 'DEMAND'
  | 'GROWTH'
  | 'INVESTMENT'
  | 'POPULARITY'
  | 'RECENCY'
  | 'COMPETITION'
  | 'RISK';
export type ContradictionSeverity = 'low' | 'medium' | 'high';
export type IntelligenceMode = 'career' | 'company' | 'technology' | 'compare';

/* ─── API Schemas ─── */

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export interface AnalyzeRequest {
  question: string;
}

export interface AnalyzeStartResponse {
  analysis_id: string;
  status: string;
}

export interface Analysis {
  id: string;
  question: string;
  intent: string | null;
  mode: string | null;
  status: AnalysisStatus;
  current_stage: string | null;
  overall_score: number | null;
  confidence_score: number | null;
  confidence_level: ConfidenceLevel | null;
  result_data: Record<string, unknown> | null;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface AnalysisListItem {
  id: string;
  question: string;
  intent: string | null;
  mode: string | null;
  status: AnalysisStatus;
  overall_score: number | null;
  confidence_level: ConfidenceLevel | null;
  created_at: string;
  completed_at: string | null;
}

export interface AnalysisListResponse {
  total: number;
  items: AnalysisListItem[];
}

export interface EvidenceItem {
  id: string;
  analysis_id: string;
  search_id: string | null;
  title: string | null;
  url: string | null;
  source: string | null;
  source_type: SourceType;
  snippet: string | null;
  entity: string | null;
  location: string | null;
  published_at: string | null;
  relevance_score: number | null;
  freshness_score: number | null;
  reliability_score: number | null;
  evidence_strength: number | null;
  trend_data?: TrendData | null;
}

export interface TrendData {
  query: string;
  average_interest: number | null;
  interest_label: string;
  geo: string;
  time_range: string;
  trend_direction: 'rising' | 'falling' | 'stable' | 'insufficient_data';
  peak_interest: number | null;
  timeline_data: Array<{ date: string; value: number }>;
}

export interface EvidenceListResponse {
  analysis_id: string;
  total: number;
  items: EvidenceItem[];
}

export interface EntityItem {
  id: string;
  analysis_id: string;
  name: string;
  normalized_name: string;
  type: string;
  mention_count: number;
  evidence_score: number | null;
}

export interface EntityListResponse {
  analysis_id: string;
  total: number;
  items: EntityItem[];
}

export interface SignalItem {
  id: string;
  analysis_id: string;
  entity: string | null;
  type: SignalType;
  direction: SignalDirection;
  strength: number;
  evidence_count: number;
  description: string | null;
  evidence_ids: string[] | null;
}

export interface SignalListResponse {
  analysis_id: string;
  total: number;
  items: SignalItem[];
}

export interface ContradictionItem {
  id: string;
  analysis_id: string;
  entity_name: string | null;
  positive_signal: string | null;
  negative_signal: string | null;
  severity: ContradictionSeverity | null;
  confidence: number | null;
  description: string | null;
  evidence_ids: string[] | null;
}

export interface CompareRequest {
  question: string;
  entities?: string[];
  mode?: IntelligenceMode;
}

/* ─── Result Data (nested inside Analysis.result_data) ─── */

export interface CategoryScores {
  job_opportunity: number;
  market_demand: number;
  recent_activity: number;
  company_presence: number;
  evidence_confidence: number;
}

export interface CityResult {
  city: string;
  overall_score: number;
  category_scores: CategoryScores;
  signals: SignalItem[];
  contradictions: ContradictionItem[];
  confidence: number;
  confidence_level: ConfidenceLevel;
  evidence_count: number;
  evidence_ids: string[];
}

export interface CareerIntelligenceResult {
  question: string;
  mode: 'career';
  cities: CityResult[];
  recommendation: {
    top_city: string;
    score: number;
    confidence: number;
    confidence_level: ConfidenceLevel;
    reasons: string[];
    actions: string[];
  };
  explanation: {
    contributions: Array<{
      label: string;
      score_contribution: number;
      evidence_count: number;
      direction: 'positive' | 'negative';
    }>;
  };
  statistics: {
    total_evidence: number;
    total_searches: number;
    total_entities: number;
    total_signals: number;
    total_contradictions: number;
  };
}

export interface CompanyResult {
  company: string;
  overall_score: number;
  signals: SignalItem[];
  contradictions: ContradictionItem[];
  confidence: number;
  confidence_level: ConfidenceLevel;
  evidence_count: number;
}

export interface TechnologyResult {
  technology: string;
  overall_score: number;
  signals: SignalItem[];
  contradictions: ContradictionItem[];
  confidence: number;
  confidence_level: ConfidenceLevel;
  recommendation: string;
  evidence_count: number;
}
