import { useState, useCallback } from 'react';

export interface PathResult {
  name: string;
  path: string;
  relative: string;
}

export interface PathDetectionResult {
  found: boolean;
  path: string;
  name: string;
  relative: string;
  message: string;
}

/**
 * Smart path detection hook
 * Searches for folders by name across Documents directory
 */
export const usePathDetection = () => {
  const [isSearching, setIsSearching] = useState(false);

  const searchPath = useCallback(async (query: string): Promise<PathDetectionResult> => {
    if (!query || query.trim().length === 0) {
      return {
        found: false,
        path: '',
        name: '',
        relative: '',
        message: 'Empty query'
      };
    }

    setIsSearching(true);
    try {
      const response = await fetch(`/api/v1/scan/search-paths/${encodeURIComponent(query)}`);
      const data = await response.json();

      if (data.results && data.results.length > 0) {
        const result = data.results[0];
        return {
          found: true,
          path: result.path,
          name: result.name,
          relative: result.relative,
          message: `Found at: ${result.relative}`
        };
      }

      return {
        found: false,
        path: query,
        name: query,
        relative: '',
        message: `Not found in Documents. Using: "${query}"`
      };
    } catch (err) {
      return {
        found: false,
        path: query,
        name: query,
        relative: '',
        message: `Search failed. Using: "${query}"`
      };
    } finally {
      setIsSearching(false);
    }
  }, []);

  return { searchPath, isSearching };
};
