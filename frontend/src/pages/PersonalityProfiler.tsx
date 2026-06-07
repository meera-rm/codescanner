import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/PathPages.css';

export const PersonalityProfiler: React.FC = () => {
  const navigate = useNavigate();
  const [directoryPath, setDirectoryPath] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
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

      // Show the detected directory name and instructions
      setDirectoryPath(directoryName);
      setError(`📁 Directory detected: "${directoryName}" - Please enter the full path below or continue with just the name`);
    }
  };

  const handleAnalyze = async () => {
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
        const statusResponse = await fetch(`/api/v1/creative-suite/${data.job_id}`);

        // Handle 202 (still processing) - extract message but keep polling
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
        if (jobResult.personality) {
          setResult(jobResult.personality);
        } else {
          setError('No personality data in response');
        }
      } else {
        setError('Analysis timed out after 30 seconds');
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
        <h1>🎭 Personality Profiler</h1>
        <p>Analyze your codebase and discover its personality archetype</p>
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
            onClick={handleAnalyze}
            disabled={loading || !directoryPath.trim()}
            className="analyze-btn"
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {result && (
          <div className="result-section">
            <h2>Personality Analysis Result</h2>
            <div className="result-card">
              <div className="archetype">
                <h3>{result.emoji || '🎭'} Archetype</h3>
                <p className="value">{result.archetype || 'Unknown'}</p>
              </div>
              {result.tagline && (
                <div className="description">
                  <p><em>"{result.tagline}"</em></p>
                </div>
              )}
              {result.dominant_traits && result.dominant_traits.length > 0 && (
                <div className="traits">
                  <h3>Dominant Traits</h3>
                  <ul>
                    {result.dominant_traits.map((trait: string, idx: number) => (
                      <li key={idx}>{trait}</li>
                    ))}
                  </ul>
                </div>
              )}
              {result.strengths && result.strengths.length > 0 && (
                <div className="strengths">
                  <h3>💪 Strengths</h3>
                  <ul>
                    {result.strengths.map((strength: string, idx: number) => (
                      <li key={idx}>{strength}</li>
                    ))}
                  </ul>
                </div>
              )}
              {result.blind_spots && result.blind_spots.length > 0 && (
                <div className="blind-spots">
                  <h3>⚠️ Blind Spots</h3>
                  <ul>
                    {result.blind_spots.map((spot: string, idx: number) => (
                      <li key={idx}>{spot}</li>
                    ))}
                  </ul>
                </div>
              )}
              {result.relationship_tips && result.relationship_tips.length > 0 && (
                <div className="tips">
                  <h3>💡 Relationship Tips</h3>
                  <ul>
                    {result.relationship_tips.map((tip: string, idx: number) => (
                      <li key={idx}>{tip}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default PersonalityProfiler;
