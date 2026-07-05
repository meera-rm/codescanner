import { useState, useCallback, useRef, useEffect } from 'react';

export interface SnippetAnalysisResult {
  code_length: number;
  quality_score: number;
  complexity: { high: number; medium: number; low: number };
  security_issues: number;
  total_issues: number;
  findings: Array<{
    line: number;
    type: string;
    message: string;
    severity: string;
  }>;
  error?: string;
}

interface CachedAnalysis {
  result: SnippetAnalysisResult;
  timestamp: number;
}

export const useLiveCodeAnalysis = () => {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState<'python' | 'javascript' | 'typescript' | 'go' | 'java' | 'rust'>('python');
  const [analysis, setAnalysis] = useState<SnippetAnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const cacheRef = useRef<Map<string, CachedAnalysis>>(new Map());

  // Simple hash function for cache key
  const getCacheKey = useCallback((codeStr: string, lang: string): string => {
    // Simple hash using length + first/last chars (not crypto, just for cache key)
    const key = `${lang}_${codeStr.length}_${codeStr.charCodeAt(0)}_${codeStr.charCodeAt(codeStr.length - 1)}`;
    return key;
  }, []);

  const analyzeCode = useCallback(async (codeToAnalyze: string, lang: string) => {
    if (!codeToAnalyze || codeToAnalyze.trim().length === 0) {
      setAnalysis(null);
      return;
    }

    const cacheKey = getCacheKey(codeToAnalyze, lang);
    const cached = cacheRef.current.get(cacheKey);

    // Return cached result if available and fresh (< 5 minutes)
    if (cached && Date.now() - cached.timestamp < 5 * 60 * 1000) {
      setAnalysis(cached.result);
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/scan/analyze-snippet', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: codeToAnalyze,
          language: lang
        })
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const result: SnippetAnalysisResult = await response.json();
      setAnalysis(result);

      // Cache the result
      cacheRef.current.set(cacheKey, {
        result,
        timestamp: Date.now()
      });

      // Limit cache size to 50 entries
      if (cacheRef.current.size > 50) {
        const oldestKey = Array.from(cacheRef.current.entries()).sort(
          (a, b) => a[1].timestamp - b[1].timestamp
        )[0][0];
        cacheRef.current.delete(oldestKey);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Analysis failed';
      setError(errorMsg);
      setAnalysis(null);
    } finally {
      setIsAnalyzing(false);
    }
  }, [getCacheKey]);

  // Debounced analysis
  const handleCodeChange = useCallback((newCode: string) => {
    setCode(newCode);

    // Clear previous timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // Set new timer
    debounceTimerRef.current = setTimeout(() => {
      analyzeCode(newCode, language);
    }, 300); // 300ms debounce
  }, [language, analyzeCode]);

  const handleLanguageChange = useCallback((newLanguage: 'python' | 'javascript' | 'typescript' | 'go' | 'java' | 'rust') => {
    setLanguage(newLanguage);
    // Re-analyze with new language
    if (code.trim().length > 0) {
      analyzeCode(code, newLanguage);
    }
  }, [code, analyzeCode]);

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, []);

  const clearCache = useCallback(() => {
    cacheRef.current.clear();
  }, []);

  return {
    code,
    language,
    analysis,
    isAnalyzing,
    error,
    handleCodeChange,
    handleLanguageChange,
    clearCache
  };
};
