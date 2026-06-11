import { useState, useCallback } from 'react';
import { FunctionSelectItem } from '../components/FunctionSelector';

export interface BatchRefactorResult {
  function_name: string;
  file: string;
  line: number;
  original_code: string;
  refactored_code: string | null;
  explanation: string;
  risk_level: string;
  status: 'completed' | 'error' | 'rejected';
  error?: string;
}

export interface BatchRefactorState {
  batchId: string | null;
  status: 'idle' | 'processing' | 'completed' | 'error';
  totalFunctions: number;
  processedFunctions: number;
  results: BatchRefactorResult[];
  error: string | null;
  progress: number; // 0-100
}

export const useRefactorBatch = () => {
  const [state, setState] = useState<BatchRefactorState>({
    batchId: null,
    status: 'idle',
    totalFunctions: 0,
    processedFunctions: 0,
    results: [],
    error: null,
    progress: 0
  });

  const startBatchRefactor = useCallback(async (
    functions: FunctionSelectItem[],
    category?: string
  ) => {
    if (functions.length === 0) {
      setState(prev => ({
        ...prev,
        error: 'No functions selected'
      }));
      return null;
    }

    setState(prev => ({
      ...prev,
      status: 'processing',
      totalFunctions: functions.length,
      error: null
    }));

    try {
      // Convert FunctionSelectItem to format expected by API
      const payload = {
        functions: functions.map(f => ({
          name: f.name,
          file: f.file,
          line: f.line,
          code: f.code,
          complexity: f.complexity,
          severity: f.severity
        })),
        category: category || 'general'
      };

      const response = await fetch('/api/v1/scan/batch-refactor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const batchJob = await response.json();

      setState(prev => ({
        ...prev,
        batchId: batchJob.batch_id,
        status: batchJob.status === 'completed' ? 'completed' : 'processing',
        processedFunctions: batchJob.processed || 0,
        results: batchJob.results || [],
        progress: batchJob.total_functions > 0
          ? Math.round((batchJob.processed / batchJob.total_functions) * 100)
          : 0
      }));

      return batchJob.batch_id;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to start batch refactoring';
      setState(prev => ({
        ...prev,
        status: 'error',
        error: errorMsg
      }));
      return null;
    }
  }, []);

  const pollBatchStatus = useCallback(async (batchId: string) => {
    try {
      const response = await fetch(`/api/v1/scan/batch-refactor/${batchId}/status`);

      if (!response.ok) {
        throw new Error(`Failed to get batch status: ${response.statusText}`);
      }

      const batchJob = await response.json();

      const progress = batchJob.total_functions > 0
        ? Math.round((batchJob.processed / batchJob.total_functions) * 100)
        : 0;

      setState(prev => ({
        ...prev,
        status: batchJob.status === 'completed' ? 'completed' : 'processing',
        processedFunctions: batchJob.processed,
        results: batchJob.results || [],
        progress: progress
      }));

      return batchJob;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to poll batch status';
      setState(prev => ({
        ...prev,
        status: 'error',
        error: errorMsg
      }));
      return null;
    }
  }, []);

  const applyBatchResults = useCallback(async (
    batchId: string,
    functionResults: BatchRefactorResult[]
  ) => {
    try {
      const response = await fetch('/api/v1/scan/batch-refactor/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          batch_id: batchId,
          function_results: functionResults
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to apply batch refactoring: ${response.statusText}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to apply batch refactoring';
      setState(prev => ({
        ...prev,
        error: errorMsg
      }));
      return null;
    }
  }, []);

  const reset = useCallback(() => {
    setState({
      batchId: null,
      status: 'idle',
      totalFunctions: 0,
      processedFunctions: 0,
      results: [],
      error: null,
      progress: 0
    });
  }, []);

  return {
    state,
    startBatchRefactor,
    pollBatchStatus,
    applyBatchResults,
    reset
  };
};
