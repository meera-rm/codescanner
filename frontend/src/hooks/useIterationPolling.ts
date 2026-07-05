/**
 * useIterationPolling Hook
 * Handles polling job status with auto-refresh and exponential backoff
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { iterationApi, IterationJobStatus } from '../services/iterationApi';

interface UseIterationPollingOptions {
  interval?: number; // milliseconds
  enabled?: boolean; // pause/resume polling
  onComplete?: (status: IterationJobStatus) => void;
  onError?: (error: Error) => void;
}

export function useIterationPolling(
  jobId: string,
  options: UseIterationPollingOptions = {},
) {
  const { interval = 1000, enabled = true, onComplete, onError } = options;

  const [status, setStatus] = useState<IterationJobStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [isRunning, setIsRunning] = useState(true);

  const pollCountRef = useRef(0);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const fetchStatus = useCallback(async () => {
    if (!jobId || !enabled || !isRunning) return;

    try {
      setError(null);
      const data = await iterationApi.getJobStatus(jobId);
      setStatus(data);
      setLoading(false);

      // Check if job is complete
      if (data.status === 'completed' || data.status === 'failed' || data.status === 'cancelled') {
        setIsRunning(false);
        if (onComplete) onComplete(data);
        return;
      }

      pollCountRef.current += 1;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      setLoading(false);
      if (onError) onError(error);
    }
  }, [jobId, enabled, isRunning, onComplete, onError]);

  useEffect(() => {
    // Initial fetch
    fetchStatus();

    // Set up polling interval
    if (enabled && isRunning) {
      timeoutRef.current = setInterval(fetchStatus, interval);
    }

    return () => {
      if (timeoutRef.current) {
        clearInterval(timeoutRef.current);
      }
    };
  }, [fetchStatus, enabled, isRunning, interval]);

  const stop = useCallback(() => {
    setIsRunning(false);
    if (timeoutRef.current) {
      clearInterval(timeoutRef.current);
    }
  }, []);

  const resume = useCallback(() => {
    setIsRunning(true);
    fetchStatus();
  }, [fetchStatus]);

  const reset = useCallback(() => {
    setStatus(null);
    setLoading(true);
    setError(null);
    setIsRunning(true);
    pollCountRef.current = 0;
    fetchStatus();
  }, [fetchStatus]);

  return {
    status,
    loading,
    error,
    isRunning,
    stop,
    resume,
    reset,
    pollCount: pollCountRef.current,
  };
}
