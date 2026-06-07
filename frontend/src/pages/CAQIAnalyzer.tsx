import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/PathPages.css';

interface CAQIData {
  score: number;
  level: string;
  color: string;
  primary_pollutant: string;
  pollutants: {
    complexity: number;
    security: number;
    smells: number;
    docs: number;
    duplication: number;
    coupling: number;
  };
}

export const CAQIAnalyzer: React.FC = () => {
  const navigate = useNavigate();
  const [directoryPath, setDirectoryPath] = useState('');
  const [loading, setLoading] = useState(false);
  const [caqi, setCAQI] = useState<CAQIData | null>(null);
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
      setError(`📁 Directory detected: "${directoryName}"`);
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
        const statusResponse = await fetch(`/api/v1/creative-suite/${data.job_id}/caqi`);

        if (statusResponse.status === 202) {
          await new Promise(r => setTimeout(r, 1000));
          attempts++;
          continue;
        }

        if (statusResponse.ok) {
          jobResult = await statusResponse.json();
          break;
        }

        const errData = await statusResponse.json().catch(() => ({}));
        throw new Error(errData.detail || `Status check failed: ${statusResponse.status}`);
      }

      if (jobResult) {
        setCAQI(jobResult);
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

  const getHealthStatus = (score: number) => {
    if (score >= 400) return { emoji: '✅', status: 'Excellent' };
    if (score >= 300) return { emoji: '🟡', status: 'Good' };
    if (score >= 200) return { emoji: '⚠️', status: 'Fair' };
    if (score >= 100) return { emoji: '❌', status: 'Poor' };
    return { emoji: '🚨', status: 'Critical' };
  };

  const pollutantName: Record<string, string> = {
    complexity: '⚙️ Complexity',
    security: '🔒 Security',
    smells: '👃 Code Smells',
    docs: '📚 Documentation',
    duplication: '📋 Duplication',
    coupling: '🔗 Coupling',
  };

  const health = caqi ? getHealthStatus(caqi.score) : null;

  return (
    <div className="path-page">
      <header className="page-header">
        <button className="back-btn" onClick={() => navigate('/caqi')}>← Back</button>
        <h1>📊 Code Air Quality Index (CAQI)</h1>
        <p>Real-time analysis of code quality across 6 health dimensions</p>
      </header>

      <main className="page-content">
        <div className="input-section">
          <label htmlFor="path">Directory Path:</label>
          <div className="input-with-button">
            <input
              id="path"
              type="text"
              placeholder="e.g., catfacts or /path/to/project"
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

        {caqi && (
          <div className="result-section">
            <h2>Code Air Quality Index Results</h2>

            {/* Main Score */}
            <div className="caqi-score-section" style={{ marginBottom: '30px' }}>
              <div className="caqi-gauge">
                <div
                  className="caqi-circle"
                  style={{
                    width: '120px',
                    height: '120px',
                    borderRadius: '50%',
                    backgroundColor: caqi.color,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto',
                    color: 'white',
                    fontWeight: 'bold',
                  }}
                >
                  <div style={{ fontSize: '12px', opacity: 0.9 }}>CAQI</div>
                  <div style={{ fontSize: '36px' }}>{caqi.score}</div>
                  <div style={{ fontSize: '11px', opacity: 0.9 }}>out of 500</div>
                </div>
              </div>

              <div style={{ textAlign: 'center', marginTop: '20px' }}>
                <p style={{ fontSize: '18px', fontWeight: 'bold' }}>
                  {health?.emoji} {caqi.level} ({health?.status})
                </p>
                <p style={{ fontSize: '14px', color: '#666' }}>
                  Primary Issue: <strong>{caqi.primary_pollutant}</strong>
                </p>
              </div>
            </div>

            {/* Pollutants Breakdown */}
            <div className="pollutants-section">
              <h3>Health Dimensions</h3>
              <div className="pollutants-grid">
                {Object.entries(caqi.pollutants).map(([key, value]) => (
                  <div key={key} className="pollutant-card">
                    <div className="pollutant-name">{pollutantName[key]}</div>
                    <div className="pollutant-bar">
                      <div
                        className="pollutant-fill"
                        style={{
                          width: `${Math.min(value, 100)}%`,
                          backgroundColor:
                            value > 75
                              ? '#d32f2f'
                              : value > 50
                              ? '#ff9800'
                              : value > 25
                              ? '#fbc02d'
                              : '#4caf50',
                          height: '100%',
                          borderRadius: '4px',
                          transition: 'width 0.3s ease',
                        }}
                      />
                    </div>
                    <div className="pollutant-value">{Math.round(value)}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Interpretation */}
            <div className="interpretation-section" style={{ marginTop: '30px' }}>
              <h3>What This Means</h3>
              {caqi.score >= 400 && (
                <p>
                  ✅ Excellent code health! Your codebase is well-maintained with good practices across all dimensions.
                  Focus on maintaining standards as the project grows.
                </p>
              )}
              {caqi.score >= 300 && caqi.score < 400 && (
                <p>
                  🟡 Good code health overall. Focus on improving the weakest dimensions to push toward excellence.
                </p>
              )}
              {caqi.score >= 200 && caqi.score < 300 && (
                <p>
                  ⚠️ Fair code health. There are significant areas for improvement. Start with the primary issue
                  ({caqi.primary_pollutant}) and work systematically through other dimensions.
                </p>
              )}
              {caqi.score >= 100 && caqi.score < 200 && (
                <p>
                  ❌ Poor code health. This codebase needs attention across multiple dimensions. Prioritize based on
                  impact and risk.
                </p>
              )}
              {caqi.score < 100 && (
                <p>
                  🚨 Critical code health issues. Immediate action needed. Consider establishing a structured
                  refactoring plan with your team.
                </p>
              )}
            </div>
          </div>
        )}
      </main>

      <style>{`
        .pollutants-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
          gap: 20px;
          margin-top: 20px;
        }

        .pollutant-card {
          padding: 15px;
          background: #f5f5f5;
          border-radius: 8px;
          border-left: 4px solid #2196f3;
        }

        .pollutant-name {
          font-weight: 600;
          margin-bottom: 10px;
          font-size: 14px;
        }

        .pollutant-bar {
          width: 100%;
          height: 24px;
          background: #e0e0e0;
          border-radius: 4px;
          overflow: hidden;
          margin-bottom: 8px;
        }

        .pollutant-value {
          font-size: 12px;
          color: #666;
          text-align: right;
        }

        .caqi-score-section {
          background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
          padding: 30px;
          border-radius: 8px;
        }

        .interpretation-section {
          background: #f9f9f9;
          padding: 20px;
          border-radius: 8px;
          border-left: 4px solid #2196f3;
        }
      `}</style>
    </div>
  );
};

export default CAQIAnalyzer;
