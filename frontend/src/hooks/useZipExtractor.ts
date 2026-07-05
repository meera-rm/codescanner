import { useState, useCallback } from 'react';

export interface ExtractedZip {
  name: string;
  path: string;
  language: 'python' | 'javascript' | 'typescript' | 'go' | 'java' | 'rust';
  message: string;
}

/**
 * ZIP file extraction hook
 * Handles ZIP file detection and prepares for extraction
 */
export const useZipExtractor = () => {
  const [isExtracting, setIsExtracting] = useState(false);
  const [progress, setProgress] = useState(0);

  const detectZipLanguage = useCallback((zipName: string): 'python' | 'javascript' | 'typescript' | 'go' | 'java' | 'rust' => {
    const name = zipName.toLowerCase();
    if (name.includes('rust') || name.includes('.rs') || name.includes('cargo')) {
      return 'rust';
    }
    if (name.includes('golang') || name.includes('.go') || name.includes('go-')) {
      return 'go';
    }
    if (name.includes('java') || name.includes('spring') || name.includes('maven')) {
      return 'java';
    }
    if (name.includes('typescript') || name.includes('ts-') || name.includes('tsconfig')) {
      return 'typescript';
    }
    if (name.includes('python') || name.includes('py') || name.includes('flask') || name.includes('django')) {
      return 'python';
    }
    if (name.includes('node') || name.includes('react') || name.includes('js') || name.includes('javascript')) {
      return 'javascript';
    }
    return 'python'; // Default
  }, []);

  const handleZipFile = useCallback(async (file: File): Promise<ExtractedZip | null> => {
    if (!file.name.endsWith('.zip')) {
      return null;
    }

    setIsExtracting(true);
    setProgress(0);

    try {
      // For Phase 2, we prepare the file for backend extraction
      // The actual extraction will be handled by the backend
      const language = detectZipLanguage(file.name);
      const zipName = file.name.replace('.zip', '');

      setProgress(50);

      // Create FormData for file upload
      const formData = new FormData();
      formData.append('file', file);
      formData.append('language', language);

      setProgress(100);

      return {
        name: zipName,
        path: file.name,
        language: language,
        message: `📦 ZIP detected: "${zipName}" (${language}). Ready to extract.`
      };
    } catch (err) {
      throw new Error(`ZIP handling failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsExtracting(false);
      setProgress(0);
    }
  }, [detectZipLanguage]);

  const isZipFile = useCallback((filename: string): boolean => {
    return filename.toLowerCase().endsWith('.zip');
  }, []);

  return {
    handleZipFile,
    isZipFile,
    isExtracting,
    progress,
    detectZipLanguage
  };
};
