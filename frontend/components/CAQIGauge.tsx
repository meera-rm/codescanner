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
import './caqi-components.css';

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
    <section className="caqi-gauge" data-testid="caqi-gauge" aria-label="CAQI Score Card">
      <div className="gauge-container" role="region" aria-labelledby="gauge-heading">
        <div className="gauge-header">
          <h2 id="gauge-heading" aria-level={2}>{teamId}</h2>
          {formattedDate && <span className="timestamp" aria-label={`Last calculated: ${formattedDate}`}>{formattedDate}</span>}
        </div>

        <div className="gauge-display" role="progressbar" aria-valuenow={overallCaqi} aria-valuemin={0} aria-valuemax={CAQI_MAX} aria-label={`Overall CAQI score: ${overallCaqi} out of ${CAQI_MAX}`}>
          <div className="gauge-circle" style={{ background: `conic-gradient(${gauge.color} 0% ${gauge.percentage}%, #e5e7eb ${gauge.percentage}% 100%)` }} aria-hidden="true">
            <div className="gauge-inner" aria-hidden="true">
              <div className="gauge-value" aria-hidden="true">{overallCaqi}</div>
              <div className="gauge-max" aria-hidden="true">/{CAQI_MAX}</div>
              <div className="gauge-grade" aria-label={`Grade: ${gauge.grade}`}>{gauge.grade}</div>
            </div>
          </div>
        </div>

        <div className="dimensions-grid" role="grid" aria-label="Dimension scores">
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
    </section>
  );
};

export default CAQIGauge;
