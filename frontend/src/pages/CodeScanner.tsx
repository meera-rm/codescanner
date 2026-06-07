import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/PathPages.css';

interface ScanFinding {
  file: string;
  line: number;
  severity: 'CRITICAL' | 'ERROR' | 'WARNING' | 'INFO';
  type: string;
  message: string;
}

export const CodeScanner: React.FC = () => {
  const navigate = useNavigate();
  const [directoryPath, setDirectoryPath] = useState('');
  const [loading, setLoading] = useState(false);
  const [findings, setFindings] = useState<ScanFinding[]>([]);
  const [error, setError] = useState('');
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleBrowse = () => {
    fileInputRef.current?.click();
  };

  const handleDirectorySelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const firstFile = files[0];
      const path = (firstFile as any).webkitRelativePath || firstFile.name;
      const directoryName = path.split('/')[0] || path;
      setDirectoryPath(directoryName);
    }
  };

  const handleScan = async () => {
    if (!directoryPath.trim()) {
      setError('Please enter a directory path');
      return;
    }

    setLoading(true);
    setError('');
    setFindings([]);
    try {
      const response = await fetch('/api/v1/scanner/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: directoryPath })
      });

      if (!response.ok) throw new Error('Scan failed');
      const data = await response.json();
      setFindings(data.findings || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const severityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return '#e74c3c';
      case 'ERROR': return '#e67e22';
      case 'WARNING': return '#f39c12';
      default: return '#95a5a6';
    }
  };

  return (
    <div className="path-page">
      <header className="page-header">
        <button className="back-btn" onClick={() => navigate('/')}>← Back</button>
        <h1>🔍 Code Scanner</h1>
        <p>Scan code for security issues, complexity, and quality metrics</p>
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
            onClick={handleScan}
            disabled={loading || !directoryPath.trim()}
            className="analyze-btn"
          >
            {loading ? 'Scanning...' : 'Scan'}
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {findings.length > 0 && (
          <div className="result-section">
            <h2>Scan Results ({findings.length} findings)</h2>
            <div className="findings-list">
              {findings.map((finding, idx) => (
                <div
                  key={idx}
                  className="finding-item"
                  style={{ borderLeftColor: severityColor(finding.severity) }}
                >
                  <div className="finding-header">
                    <span className="severity" style={{ background: severityColor(finding.severity) }}>
                      {finding.severity}
                    </span>
                    <span className="type">{finding.type}</span>
                    <span className="file">{finding.file}:{finding.line}</span>
                  </div>
                  <p className="message">{finding.message}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {!loading && findings.length === 0 && directoryPath && (
          <div className="empty-state">
            <p>Click "Scan" to start analyzing your code</p>
          </div>
        )}
      </main>
    </div>
  );
};

export default CodeScanner;
