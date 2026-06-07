/**
 * CAQI Radar Chart Component
 *
 * Visualizes 6 CAQI dimensions in a radar/spider chart format
 * with personality archetype label and context
 */

import React from 'react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip
} from 'recharts';
import './CAQIRadarChart.css';

interface CAQIRadarChartProps {
  /** Team name to display as header */
  teamName: string;
  /** Personality archetype classification (Reckless Optimist, Cautious Perfectionist, etc.) */
  archetype: string;
  /** CAQI dimension scores 0-100 (security, complexity, documentation, testing, dependencies, maintainability) */
  dimensions: {
    security: number;
    complexity: number;
    documentation: number;
    testing: number;
    dependencies: number;
    maintainability: number;
  };
  /** Overall CAQI score 0-500 (optional) */
  overallCAQI?: number;
}

export const CAQIRadarChart: React.FC<CAQIRadarChartProps> = ({
  teamName,
  archetype,
  dimensions,
  overallCAQI
}) => {
  // Format data for Recharts radar chart
  const chartData = [
    { dimension: 'Security', value: Math.round(dimensions.security) },
    { dimension: 'Complexity', value: Math.round(dimensions.complexity) },
    { dimension: 'Documentation', value: Math.round(dimensions.documentation) },
    { dimension: 'Testing', value: Math.round(dimensions.testing) },
    { dimension: 'Dependencies', value: Math.round(dimensions.dependencies) },
    { dimension: 'Maintainability', value: Math.round(dimensions.maintainability) }
  ];

  // Map archetype to color
  const archetypeColors: Record<string, string> = {
    'Reckless Optimist': '#FF6B6B',
    'Cautious Perfectionist': '#4ECDC4',
    'Secretive Perfectionist': '#FFE66D',
    'Anxious Overthinker': '#95E1D3',
    'Pragmatic Engineer': '#88D498'
  };

  const color = archetypeColors[archetype] || '#8884D8';

  // Generate aria-label for screen readers
  const radarLabel = `${teamName} CAQI Radar Chart. Archetype: ${archetype}. Overall Score: ${overallCAQI ?? 'Not available'}/500`;

  return (
    <div className="caqi-radar-chart-container">
      <div className="radar-header">
        <h2 className="team-name">{teamName}</h2>
        <div className="archetype-badge" style={{ backgroundColor: color }}>
          {archetype}
        </div>
        {overallCAQI !== undefined && (
          <div className="overall-caqi">
            <span className="caqi-label">Overall CAQI</span>
            <span className="caqi-score">{overallCAQI}/500</span>
          </div>
        )}
      </div>

      <div role="img" aria-label={radarLabel}>
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <PolarGrid stroke="#E8E8E8" />
            <PolarAngleAxis
              dataKey="dimension"
              tick={{ fill: '#666', fontSize: 12 }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 100]}
              tick={{ fill: '#999', fontSize: 11 }}
            />
            <Radar
              name="Score"
              dataKey="value"
              stroke={color}
              fill={color}
              fillOpacity={0.6}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: `2px solid ${color}`,
                borderRadius: '8px',
                padding: '10px'
              }}
              formatter={(value) => `${value}/100`}
            />
            <Legend />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      <div className="dimension-breakdown">
        <div className="breakdown-grid">
          {chartData.map((item) => (
            <div key={item.dimension} className="dimension-item">
              <span className="dimension-name">{item.dimension}</span>
              <div className="dimension-bar">
                <div
                  className="dimension-fill"
                  style={{
                    width: `${item.value}%`,
                    backgroundColor: color
                  }}
                />
              </div>
              <span className="dimension-value">{item.value}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CAQIRadarChart;
