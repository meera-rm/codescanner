import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/PathPages.css';

export const OnboardingProfiles: React.FC = () => {
  const navigate = useNavigate();
  const [directoryPath, setDirectoryPath] = useState('');
  const [teamName, setTeamName] = useState('');
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState('');
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

  const handleGenerate = async () => {
    if (!directoryPath.trim()) {
      setError('Please enter a directory path');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const response = await fetch('/api/v1/onboarding/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          path: directoryPath,
          team_name: teamName || 'Engineering Team'
        })
      });

      if (!response.ok) throw new Error('Profile generation failed');
      const data = await response.json();
      setProfile(data.profile || data.content || JSON.stringify(data, null, 2));
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
        <h1>👥 Onboarding Profiles</h1>
        <p>Generate onboarding guides and team profiles for new hires</p>
      </header>

      <main className="page-content">
        <div className="input-section">
          <div className="input-group">
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
          </div>
          <div className="input-group">
            <label htmlFor="team">Team Name (optional):</label>
            <input
              id="team"
              type="text"
              placeholder="e.g., Backend Engineering"
              value={teamName}
              onChange={(e) => setTeamName(e.target.value)}
              disabled={loading}
            />
          </div>
          <button
            onClick={handleGenerate}
            disabled={loading || !directoryPath.trim()}
            className="analyze-btn"
          >
            {loading ? 'Generating...' : 'Generate Profile'}
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {profile && (
          <div className="result-section">
            <h2>Onboarding Profile</h2>
            <div className="profile-content">
              <pre>{profile}</pre>
            </div>
            <button
              onClick={() => {
                const element = document.createElement('a');
                element.setAttribute('href', `data:text/markdown;charset=utf-8,${encodeURIComponent(profile)}`);
                element.setAttribute('download', 'onboarding-profile.md');
                element.style.display = 'none';
                document.body.appendChild(element);
                element.click();
                document.body.removeChild(element);
              }}
              className="download-btn"
            >
              📥 Download Profile
            </button>
          </div>
        )}
      </main>
    </div>
  );
};

export default OnboardingProfiles;
