/**
 * useAnalysis – polls the backend for analysis status until completion.
 */
import { useCallback, useEffect, useRef, useState } from 'react';
import type { Analysis, EvidenceListResponse, EntityListResponse, SignalListResponse } from '../types';
import * as api from '../services/api';

interface UseAnalysisReturn {
  analysis: Analysis | null;
  evidence: EvidenceListResponse | null;
  entities: EntityListResponse | null;
  signals: SignalListResponse | null;
  loading: boolean;
  error: string | null;
  startAnalysis: (question: string) => Promise<string | null>;
  loadAnalysis: (id: string) => void;
}

export function useAnalysis(): UseAnalysisReturn {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [evidence, setEvidence] = useState<EvidenceListResponse | null>(null);
  const [entities, setEntities] = useState<EntityListResponse | null>(null);
  const [signals, setSignals] = useState<SignalListResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  const fetchFullResults = useCallback(async (id: string) => {
    try {
      const [ev, en, si] = await Promise.all([
        api.getEvidence(id),
        api.getEntities(id),
        api.getSignals(id),
      ]);
      setEvidence(ev);
      setEntities(en);
      setSignals(si);
    } catch {
      // Non-fatal: results page will still show analysis
    }
  }, []);

  const pollAnalysis = useCallback(
    (id: string) => {
      stopPolling();
      setLoading(true);
      setError(null);

      const poll = async () => {
        try {
          const data = await api.getAnalysis(id);
          setAnalysis(data);

          if (data.status === 'completed' || data.status === 'partial') {
            stopPolling();
            setLoading(false);
            await fetchFullResults(id);
          } else if (data.status === 'failed') {
            stopPolling();
            setLoading(false);
            setError(data.error_message || 'Analysis failed');
          }
        } catch (err) {
          // Keep polling on transient errors
          console.error('Poll error:', err);
        }
      };

      poll(); // immediate first check
      pollRef.current = setInterval(poll, 2000);
    },
    [stopPolling, fetchFullResults],
  );

  const startAnalysisFn = useCallback(
    async (question: string): Promise<string | null> => {
      setLoading(true);
      setError(null);
      setAnalysis(null);
      setEvidence(null);
      setEntities(null);
      setSignals(null);

      try {
        const res = await api.startAnalysis({ question });
        pollAnalysis(res.analysis_id);
        return res.analysis_id;
      } catch (err) {
        setLoading(false);
        setError(err instanceof Error ? err.message : 'Failed to start analysis');
        return null;
      }
    },
    [pollAnalysis],
  );

  const loadAnalysis = useCallback(
    (id: string) => {
      pollAnalysis(id);
    },
    [pollAnalysis],
  );

  useEffect(() => {
    return () => stopPolling();
  }, [stopPolling]);

  return {
    analysis,
    evidence,
    entities,
    signals,
    loading,
    error,
    startAnalysis: startAnalysisFn,
    loadAnalysis,
  };
}
