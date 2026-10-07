/**
 * Clariq API client.
 * All requests go through the Vite proxy → FastAPI backend.
 * Never exposes API keys to the browser.
 */

import type {
  Analysis,
  AnalysisListResponse,
  AnalyzeRequest,
  AnalyzeStartResponse,
  CompareRequest,
  EntityListResponse,
  EvidenceListResponse,
  HealthResponse,
  SignalListResponse,
} from '../types';

const BASE = '';  // proxied via vite.config.ts

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });

  if (!res.ok) {
    const body = await res.text().catch(() => 'Unknown error');
    throw new ApiError(res.status, `${res.status}: ${body}`);
  }

  return res.json() as Promise<T>;
}

/* ─── Health ─── */
export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/health');
}

/* ─── Analysis ─── */
export function startAnalysis(questionOrReq: string | AnalyzeRequest): Promise<AnalyzeStartResponse> {
  const payload: AnalyzeRequest =
    typeof questionOrReq === 'string' ? { question: questionOrReq } : questionOrReq;

  return request<AnalyzeStartResponse>('/api/analyze', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getAnalyses(limit: number = 20): Promise<AnalysisListResponse> {
  return request<AnalysisListResponse>(`/api/analyze?limit=${limit}`);
}

export function getAnalysis(id: string): Promise<Analysis> {
  return request<Analysis>(`/api/analyze/${id}`);
}

export function getEvidence(id: string): Promise<EvidenceListResponse> {
  return request<EvidenceListResponse>(`/api/analyze/${id}/evidence`);
}

export function getSignals(id: string): Promise<SignalListResponse> {
  return request<SignalListResponse>(`/api/analyze/${id}/signals`);
}

export function getEntities(id: string): Promise<EntityListResponse> {
  return request<EntityListResponse>(`/api/analyze/${id}/entities`);
}

/* ─── Compare ─── */
export function startCompare(req: CompareRequest): Promise<AnalyzeStartResponse> {
  return request<AnalyzeStartResponse>('/api/compare', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

export { ApiError };
