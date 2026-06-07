/**
 * CAQI Engineering Culture Dashboard
 *
 * Main page orchestrating all Path I components:
 * - Radar chart visualization
 * - Team comparison view
 * - Trend timeline analysis
 */

import React, { useState, useEffect } from 'react';
import CAQIRadarChart from '../components/CAQIRadarChart';
import TeamComparison from '../components/TeamComparison';
import TrendTimeline from '../components/TrendTimeline';
import '../styles/CAQIDashboard.css';

interface Team {
  team_id: string;
  team_name: string;
  dimensions: {
    security: number;
    complexity: number;
    documentation: number;
    testing: number;
    dependencies: number;
    maintainability: number;
  };
  overall_caqi: number;
  personality_archetype: string;
  member_count: number;
  calculated_at: string;
}

interface TrendData {
  month: string;
  caqi: number;
  archetype: string;
  recorded_at?: string;
}

type ViewMode = 'radar' | 'comparison' | 'trend';

export const CAQIDashboard: React.FC = () => {
  const [activeView, setActiveView] = useState<ViewMode>('comparison');
  const [teams, setTeams] = useState<Team[]>([]);
  const [trendData, setTrendData] = useState<TrendData[]>([]);
  const [selectedTeamId, setSelectedTeamId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Fetch teams on component mount
  useEffect(() => {
    // TODO: Implement real API fetch in production
    // const fetchTeams = async () => {
    //   setLoading(true);
    //   setError(undefined);
    //   try {
    //     const response = await fetch('/api/v1/caqi/team/backend-team/comparison?team_ids=frontend-team,data-team');
    //     if (!response.ok) throw new Error('Failed to fetch teams');
    //     const data = await response.json();
    //     setTeams(data);
    //     if (data.length > 0) {
    //       setSelectedTeamId(data[0].team_id);
    //     }
    //   } catch (err) {
    //     setError(err instanceof Error ? err.message : 'Failed to fetch teams');
    //   } finally {
    //     setLoading(false);
    //   }
    // };

    // For now, use mock data for demo
    const mockTeams: Team[] = [
      {
        team_id: 'backend-team',
        team_name: 'Backend Engineering',
        dimensions: {
          security: 85,
          complexity: 72,
          documentation: 80,
          testing: 88,
          dependencies: 65,
          maintainability: 78
        },
        overall_caqi: 380,
        personality_archetype: 'Pragmatic Engineer',
        member_count: 4,
        calculated_at: new Date().toISOString()
      },
      {
        team_id: 'frontend-team',
        team_name: 'Frontend Engineering',
        dimensions: {
          security: 78,
          complexity: 65,
          documentation: 72,
          testing: 75,
          dependencies: 60,
          maintainability: 70
        },
        overall_caqi: 340,
        personality_archetype: 'Cautious Perfectionist',
        member_count: 3,
        calculated_at: new Date().toISOString()
      },
      {
        team_id: 'data-team',
        team_name: 'Data Engineering',
        dimensions: {
          security: 80,
          complexity: 75,
          documentation: 68,
          testing: 82,
          dependencies: 70,
          maintainability: 75
        },
        overall_caqi: 365,
        personality_archetype: 'Pragmatic Engineer',
        member_count: 3,
        calculated_at: new Date().toISOString()
      }
    ];
    setTeams(mockTeams);
    setSelectedTeamId(mockTeams[0].team_id);
  }, []);

  // Fetch trend data when selected team changes
  useEffect(() => {
    if (!selectedTeamId) return;

    const fetchTrendData = async () => {
      setLoading(true);
      try {
        // In production, fetch from API
        // const response = await fetch(`/api/v1/caqi/team/${selectedTeamId}/monthly-snapshots?start_year=2026&start_month=4&num_months=3`);
        // const data = await response.json();
        // setTrendData(data.snapshots);

        // For now, use mock data
        const mockTrend: TrendData[] = [
          {
            month: 'Apr',
            caqi: 355,
            archetype: 'Reckless Optimist'
          },
          {
            month: 'May',
            caqi: 372,
            archetype: 'Pragmatic Engineer'
          },
          {
            month: 'Jun',
            caqi: 380,
            archetype: 'Pragmatic Engineer'
          }
        ];
        setTrendData(mockTrend);
      } catch (err) {
        console.error('Failed to fetch trend data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchTrendData();
  }, [selectedTeamId]);

  const selectedTeam = teams.find((t) => t.team_id === selectedTeamId);

  return (
    <div className="caqi-dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>Engineering Culture Dashboard</h1>
          <p className="subtitle">
            Track team CAQI scores, personality archetypes, and cultural trends
          </p>
        </div>
      </header>

      <nav className="view-tabs">
        <button
          className={`tab-button ${activeView === 'comparison' ? 'active' : ''}`}
          onClick={() => setActiveView('comparison')}
        >
          Team Comparison
        </button>
        <button
          className={`tab-button ${activeView === 'radar' ? 'active' : ''}`}
          onClick={() => setActiveView('radar')}
        >
          Team Details
        </button>
        <button
          className={`tab-button ${activeView === 'trend' ? 'active' : ''}`}
          onClick={() => setActiveView('trend')}
        >
          Trends
        </button>
      </nav>

      <main className="dashboard-content">
        {activeView === 'comparison' && (
          <TeamComparison teams={teams} loading={loading} />
        )}

        {activeView === 'radar' && selectedTeam && (
          <div className="detail-view">
            <CAQIRadarChart
              teamName={selectedTeam.team_name}
              archetype={selectedTeam.personality_archetype}
              dimensions={selectedTeam.dimensions}
              overallCAQI={selectedTeam.overall_caqi}
            />
          </div>
        )}

        {activeView === 'trend' && selectedTeam && (
          <div className="trend-view">
            <TrendTimeline
              teamName={selectedTeam.team_name}
              data={trendData}
              trendDirection={getTrendDirection(trendData)}
              changePercent={calculateChange(trendData)}
              loading={loading}
            />
          </div>
        )}
      </main>

      <footer className="dashboard-footer">
        <p>
          Powered by CODEPULSE AI • Last updated:{' '}
          {selectedTeam?.calculated_at ? new Date(selectedTeam.calculated_at).toLocaleDateString() : 'N/A'}
        </p>
      </footer>
    </div>
  );
};

function getTrendDirection(data: TrendData[]): 'improving' | 'stable' | 'declining' {
  if (data.length < 2) return 'stable';
  const first = data[0].caqi;
  const last = data[data.length - 1].caqi;
  const change = ((last - first) / first) * 100;
  if (change > 5) return 'improving';
  if (change < -5) return 'declining';
  return 'stable';
}

function calculateChange(data: TrendData[]): number {
  if (data.length < 2) return 0;
  const first = data[0].caqi;
  const last = data[data.length - 1].caqi;
  return ((last - first) / first) * 100;
}

export default CAQIDashboard;
