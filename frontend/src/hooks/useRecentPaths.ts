import { useState, useCallback, useEffect } from 'react';

export interface RecentPath {
  path: string;
  name: string;
  language: 'python' | 'javascript' | 'sql';
  timestamp: number;
  relative?: string;
}

const STORAGE_KEY = 'codescanner_recent_paths';
const MAX_RECENT = 10;

/**
 * Recent paths management hook
 * Stores and retrieves recently scanned paths
 */
export const useRecentPaths = () => {
  const [recentPaths, setRecentPaths] = useState<RecentPath[]>([]);

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const paths = JSON.parse(stored);
        setRecentPaths(paths);
      }
    } catch (err) {
      console.warn('Failed to load recent paths:', err);
    }
  }, []);

  // Add a path to recent history
  const addRecentPath = useCallback((path: RecentPath) => {
    setRecentPaths(prev => {
      // Remove duplicate if it exists
      const filtered = prev.filter(p => p.path !== path.path);

      // Add to front
      const updated = [{ ...path, timestamp: Date.now() }, ...filtered];

      // Keep only latest 10
      const trimmed = updated.slice(0, MAX_RECENT);

      // Save to localStorage
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
      } catch (err) {
        console.warn('Failed to save recent paths:', err);
      }

      return trimmed;
    });
  }, []);

  // Remove a path from history
  const removeRecentPath = useCallback((path: string) => {
    setRecentPaths(prev => {
      const updated = prev.filter(p => p.path !== path);
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      } catch (err) {
        console.warn('Failed to update recent paths:', err);
      }
      return updated;
    });
  }, []);

  // Clear all recent paths
  const clearRecentPaths = useCallback(() => {
    setRecentPaths([]);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (err) {
      console.warn('Failed to clear recent paths:', err);
    }
  }, []);

  // Get display name with timestamp
  const getDisplayName = useCallback((recentPath: RecentPath): string => {
    const date = new Date(recentPath.timestamp);
    const timeAgo = getTimeAgo(date);
    return `${recentPath.name} (${timeAgo})`;
  }, []);

  // Format time difference
  const getTimeAgo = (date: Date): string => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'just now';
  };

  return {
    recentPaths,
    addRecentPath,
    removeRecentPath,
    clearRecentPaths,
    getDisplayName,
    hasRecent: recentPaths.length > 0
  };
};
