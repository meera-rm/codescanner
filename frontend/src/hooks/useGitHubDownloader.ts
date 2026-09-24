import { useState, useCallback } from 'react';

export interface GitHubRepo {
  owner: string;
  repo: string;
  url: string;
  branch: string;
  language: 'python' | 'javascript' | 'typescript' | 'go' | 'java' | 'rust';
}

export interface GitHubDownloadResult {
  name: string;
  path: string;
  language: 'python' | 'javascript' | 'typescript' | 'go' | 'java' | 'rust';
  owner: string;
  repo: string;
  message: string;
}

/**
 * GitHub repository downloader hook
 * Parses GitHub URLs and prepares for download
 */
export const useGitHubDownloader = () => {
  const [isDownloading, setIsDownloading] = useState(false);
  const [progress, setProgress] = useState(0);

  // Parse GitHub URL
  const parseGitHubUrl = useCallback((urlString: string): GitHubRepo | null => {
    try {
      // Support formats: github.com/owner/repo, https://github.com/owner/repo, git@github.com:owner/repo.git
      let owner = '';
      let repo = '';
      let branch = 'main';

      const url = urlString.trim();

      // Extract from https://github.com/owner/repo format
      const httpsMatch = url.match(/github\.com\/([^\/]+)\/([^\/\s]+?)(?:\.git)?(?:\/tree\/([^\/\s]+))?$/);
      if (httpsMatch) {
        owner = httpsMatch[1];
        repo = httpsMatch[2];
        branch = httpsMatch[3] || 'main';
      }

      // Extract from git@github.com:owner/repo.git format
      const sshMatch = url.match(/git@github\.com:([^\/]+)\/([^\/\s]+?)(?:\.git)?$/);
      if (sshMatch) {
        owner = sshMatch[1];
        repo = sshMatch[2];
      }

      if (!owner || !repo) {
        return null;
      }

      return {
        owner,
        repo,
        url: `https://github.com/${owner}/${repo}`,
        branch,
        language: detectRepoLanguage(repo)
      };
    } catch {
      return null;
    }
  }, []);

  // Detect likely language from repo name
  const detectRepoLanguage = (repoName: string): 'python' | 'javascript' | 'typescript' | 'go' | 'java' | 'rust' => {
    const name = repoName.toLowerCase();
    if (name.includes('python') || name.includes('py') || name.includes('flask') || name.includes('django') || name.includes('etl')) {
      return 'python';
    }
    if (name.includes('node') || name.includes('react') || name.includes('js') || name.includes('frontend') || name.includes('typescript')) {
      return 'javascript';
    }
    return 'python'; // Default
  };

  // Handle GitHub URL input
  const handleGitHubUrl = useCallback(async (urlString: string): Promise<GitHubDownloadResult | null> => {
    const gitHubRepo = parseGitHubUrl(urlString);
    if (!gitHubRepo) {
      return null;
    }

    setIsDownloading(true);
    setProgress(0);

    try {
      setProgress(25);

      // Validate repo exists (in Phase 2, this would call a backend API)
      // For now, we prepare the download info
      const repoName = gitHubRepo.repo;

      setProgress(75);

      // Get language emoji
      const langEmoji = gitHubRepo.language === 'javascript' ? '📄' : '🐍';

      setProgress(100);

      return {
        name: repoName,
        path: gitHubRepo.url,
        language: gitHubRepo.language,
        owner: gitHubRepo.owner,
        repo: gitHubRepo.repo,
        message: `🔗 GitHub: ${gitHubRepo.owner}/${gitHubRepo.repo} (${langEmoji} ${gitHubRepo.language}). Ready to download.`
      };
    } catch (err) {
      throw new Error(`GitHub parsing failed: ${err instanceof Error ? err.message : 'Invalid URL'}`);
    } finally {
      setIsDownloading(false);
      setProgress(0);
    }
  }, [parseGitHubUrl]);

  // Check if input is a GitHub URL
  const isGitHubUrl = useCallback((input: string): boolean => {
    return input.includes('github.com') || input.startsWith('git@github.com:');
  }, []);

  return {
    handleGitHubUrl,
    parseGitHubUrl,
    isGitHubUrl,
    isDownloading,
    progress,
    detectRepoLanguage
  };
};
