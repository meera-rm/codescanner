/**
 * Developer Contributions Component - shows developer impact rankings
 *
 * Features:
 * - Developer impact scores sorted by contribution
 * - Per-dimension contribution breakdown
 * - Color-coded positive/negative contributions
 * - Expandable details for each developer
 */

import React, { useState, useMemo, useCallback } from 'react';
import {
  DIMENSIONS,
  DIMENSION_LABELS,
  CONTRIBUTION_THRESHOLDS,
} from '../constants/caqi';
import './caqi-components.css';

interface DimensionContribution {
  developerScore: number;
  teamAvg: number;
  contribution: number;
}

interface Developer {
  developerId: string;
  teamId: string;
  contributions: {
    [key in typeof DIMENSIONS[number]]?: DimensionContribution;
  };
  overallContribution: number;
}

interface DeveloperContributionsProps {
  teamId: string;
  developers: Developer[];
  period?: number;
  onDeveloperClick?: (developerId: string) => void;
}

const CONTRIBUTION_BAR_SCALE = 5; // Scale factor for contribution bar width

export const DeveloperContributions: React.FC<DeveloperContributionsProps> = ({
  teamId,
  developers,
  period = 30,
  onDeveloperClick,
}) => {
  const [expandedDeveloper, setExpandedDeveloper] = useState<string | null>(null);

  const sortedDevelopers = useMemo(
    () => [...developers].sort((a, b) => Math.abs(b.overallContribution) - Math.abs(a.overallContribution)),
    [developers]
  );

  const getContributionColor = useCallback((contribution: number): string => {
    if (contribution > CONTRIBUTION_THRESHOLDS.highPositive) return '#22c55e'; // Green
    if (contribution > CONTRIBUTION_THRESHOLDS.minorPositive) return '#84cc16'; // Light green
    if (contribution > CONTRIBUTION_THRESHOLDS.minorNegative) return '#f97316'; // Orange
    return '#ef4444'; // Red
  }, []);

  const getImpactLabel = useCallback((contribution: number): string => {
    const abs = Math.abs(contribution);
    if (abs > 10) return 'High Impact';
    if (abs > 5) return 'Medium Impact';
    if (abs > 0) return 'Low Impact';
    return 'No Impact';
  }, []);

  const handleDeveloperClick = useCallback((developerId: string) => {
    setExpandedDeveloper((prev) => (prev === developerId ? null : developerId));
    onDeveloperClick?.(developerId);
  }, [onDeveloperClick]);

  const handleDeveloperKeyDown = useCallback((e: React.KeyboardEvent, developerId: string) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleDeveloperClick(developerId);
    }
  }, [handleDeveloperClick]);

  return (
    <div className="developer-contributions" data-testid="developer-contributions">
      <div className="component-header">
        <h2>{teamId} - Developer Contributions</h2>
        <span className="period-label">({period} days)</span>
      </div>

      <div className="developers-list">
        {sortedDevelopers.length === 0 ? (
          <div className="no-data">No developer data available</div>
        ) : (
          sortedDevelopers.map((dev) => (
            <div key={dev.developerId} className="developer-card" data-testid={`dev-card-${dev.developerId}`}>
              <div
                className="developer-header"
                onClick={() => handleDeveloperClick(dev.developerId)}
                onKeyDown={(e) => handleDeveloperKeyDown(e, dev.developerId)}
                role="button"
                tabIndex={0}
                aria-expanded={expandedDeveloper === dev.developerId}
                aria-label={`${dev.developerId} - ${getImpactLabel(dev.overallContribution)}`}
              >
                <div className="developer-info">
                  <h3 className="developer-name">{dev.developerId}</h3>
                  <span className="impact-label" style={{ color: getContributionColor(dev.overallContribution) }}>
                    {getImpactLabel(dev.overallContribution)}
                  </span>
                </div>

                <div className="developer-score">
                  <div className="overall-contribution" style={{ color: getContributionColor(dev.overallContribution) }}>
                    {dev.overallContribution > 0 ? '+' : ''}{dev.overallContribution.toFixed(2)}
                  </div>
                  <span className="expand-icon" aria-hidden="true">{expandedDeveloper === dev.developerId ? '▼' : '▶'}</span>
                </div>
              </div>

              {expandedDeveloper === dev.developerId && (
                <div className="developer-details" role="region" aria-label={`Details for ${dev.developerId}`}>
                  <div className="dimensions-breakdown">
                    {DIMENSIONS.map((dim) => {
                      const contrib = dev.contributions[dim];
                      if (!contrib) return null;

                      const barWidth = Math.min(Math.abs(contrib.contribution) * CONTRIBUTION_BAR_SCALE, 100);

                      return (
                        <div key={dim} className="dimension-contribution" data-testid={`dim-${dev.developerId}-${dim}`}>
                          <div className="dimension-header">
                            <span className="dimension-name">{DIMENSION_LABELS[dim]}</span>
                            <span className="dimension-scores">
                              {contrib.developerScore.toFixed(1)} (team avg: {contrib.teamAvg.toFixed(1)})
                            </span>
                          </div>
                          <div className="contribution-bar">
                            <div
                              className="contribution-fill"
                              style={{
                                width: `${barWidth}%`,
                                backgroundColor: getContributionColor(contrib.contribution),
                                marginLeft: contrib.contribution < 0 ? 'auto' : '0',
                              }}
                              data-testid={`contrib-bar-${dim}`}
                            />
                          </div>
                          <span className="contribution-value">
                            {contrib.contribution > 0 ? '+' : ''}{contrib.contribution.toFixed(2)}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default DeveloperContributions;
