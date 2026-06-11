import { useState, useRef, useCallback } from 'react';
import { usePathDetection } from './usePathDetection';
import { useZipExtractor } from './useZipExtractor';
import { useGitHubDownloader } from './useGitHubDownloader';
import { useRecentPaths } from './useRecentPaths';

export interface UploadState {
  directoryPath: string;
  language: 'python' | 'javascript' | 'sql';
  message: string;
  isLoading: boolean;
  error: string;
}

export interface UploadManagerOptions {
  onPathSelected?: (path: string, language: string) => void;
  onError?: (error: string) => void;
  onMessage?: (message: string) => void;
}

/**
 * Unified upload manager hook
 * Phase 2: Consolidates browse, drag & drop, text input, ZIP, and GitHub handlers
 */
export const useUploadManager = (options: UploadManagerOptions = {}) => {
  const { searchPath, isSearching } = usePathDetection();
  const { handleZipFile, isZipFile } = useZipExtractor();
  const { handleGitHubUrl, isGitHubUrl } = useGitHubDownloader();
  const { recentPaths, addRecentPath } = useRecentPaths();

  const folderInputRef = useRef<HTMLInputElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [state, setState] = useState<UploadState>({
    directoryPath: '',
    language: 'python',
    message: '',
    isLoading: false,
    error: ''
  });

  // Detect language from file extension
  const detectLanguage = useCallback((path: string, filename?: string): 'python' | 'javascript' | 'sql' => {
    const fullStr = `${path} ${filename || ''}`.toLowerCase();

    // Check for JavaScript indicators (file extensions or project markers)
    if (fullStr.includes('.js') || fullStr.includes('.jsx') || fullStr.includes('.ts') || fullStr.includes('.tsx') ||
        fullStr.includes('package.json') || fullStr.includes('vite.config') || fullStr.includes('webpack') ||
        fullStr.includes('node_modules') || fullStr.includes('react') || fullStr.includes('next') ||
        fullStr.includes('angular') || fullStr.includes('vue')) {
      return 'javascript';
    }

    // Check for SQL indicators
    if (fullStr.includes('.sql') || fullStr.includes('postgres') || fullStr.includes('mysql')) {
      return 'sql';
    }

    // Check for Python indicators (file extensions or project markers)
    if (fullStr.includes('.py') || fullStr.includes('python') || fullStr.includes('django') ||
        fullStr.includes('flask') || fullStr.includes('requirements.txt') || fullStr.includes('pipfile')) {
      return 'python';
    }

    return 'python'; // Default to Python
  }, []);

  // Get language emoji label
  const getLanguageLabel = useCallback((lang: string) => {
    switch (lang) {
      case 'javascript':
        return '📄 JS';
      case 'sql':
        return '📊 SQL';
      default:
        return '🐍 Python';
    }
  }, []);

  // Process detected path
  const processPath = useCallback(async (folderName: string, webkitPath?: string) => {
    setState(prev => ({ ...prev, isLoading: true }));

    const lang = detectLanguage(webkitPath || folderName, folderName);

    try {
      const result = await searchPath(folderName);

      const finalPath = result.found ? result.path : result.path;
      const finalMessage = result.found
        ? `📁 Auto-detected: "${result.name}" (${getLanguageLabel(lang)}) at ${result.relative}`
        : `📁 Selected: "${folderName}" (${getLanguageLabel(lang)})`;

      setState(prev => ({
        ...prev,
        directoryPath: finalPath,
        language: lang,
        message: finalMessage,
        error: ''
      }));

      // Add to recent paths (Phase 2)
      addRecentPath({
        path: finalPath,
        name: result.name || folderName,
        language: lang,
        relative: result.relative,
        timestamp: Date.now()
      });

      options.onPathSelected?.(finalPath, lang);
      options.onMessage?.(finalMessage);
    } catch (err) {
      const error = `Failed to process path: ${err instanceof Error ? err.message : 'Unknown error'}`;
      setState(prev => ({ ...prev, error }));
      options.onError?.(error);
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  }, [searchPath, detectLanguage, getLanguageLabel, options]);

  // Browse folder
  const browseFolders = useCallback(() => {
    folderInputRef.current?.click();
  }, []);

  // Handle folder selection from browse
  const handleFolderSelect = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const firstFile = files[0];
    const webkitPath = (firstFile as any).webkitRelativePath;

    if (webkitPath) {
      const parts = webkitPath.split('/');
      const folderName = parts[0];
      await processPath(folderName, webkitPath);
    } else {
      // Single file selected
      const lang = detectLanguage(firstFile.name);
      setState(prev => ({
        ...prev,
        directoryPath: firstFile.name,
        language: lang,
        message: `📄 Selected file: "${firstFile.name}" (${getLanguageLabel(lang)})`
      }));
    }

    // Reset input
    e.target.value = '';
  }, [processPath, detectLanguage, getLanguageLabel]);

  // Handle drag over
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  // Handle drag enter/leave
  const handleDragChange = useCallback((e: React.DragEvent, isActive: boolean) => {
    e.preventDefault();
    e.stopPropagation();
    // Return isActive state for UI feedback
    return isActive;
  }, []);

  // Handle drop - supports folders, files, ZIP files (Phase 2), and GitHub URLs
  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();

    const items = e.dataTransfer?.items;
    if (!items) return;

    setState(prev => ({ ...prev, isLoading: true }));

    try {
      for (let i = 0; i < items.length; i++) {
        const item = items[i];
        if (item.kind === 'file') {
          const entry = item.webkitGetAsEntry?.();
          const file = item.getAsFile();

          // Check if it's a ZIP file (Phase 2)
          if (file && isZipFile(file.name)) {
            const zipResult = await handleZipFile(file);
            if (zipResult) {
              setState(prev => ({
                ...prev,
                message: zipResult.message,
                directoryPath: zipResult.path,
                language: zipResult.language
              }));
              options.onMessage?.(zipResult.message);
            }
          } else if (entry?.isDirectory) {
            // Dropped a folder
            await processPath(entry.name);
          } else if (entry?.isFile) {
            // Dropped a file
            const lang = detectLanguage(file?.name || '');
            setState(prev => ({
              ...prev,
              directoryPath: file?.name || '',
              language: lang,
              message: `📄 Dropped file: "${file?.name}" (${getLanguageLabel(lang)})`
            }));
          }
          break;
        }
      }
    } catch (err) {
      const error = `Drop failed: ${err instanceof Error ? err.message : 'Unknown error'}`;
      setState(prev => ({ ...prev, error }));
      options.onError?.(error);
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  }, [processPath, detectLanguage, getLanguageLabel, handleZipFile, isZipFile, options]);

  // Handle text input - supports paths, GitHub URLs (Phase 2), and ZIP files (Phase 2)
  const handleTextInput = useCallback(async (input: string) => {
    if (!input.trim()) {
      setState(prev => ({ ...prev, directoryPath: '', message: '' }));
      return;
    }

    setState(prev => ({ ...prev, isLoading: true }));

    try {
      // Check if it's a GitHub URL (Phase 2)
      if (isGitHubUrl(input)) {
        const gitHubResult = await handleGitHubUrl(input);
        if (gitHubResult) {
          setState(prev => ({
            ...prev,
            directoryPath: gitHubResult.path,
            language: gitHubResult.language,
            message: gitHubResult.message,
            error: ''
          }));
          options.onMessage?.(gitHubResult.message);
          setState(prev => ({ ...prev, isLoading: false }));
          return;
        }
      }

      // Otherwise treat as local path
      await processPath(input);
    } catch (err) {
      const error = `Input processing failed: ${err instanceof Error ? err.message : 'Unknown error'}`;
      setState(prev => ({ ...prev, error }));
      options.onError?.(error);
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  }, [processPath, isGitHubUrl, handleGitHubUrl, options]);

  // Clear all
  const reset = useCallback(() => {
    setState({
      directoryPath: '',
      language: 'python',
      message: '',
      isLoading: false,
      error: ''
    });
  }, []);

  return {
    // State
    state,
    recentPaths,

    // File inputs
    folderInputRef,
    fileInputRef,

    // Handlers
    browseFolders,
    handleFolderSelect,
    handleDragOver,
    handleDragChange,
    handleDrop,
    handleTextInput,

    // Utilities
    reset,
    getLanguageLabel,
    isSearching,
    supportsInput: (input: string) => isGitHubUrl(input) || isZipFile(input)
  };
};
