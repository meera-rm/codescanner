import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/Home.css';

interface HomePath {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  icon: string;
  color: string;
  featured?: boolean;
}

export const Home: React.FC = () => {
  const paths: HomePath[] = [
    {
      id: 'personality',
      title: 'Personality Profiler',
      subtitle: 'Path G',
      description: 'Analyze your codebase and discover its personality archetype',
      icon: '🎭',
      color: '#9b59b6'
    },
    {
      id: 'letter',
      title: 'Inheritance Letter',
      subtitle: 'Path H',
      description: 'Generate a legacy letter for your code to future developers',
      icon: '💌',
      color: '#e74c3c'
    },
    {
      id: 'caqi',
      title: 'CAQI Dashboard',
      subtitle: 'Path I',
      description: 'Track team CAQI scores, personality archetypes, and cultural trends',
      icon: '📊',
      color: '#3498db'
    },
    {
      id: 'scanner',
      title: 'Code Scanner',
      subtitle: 'Path K',
      description: 'Scan code for security issues, complexity, and quality metrics',
      icon: '🔍',
      color: '#27ae60'
    },
    {
      id: 'onboarding',
      title: 'Onboarding Profiles',
      subtitle: 'Path J',
      description: 'Generate onboarding guides and team profiles for new hires',
      icon: '👥',
      color: '#f39c12'
    },
    /* {
      id: 'dashboard',
      title: 'Analytics Dashboard',
      subtitle: 'Main Hub',
      description: 'View real-time metrics, health monitoring, and AI insights',
      icon: '📈',
      color: '#e74c3c',
      featured: true
    } */
  ];

  return (
    <div className="home-container">
      <header className="home-header">
        <h1>🚀 CodePulse AI</h1>
        <p>Code Intelligence Platform</p>
        <p className="subtitle">Choose an analysis path to get started</p>
      </header>

      <main className="paths-grid">
        {paths.map((path) => (
          <Link
            key={path.id}
            to={`/${path.id}`}
            className={`path-card ${path.featured ? 'featured' : ''}`}
          >
            <div className="path-icon" style={{ '--icon-color': path.color } as React.CSSProperties}>
              {path.icon}
            </div>
            <div className="path-content">
              <h2>{path.title}</h2>
              <p className="path-subtitle">{path.subtitle}</p>
              <p className="path-description">{path.description}</p>
            </div>
            <div className="path-arrow">→</div>
          </Link>
        ))}
      </main>

      <footer className="home-footer">
        <p>Powered by CODEPULSE AI • Multiple analysis paths, one platform</p>
      </footer>
    </div>
  );
};

export default Home;
