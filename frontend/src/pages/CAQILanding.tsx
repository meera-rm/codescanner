import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/PathPages.css';

export const CAQILanding: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="path-page">
      <header className="page-header">
        <button className="back-btn" onClick={() => navigate('/')}>← Back</button>
        <h1>📊 Code Air Quality Index</h1>
        <p>Choose how you want to analyze code quality</p>
      </header>

      <main className="page-content">
        <div className="caqi-landing-grid">
          {/* CAQI Analyzer Card */}
          <div
            className="caqi-card"
            onClick={() => navigate('/caqi/analyzer')}
            style={{
              cursor: 'pointer',
              padding: '40px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              textAlign: 'center',
              transition: 'transform 0.3s ease, box-shadow 0.3s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-8px)';
              e.currentTarget.style.boxShadow = '0 20px 40px rgba(102, 126, 234, 0.4)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
            <h2 style={{ fontSize: '24px', marginBottom: '12px' }}>CAQI Analyzer</h2>
            <p style={{ marginBottom: '20px', fontSize: '14px', opacity: 0.95 }}>
              Analyze a single codebase and get real metrics
            </p>
            <div style={{
              fontSize: '12px',
              opacity: 0.85,
              lineHeight: '1.8',
              textAlign: 'left',
              display: 'inline-block'
            }}>
              <p>✅ Real codebase analysis</p>
              <p>📈 6 health dimensions</p>
              <p>⚙️ Complexity, Security, Smells</p>
              <p>📚 Docs, Duplication, Coupling</p>
            </div>
            <button style={{
              marginTop: '24px',
              padding: '12px 32px',
              backgroundColor: 'rgba(255, 255, 255, 0.2)',
              color: 'white',
              border: '2px solid white',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 'bold',
              transition: 'all 0.3s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'white';
              e.currentTarget.style.color = '#667eea';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
              e.currentTarget.style.color = 'white';
            }}
            >
              Analyze Project →
            </button>
          </div>

          {/* CAQI Dashboard Card
          <div
            className="caqi-card"
            onClick={() => navigate('/caqi/dashboard')}
            style={{
              cursor: 'pointer',
              padding: '40px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
              color: 'white',
              textAlign: 'center',
              transition: 'transform 0.3s ease, box-shadow 0.3s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-8px)';
              e.currentTarget.style.boxShadow = '0 20px 40px rgba(245, 87, 108, 0.4)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>👥</div>
            <h2 style={{ fontSize: '24px', marginBottom: '12px' }}>CAQI Dashboard</h2>
            <p style={{ marginBottom: '20px', fontSize: '14px', opacity: 0.95 }}>
              Compare multiple teams and track trends over time
            </p>
            <div style={{
              fontSize: '12px',
              opacity: 0.85,
              lineHeight: '1.8',
              textAlign: 'left',
              display: 'inline-block'
            }}>
              <p>👥 Team comparison view</p>
              <p>📊 Radar chart visualization</p>
              <p>📈 Trend timeline analysis</p>
              <p>🎯 Team personality archetypes</p>
            </div>
            <button style={{
              marginTop: '24px',
              padding: '12px 32px',
              backgroundColor: 'rgba(255, 255, 255, 0.2)',
              color: 'white',
              border: '2px solid white',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 'bold',
              transition: 'all 0.3s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'white';
              e.currentTarget.style.color = '#f5576c';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
              e.currentTarget.style.color = 'white';
            }}
            >
              View Dashboard →
            </button>
          </div>
          */}
        </div>

        {/* Info Section */}
        <div style={{
          marginTop: '60px',
          padding: '30px',
          backgroundColor: '#f5f5f5',
          borderRadius: '8px',
          borderLeft: '4px solid #667eea'
        }}>
          <h3>About CAQI</h3>
          <p>
            The Code Air Quality Index (CAQI) is an EPA-style health score for your codebase,
            ranging from 0-500. It combines metrics across six dimensions to give you a comprehensive
            view of code quality health.
          </p>
          <p style={{ marginTop: '12px' }}>
            <strong>🔍 Analyzer:</strong> Perfect for quickly assessing a single project's health.
          </p>
          <p style={{ marginTop: '8px' }}>
            <strong>👥 Dashboard:</strong> Ideal for organizations tracking multiple teams' code quality
            metrics and trends over time.
          </p>
        </div>
      </main>

      <style>{`
        .caqi-landing-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
          gap: 30px;
          margin: 40px 0;
        }

        .caqi-card {
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        @media (max-width: 768px) {
          .caqi-landing-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default CAQILanding;
