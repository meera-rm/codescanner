import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/PathPages.css';

export const PersonalityProfiler: React.FC = () => {
  const navigate = useNavigate();
  const [directoryPath, setDirectoryPath] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

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

      if (!response.ok) throw new Error('Analysis failed');
      const data = await response.json();

      // Poll for results
      let jobResult = null;
      let attempts = 0;
      while (attempts < 30) {
        const statusResponse = await fetch(`/api/v1/creative-suite/${data.job_id}`);
        if (statusResponse.ok) {
          jobResult = await statusResponse.json();
          break;
        }
        await new Promise(r => setTimeout(r, 1000));
        attempts++;
      }

      if (jobResult) {
        setResult(jobResult.personality);
      } else {
        setError('Analysis timed out');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
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
          <input
            id="path"
            type="text"
            placeholder="e.g., /path/to/your/project"
            value={directoryPath}
            onChange={(e) => setDirectoryPath(e.target.value)}
            disabled={loading}
          />
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
                <h3>Archetype</h3>
                <p className="value">{result.archetype || 'Unknown'}</p>
              </div>
              <div className="description">
                <h3>Description</h3>
                <p>{result.description || 'No description available'}</p>
              </div>
              {result.traits && (
                <div className="traits">
                  <h3>Traits</h3>
                  <ul>
                    {result.traits.map((trait: string, idx: number) => (
                      <li key={idx}>{trait}</li>
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
