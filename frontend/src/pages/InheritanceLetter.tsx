import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/PathPages.css';

export const InheritanceLetter: React.FC = () => {
  const navigate = useNavigate();
  const [directoryPath, setDirectoryPath] = useState('');
  const [loading, setLoading] = useState(false);
  const [letter, setLetter] = useState('');
  const [error, setError] = useState('');
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleBrowse = () => {
    fileInputRef.current?.click();
  };

  const handleDirectorySelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const firstFile = files[0];
      const relativePath = (firstFile as any).webkitRelativePath || firstFile.name;
      const directoryName = relativePath.split('/')[0] || relativePath;

      setDirectoryPath(directoryName);
      setError(`📁 Directory detected: "${directoryName}" - Please enter the full path below or continue with just the name`);
    }
  };

  const handleGenerate = async () => {
    if (!directoryPath.trim()) {
      setError('Please enter a directory path');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const response = await fetch('/api/v1/creative-suite/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ directory_path: directoryPath })
      });

      let errorMessage = '';
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        errorMessage = errorData.detail || `HTTP ${response.status}: ${response.statusText}`;
        throw new Error(errorMessage);
      }

      const data = await response.json();
      if (!data.job_id) throw new Error('No job ID returned from server');

      // Poll for results
      let jobResult = null;
      let attempts = 0;
      while (attempts < 30) {
        const statusResponse = await fetch(`/api/v1/creative-suite/${data.job_id}/letter`);

        // Handle 202 (still processing) - keep polling
        if (statusResponse.status === 202) {
          await new Promise(r => setTimeout(r, 1000));
          attempts++;
          continue;
        }

        // Handle 200 (completed)
        if (statusResponse.ok) {
          jobResult = await statusResponse.json();
          break;
        }

        // Handle other errors
        const errData = await statusResponse.json().catch(() => ({}));
        throw new Error(errData.detail || `Status check failed: ${statusResponse.status}`);
      }

      if (jobResult) {
        // Letter is returned directly from endpoint, format it nicely
        const letterText = typeof jobResult === 'string'
          ? jobResult
          : jobResult.letter
          ? JSON.stringify(jobResult.letter, null, 2)
          : JSON.stringify(jobResult, null, 2);
        setLetter(letterText);
      } else {
        setError('Generation timed out after 30 seconds');
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="path-page">
      <header className="page-header">
        <button className="back-btn" onClick={() => navigate('/')}>← Back</button>
        <h1>💌 Inheritance Letter</h1>
        <p>Generate a legacy letter for your code to future developers</p>
      </header>

      <main className="page-content">
        <div className="input-section">
          <label htmlFor="path">Directory Path:</label>
          <div className="input-with-button">
            <input
              id="path"
              type="text"
              placeholder="e.g., /path/to/your/project or browse folder"
              value={directoryPath}
              onChange={(e) => setDirectoryPath(e.target.value)}
              disabled={loading}
            />
            <button
              onClick={handleBrowse}
              disabled={loading}
              className="browse-btn"
              title="Browse for directory"
            >
              📁 Browse
            </button>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              style={{ display: 'none' }}
              onChange={handleDirectorySelect}
              {...({ webkitdirectory: '', mozdirectory: '' } as any)}
            />
          </div>
          <button
            onClick={handleGenerate}
            disabled={loading || !directoryPath.trim()}
            className="analyze-btn"
          >
            {loading ? 'Generating...' : 'Generate Letter'}
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {letter && (
          <div className="result-section">
            <h2>💌 Inheritance Letter</h2>
            <div className="letter-content">
              <pre>{letter}</pre>
            </div>
            <button
              onClick={() => {
                const element = document.createElement('a');
                element.setAttribute('href', `data:text/plain;charset=utf-8,${encodeURIComponent(letter)}`);
                element.setAttribute('download', 'inheritance-letter.txt');
                element.style.display = 'none';
                document.body.appendChild(element);
                element.click();
                document.body.removeChild(element);
              }}
              className="download-btn"
            >
              📥 Download Letter
            </button>
          </div>
        )}
      </main>
    </div>
  );
};

export default InheritanceLetter;
