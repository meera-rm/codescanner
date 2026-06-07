/**
 * Trend Timeline Component
 *
 * Displays CAQI trend over 90 days with line chart
 * and personality archetype evolution
 */

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import './TrendTimeline.css';

interface TrendEntry {
  month: string;
  caqi: number;
  archetype: string;
  recorded_at?: string;
}

interface TrendTimelineProps {
  /** Team name to display as header */
  teamName: string;
  /** Array of CAQI trend snapshots (limited to 12 months max). Format: month label and CAQI score */
  data: TrendEntry[];
  /** Trend direction indicator: 'improving' (>5%), 'declining' (<-5%), or 'stable' (default: 'stable') */
  trendDirection?: 'improving' | 'stable' | 'declining';
  /** Percentage change from first to last CAQI score (default: 0) */
  changePercent?: number;
  /** Show loading spinner while data fetches (default: false) */
  loading?: boolean;
  /** Error message to display if data fetch fails (default: undefined) */
  error?: string;
}

export const TrendTimeline: React.FC<TrendTimelineProps> = ({
  teamName,
  data,
  trendDirection = 'stable',
  changePercent = 0,
  loading = false,
  error
}) => {
  if (loading) {
    return (
      <div className="trend-timeline-container">
        <div className="loading">Loading trend data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="trend-timeline-container">
        <div className="error">{error}</div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="trend-timeline-container">
        <div className="empty-state">No trend data available</div>
      </div>
    );
  }

  // Limit to 12 months max for performance (prevents chart rendering lag with large datasets)
  const limitedData = data.slice(-12);

  // Format data for chart
  const chartData = limitedData.map((entry) => ({
    name: entry.month,
    CAQI: entry.caqi,
    archetype: entry.archetype
  }));

  // Determine trend color
  const trendColor =
    trendDirection === 'improving'
      ? '#4ECDC4'
      : trendDirection === 'declining'
        ? '#FF6B6B'
        : '#FFE66D';

  // Generate aria-label for screen readers
  const currentScore = limitedData[limitedData.length - 1]?.caqi || 0;
  const startingScore = limitedData[0]?.caqi || 0;
  const chartLabel = `${teamName} CAQI Trend Chart. Starting score: ${startingScore}, Current score: ${currentScore}, Trend: ${trendDirection}`;

  return (
    <div className="trend-timeline-container">
      <div className="trend-header">
        <h2>{teamName} - 3-Month Trend</h2>
        <div className="trend-summary">
          <div className={`trend-indicator ${trendDirection}`}>
            <span className="trend-arrow">
              {trendDirection === 'improving'
                ? '↗'
                : trendDirection === 'declining'
                  ? '↘'
                  : '→'}
            </span>
            <span className="trend-label">
              {trendDirection === 'improving'
                ? 'Improving'
                : trendDirection === 'declining'
                  ? 'Declining'
                  : 'Stable'}
            </span>
          </div>
          <div className="change-percent">
            <span className={`percent-value ${trendDirection}`}>
              {changePercent > 0 ? '+' : ''}
              {changePercent.toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      <div role="img" aria-label={chartLabel}>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e8e8e8" />
          <XAxis
            dataKey="name"
            tick={{ fill: '#666', fontSize: 12 }}
            stroke="#ccc"
          />
          <YAxis
            domain={[0, 500]}
            tick={{ fill: '#666', fontSize: 12 }}
            stroke="#ccc"
            label={{ value: 'CAQI Score', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: `2px solid ${trendColor}`,
              borderRadius: '8px',
              padding: '10px'
            }}
            formatter={(value) => [`CAQI: ${value}`, 'Score']}
            labelFormatter={(label) => `Month: ${label}`}
          />
          <Legend />
          <ReferenceLine y={300} stroke="#ddd" strokeDasharray="5 5" label="Fair (300)" />
          <ReferenceLine y={350} stroke="#ddd" strokeDasharray="5 5" label="Good (350)" />
          <ReferenceLine y={400} stroke="#ddd" strokeDasharray="5 5" label="Excellent (400)" />
          <Line
            type="monotone"
            dataKey="CAQI"
            stroke={trendColor}
            dot={{ fill: trendColor, r: 6 }}
            activeDot={{ r: 8 }}
            strokeWidth={3}
            isAnimationActive={true}
          />
        </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="month-snapshots">
        <h3>Monthly Archetypes</h3>
        <div className="snapshot-grid">
          {limitedData.map((entry, index) => (
            <div key={index} className="snapshot-card">
              <div className="snapshot-month">{entry.month}</div>
              <div className="snapshot-archetype">{entry.archetype}</div>
              <div className="snapshot-caqi">
                <span className="caqi-label">CAQI</span>
                <span className={`caqi-score caqi-${getCAQILevel(entry.caqi)}`}>
                  {entry.caqi}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="trend-insights">
        <h3>Trend Analysis</h3>
        <div className="insights-grid">
          <div className="insight-card">
            <span className="insight-label">Starting Score</span>
            <span className="insight-value">{limitedData[0]?.caqi || 0}</span>
          </div>
          <div className="insight-card">
            <span className="insight-label">Current Score</span>
            <span className="insight-value">{limitedData[limitedData.length - 1]?.caqi || 0}</span>
          </div>
          <div className="insight-card">
            <span className="insight-label">Highest Score</span>
            <span className="insight-value">
              {Math.max(...limitedData.map((d) => d.caqi))}
            </span>
          </div>
          <div className="insight-card">
            <span className="insight-label">Lowest Score</span>
            <span className="insight-value">
              {Math.min(...limitedData.map((d) => d.caqi))}
            </span>
          </div>
        </div>
      </div>

      <div className="trend-interpretation">
        <p>
          {getTrendInterpretation(
            trendDirection,
            changePercent,
            limitedData[limitedData.length - 1]?.archetype || ''
          )}
        </p>
      </div>
    </div>
  );
};

function getCAQILevel(caqi: number): string {
  if (caqi >= 400) return 'excellent';
  if (caqi >= 350) return 'good';
  if (caqi >= 300) return 'fair';
  return 'poor';
}

function getTrendInterpretation(
  direction: string,
  changePercent: number,
  currentArchetype: string
): string {
  if (direction === 'improving') {
    return `Great progress! Your team's CAQI has improved by ${changePercent.toFixed(1)}% over the past 3 months.
            As a ${currentArchetype}, focus on maintaining this momentum by continuing your current practices.`;
  } else if (direction === 'declining') {
    return `Your team's CAQI has declined by ${Math.abs(changePercent).toFixed(1)}% over the past 3 months.
            Consider reviewing what changed and identifying areas where the ${currentArchetype} archetype could use improvement.`;
  } else {
    return `Your team's CAQI has remained relatively stable over the past 3 months.
            As a ${currentArchetype}, ensure you're consistently maintaining your engineering standards and look for opportunities to improve.`;
  }
}

export default TrendTimeline;
