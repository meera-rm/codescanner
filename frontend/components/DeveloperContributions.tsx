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

      <style jsx>{`
        .developer-contributions {
          width: 100%;
          padding: 24px;
          background: white;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .component-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 24px;
        }

        .component-header h2 {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
        }

        .period-label {
          color: #6b7280;
          font-size: 14px;
        }

        .developers-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .developer-card {
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          overflow: hidden;
        }

        .developer-header {
          padding: 16px;
          background: #f9fafb;
          display: flex;
          justify-content: space-between;
          align-items: center;
          cursor: pointer;
          transition: background-color 200ms;
        }

        .developer-header:hover {
          background: #f3f4f6;
        }

        .developer-info {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .developer-name {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
          color: #1f2937;
        }

        .impact-label {
          font-size: 12px;
          font-weight: 500;
          padding: 4px 8px;
          background: #f3f4f6;
          border-radius: 4px;
        }

        .developer-score {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .overall-contribution {
          font-size: 18px;
          font-weight: 700;
          min-width: 80px;
          text-align: right;
        }

        .expand-icon {
          color: #9ca3af;
          font-size: 12px;
          transition: transform 200ms;
        }

        .developer-details {
          padding: 16px;
          border-top: 1px solid #e5e7eb;
          background: white;
        }

        .dimensions-breakdown {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .dimension-contribution {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .dimension-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .dimension-name {
          font-weight: 500;
          font-size: 14px;
          color: #374151;
        }

        .dimension-scores {
          font-size: 12px;
          color: #6b7280;
        }

        .contribution-bar {
          width: 100%;
          height: 20px;
          background: #e5e7eb;
          border-radius: 4px;
          overflow: hidden;
          display: flex;
        }

        .contribution-fill {
          height: 100%;
          transition: width 300ms ease;
        }

        .contribution-value {
          font-size: 12px;
          font-weight: 600;
          color: #1f2937;
        }

        .no-data {
          padding: 32px;
          text-align: center;
          color: #6b7280;
        }
      `}</style>
    </div>
  );
};

export default DeveloperContributions;
