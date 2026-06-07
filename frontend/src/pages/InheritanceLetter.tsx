import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/PathPages.css';

export const InheritanceLetter: React.FC = () => {
  const navigate = useNavigate();
  const [directoryPath, setDirectoryPath] = useState('');
  const [loading, setLoading] = useState(false);
  const [letter, setLetter] = useState('');
  const [error, setError] = useState('');

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

      if (!response.ok) throw new Error('Analysis failed');
      const data = await response.json();

      // Poll for results
      let jobResult = null;
      let attempts = 0;
      while (attempts < 30) {
        const statusResponse = await fetch(`/api/v1/creative-suite/${data.job_id}/letter`);
        if (statusResponse.ok) {
          jobResult = await statusResponse.json();
          break;
        }
        await new Promise(r => setTimeout(r, 1000));
        attempts++;
      }

      if (jobResult) {
        setLetter(jobResult.content || JSON.stringify(jobResult));
      } else {
        setError('Generation timed out');
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
        <h1>💌 Inheritance Letter</h1>
        <p>Generate a legacy letter for your code to future developers</p>
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
            <h2>Inheritance Letter</h2>
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
