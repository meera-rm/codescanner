/**
 * CAQI Gauge Component - displays team CAQI score as interactive gauge
 *
 * Shows:
 * - Overall CAQI (0-500 scale)
 * - Color-coded performance (red/yellow/green)
 * - Individual dimension scores (0-100 each)
 */

import React, { useMemo, useCallback } from 'react';
import {
  CAQI_MAX,
  DIMENSION_LABELS,
  DIMENSIONS,
  getGrade,
  getScoreColor,
  formatDate,
  validateCaqiScore,
  validateDimensionScore,
} from '../constants/caqi';

interface CAQIDimensions {
  security: number;
  complexity: number;
  documentation: number;
  testing: number;
  dependencies: number;
  maintainability: number;
}

interface CAQIGaugeProps {
  teamId: string;
  overallCaqi: number;
  dimensions: CAQIDimensions;
  calculatedAt?: string;
  onDimensionClick?: (dimension: string) => void;
}

export const CAQIGauge: React.FC<CAQIGaugeProps> = ({
  teamId,
  overallCaqi,
  dimensions,
  calculatedAt,
  onDimensionClick,
}) => {
  // Validate props
  if (!validateCaqiScore(overallCaqi)) {
    console.warn(`Invalid CAQI score: ${overallCaqi}. Expected 0-${CAQI_MAX}`);
  }

  Object.values(dimensions).forEach((score) => {
    if (!validateDimensionScore(score)) {
      console.warn(`Invalid dimension score: ${score}. Expected 0-100`);
    }
  });

  const gauge = useMemo(() => ({
    color: getScoreColor(overallCaqi),
    grade: getGrade(overallCaqi),
    percentage: (overallCaqi / CAQI_MAX) * 100,
  }), [overallCaqi]);

  const formattedDate = useMemo(() =>
    calculatedAt ? formatDate(calculatedAt) : null,
    [calculatedAt]
  );

  const dimensionArray = useMemo(() =>
    DIMENSIONS.map((dim) => ({
      key: dim,
      label: DIMENSION_LABELS[dim],
      value: dimensions[dim],
    })),
    [dimensions]
  );

  const handleDimensionClick = useCallback((dimension: string) => {
    onDimensionClick?.(dimension);
  }, [onDimensionClick]);

  const handleDimensionKeyDown = useCallback((e: React.KeyboardEvent, dimension: string) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onDimensionClick?.(dimension);
    }
  }, [onDimensionClick]);

  return (
    <div className="caqi-gauge" data-testid="caqi-gauge">
      <div className="gauge-container">
        <div className="gauge-header">
          <h2>{teamId}</h2>
          {formattedDate && <span className="timestamp">{formattedDate}</span>}
        </div>

        <div className="gauge-display">
          <div className="gauge-circle" style={{ background: `conic-gradient(${gauge.color} 0% ${gauge.percentage}%, #e5e7eb ${gauge.percentage}% 100%)` }}>
            <div className="gauge-inner">
              <div className="gauge-value">{overallCaqi}</div>
              <div className="gauge-max">/{CAQI_MAX}</div>
              <div className="gauge-grade">{gauge.grade}</div>
            </div>
          </div>
        </div>

        <div className="dimensions-grid">
          {dimensionArray.map((dim) => (
            <div
              key={dim.key}
              className="dimension-card"
              onClick={() => handleDimensionClick(dim.key)}
              onKeyDown={(e) => handleDimensionKeyDown(e, dim.key)}
              role="button"
              tabIndex={0}
              aria-label={`${dim.label}: ${dim.value}`}
              data-testid={`dimension-${dim.key}`}
            >
              <div className="dimension-label">{dim.label}</div>
              <div className="dimension-value">{dim.value}</div>
              <div className="dimension-bar">
                <div
                  className="dimension-fill"
                  style={{
                    width: `${Math.min(dim.value, 100)}%`,
                    backgroundColor: getScoreColor(dim.value, 100),
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      <style jsx>{`
        .caqi-gauge {
          width: 100%;
          max-width: 600px;
          padding: 24px;
          background: white;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .gauge-container {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }

        .gauge-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .gauge-header h2 {
          margin: 0;
          font-size: 20px;
          font-weight: 600;
        }

        .timestamp {
          font-size: 12px;
          color: #6b7280;
        }

        .gauge-display {
          display: flex;
          justify-content: center;
        }

        .gauge-circle {
          width: 200px;
          height: 200px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          position: relative;
        }

        .gauge-inner {
          width: 160px;
          height: 160px;
          background: white;
          border-radius: 50%;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 4px;
        }

        .gauge-value {
          font-size: 32px;
          font-weight: 700;
          color: #1f2937;
        }

        .gauge-max {
          font-size: 12px;
          color: #6b7280;
        }

        .gauge-grade {
          font-size: 24px;
          font-weight: 600;
          color: #3b82f6;
        }

        .dimensions-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
          gap: 12px;
        }

        .dimension-card {
          padding: 12px;
          background: #f9fafb;
          border-radius: 8px;
          cursor: pointer;
          transition: background-color 200ms;
        }

        .dimension-card:hover {
          background: #f3f4f6;
        }

        .dimension-label {
          font-size: 12px;
          font-weight: 500;
          color: #6b7280;
          margin-bottom: 4px;
        }

        .dimension-value {
          font-size: 18px;
          font-weight: 600;
          color: #1f2937;
          margin-bottom: 8px;
        }

        .dimension-bar {
          width: 100%;
          height: 6px;
          background: #e5e7eb;
          border-radius: 3px;
          overflow: hidden;
        }

        .dimension-fill {
          height: 100%;
          transition: width 300ms ease;
        }
      `}</style>
    </div>
  );
};

export default CAQIGauge;
