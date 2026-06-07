/**
 * Team Comparison Component
 *
 * Displays multiple teams side-by-side with their CAQI scores
 * and personality archetypes for comparison
 */

import React, { useState } from 'react';
import CAQIRadarChart from './CAQIRadarChart';
import './TeamComparison.css';

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

interface TeamComparisonProps {
  /** Array of teams to display and compare */
  teams: Team[];
  /** Show loading spinner while data fetches (default: false) */
  loading?: boolean;
  /** Error message to display if data fetch fails (default: undefined) */
  error?: string;
}

export const TeamComparison: React.FC<TeamComparisonProps> = ({
  teams,
  loading = false,
  error
}) => {
  const [selectedTeam, setSelectedTeam] = useState<string | null>(
    teams.length > 0 ? teams[0].team_id : null
  );

  if (loading) {
    return (
      <div className="team-comparison-container">
        <div className="loading">Loading team data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="team-comparison-container">
        <div className="error">{error}</div>
      </div>
    );
  }

  if (!teams || teams.length === 0) {
    return (
      <div className="team-comparison-container">
        <div className="empty-state">No teams found</div>
      </div>
    );
  }

  return (
    <div className="team-comparison-container">
      <h1>Team Comparison</h1>

      <div className="team-selector">
        <div className="selector-label">Select teams to view:</div>
        <div className="team-pills">
          {teams.map((team) => (
            <button
              key={team.team_id}
              className={`team-pill ${selectedTeam === team.team_id ? 'active' : ''}`}
              onClick={() => setSelectedTeam(team.team_id)}
            >
              {team.team_name}
              <span className="caqi-badge">{team.overall_caqi}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="comparison-grid">
        {/* Left side: Detailed view of selected team */}
        {selectedTeam && (
          <div className="selected-team-detail">
            {teams
              .filter((team) => team.team_id === selectedTeam)
              .map((team) => (
                <div key={team.team_id}>
                  <CAQIRadarChart
                    teamName={team.team_name}
                    archetype={team.personality_archetype}
                    dimensions={team.dimensions}
                    overallCAQI={team.overall_caqi}
                  />
                  <div className="team-metadata">
                    <div className="metadata-item">
                      <span className="label">Team Size</span>
                      <span className="value">{team.member_count} members</span>
                    </div>
                    <div className="metadata-item">
                      <span className="label">Last Updated</span>
                      <span className="value">
                        {new Date(team.calculated_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        )}

        {/* Right side: Comparison table */}
        <div className="comparison-table-container">
          <h3>Team Metrics</h3>
          <table className="comparison-table">
            <thead>
              <tr>
                <th>Team</th>
                <th>Archetype</th>
                <th>CAQI</th>
                <th>Security</th>
                <th>Complexity</th>
                <th>Docs</th>
                <th>Testing</th>
                <th>Members</th>
              </tr>
            </thead>
            <tbody>
              {teams.map((team) => (
                <tr
                  key={team.team_id}
                  className={`team-row ${selectedTeam === team.team_id ? 'active' : ''}`}
                  onClick={() => setSelectedTeam(team.team_id)}
                >
                  <td className="team-name-cell">
                    <span className="team-name-text">{team.team_name}</span>
                  </td>
                  <td className="archetype-cell">
                    <span className="archetype-text">{team.personality_archetype}</span>
                  </td>
                  <td className="caqi-cell">
                    <span className={`caqi-score caqi-${getCAQILevel(team.overall_caqi)}`}>
                      {team.overall_caqi}
                    </span>
                  </td>
                  <td className="dimension-cell">
                    <span className="dimension-score">{Math.round(team.dimensions.security)}</span>
                  </td>
                  <td className="dimension-cell">
                    <span className="dimension-score">{Math.round(team.dimensions.complexity)}</span>
                  </td>
                  <td className="dimension-cell">
                    <span className="dimension-score">{Math.round(team.dimensions.documentation)}</span>
                  </td>
                  <td className="dimension-cell">
                    <span className="dimension-score">{Math.round(team.dimensions.testing)}</span>
                  </td>
                  <td className="member-cell">{team.member_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Summary statistics */}
      <div className="summary-stats">
        <div className="stat-card">
          <span className="stat-label">Average CAQI</span>
          <span className="stat-value">
            {Math.round(teams.reduce((sum, t) => sum + t.overall_caqi, 0) / teams.length)}
          </span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Highest CAQI</span>
          <span className="stat-value">
            {Math.max(...teams.map((t) => t.overall_caqi))}
          </span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Total Members</span>
          <span className="stat-value">
            {teams.reduce((sum, t) => sum + t.member_count, 0)}
          </span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Teams</span>
          <span className="stat-value">{teams.length}</span>
        </div>
      </div>
    </div>
  );
};

// Helper function to determine CAQI level
function getCAQILevel(caqi: number): string {
  if (caqi >= 400) return 'excellent';
  if (caqi >= 350) return 'good';
  if (caqi >= 300) return 'fair';
  return 'poor';
}

export default TeamComparison;
