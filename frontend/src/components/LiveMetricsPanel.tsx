import React from 'react';
import { SnippetAnalysisResult } from '../hooks/useLiveCodeAnalysis';

interface LiveMetricsPanelProps {
  analysis: SnippetAnalysisResult | null;
  isAnalyzing: boolean;
  error: string | null;
  theme?: 'light' | 'dark';
}

const CircleGauge: React.FC<{
  label: string;
  value: number;
  max: number;
  icon: string;
  color: string;
  subtext?: string;
}> = ({ label, value, max, icon, color, subtext }) => {
  const percentage = max > 0 ? (value / max) * 100 : 0;
  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '8px'
    }}>
      <div style={{ fontSize: '20px' }}>{icon}</div>
      <svg width="100" height="100" viewBox="0 0 100 100">
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke="#e0e0e0"
          strokeWidth="8"
        />
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.3s ease' }}
        />
        <text
          x="50"
          y="50"
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize="20"
          fontWeight="600"
          fill={color}
        >
          {value}
        </text>
      </svg>
      <div style={{ fontSize: '12px', fontWeight: 600, textAlign: 'center' }}>
        {label}
      </div>
      {subtext && (
        <div style={{ fontSize: '10px', color: '#999999' }}>
          {subtext}
        </div>
      )}
    </div>
  );
};

export const LiveMetricsPanel: React.FC<LiveMetricsPanelProps> = ({
  analysis,
  isAnalyzing,
  error,
  theme = 'light'
}) => {
  const bgColor = theme === 'light' ? '#f9f9f9' : '#1f1f1f';
  const panelBg = theme === 'light' ? '#ffffff' : '#2a2a2a';
  const borderColor = theme === 'light' ? '#e0e0e0' : '#333333';
  const textColor = theme === 'light' ? '#2c2c2c' : '#ffffff';
  const mutedColor = theme === 'light' ? '#666666' : '#cccccc';

  if (error) {
    return (
      <div style={{
        padding: '24px',
        backgroundColor: bgColor,
        borderRadius: '4px',
        border: `1px solid ${borderColor}`,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '300px'
      }}>
        <div style={{ fontSize: '24px', marginBottom: '12px' }}>⚠️</div>
        <div style={{ fontSize: '12px', color: '#e74c3c', fontWeight: 600 }}>
          Analysis Error
        </div>
        <div style={{ fontSize: '11px', color: mutedColor, marginTop: '8px', textAlign: 'center' }}>
          {error}
        </div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div style={{
        padding: '24px',
        backgroundColor: bgColor,
        borderRadius: '4px',
        border: `1px solid ${borderColor}`,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '300px'
      }}>
        <div style={{ fontSize: '32px', marginBottom: '12px' }}>📊</div>
        <div style={{ fontSize: '12px', color: mutedColor, fontWeight: 600 }}>
          No Code to Analyze
        </div>
        <div style={{ fontSize: '11px', color: '#999999', marginTop: '8px' }}>
          Paste or type code in the editor to see metrics
        </div>
      </div>
    );
  }

  const qualityColor = analysis.quality_score >= 80 ? '#27ae60' :
                        analysis.quality_score >= 60 ? '#f39c12' : '#e74c3c';

  const complexityTotal = analysis.complexity.high + analysis.complexity.medium + analysis.complexity.low;

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '16px',
      backgroundColor: bgColor,
      borderRadius: '4px',
      padding: '16px'
    }}>
      {/* Top Metrics - 3 Gauges */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr 1fr',
        gap: '16px',
        padding: '12px',
        backgroundColor: panelBg,
        borderRadius: '4px',
        border: `1px solid ${borderColor}`
      }}>
        <CircleGauge
          icon="⭐"
          label="Quality"
          value={analysis.quality_score}
          max={100}
          color={qualityColor}
          subtext={`${analysis.quality_score}/100`}
        />
        <CircleGauge
          icon="📈"
          label="Complexity"
          value={complexityTotal}
          max={10}
          color={complexityTotal > 5 ? '#e74c3c' : complexityTotal > 2 ? '#f39c12' : '#27ae60'}
          subtext={`${complexityTotal} issues`}
        />
        <CircleGauge
          icon="🔒"
          label="Security"
          value={analysis.security_issues}
          max={5}
          color={analysis.security_issues > 2 ? '#e74c3c' : analysis.security_issues > 0 ? '#f39c12' : '#27ae60'}
          subtext={`${analysis.security_issues} issues`}
        />
      </div>

      {/* Summary Stats */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '12px',
        padding: '12px',
        backgroundColor: panelBg,
        borderRadius: '4px',
        border: `1px solid ${borderColor}`
      }}>
        <div style={{
          padding: '8px',
          backgroundColor: theme === 'light' ? '#f5f5f5' : '#1f1f1f',
          borderRadius: '3px'
        }}>
          <div style={{ fontSize: '10px', color: '#999999', marginBottom: '4px' }}>
            Code Length
          </div>
          <div style={{ fontSize: '14px', fontWeight: 600, color: textColor }}>
            {analysis.code_length} chars
          </div>
        </div>
        <div style={{
          padding: '8px',
          backgroundColor: theme === 'light' ? '#f5f5f5' : '#1f1f1f',
          borderRadius: '3px'
        }}>
          <div style={{ fontSize: '10px', color: '#999999', marginBottom: '4px' }}>
            Total Issues
          </div>
          <div style={{ fontSize: '14px', fontWeight: 600, color: textColor }}>
            {analysis.total_issues}
          </div>
        </div>
      </div>

      {/* Complexity Breakdown */}
      <div style={{
        padding: '12px',
        backgroundColor: panelBg,
        borderRadius: '4px',
        border: `1px solid ${borderColor}`
      }}>
        <div style={{
          fontSize: '11px',
          fontWeight: 600,
          color: textColor,
          marginBottom: '8px',
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          📊 Complexity Breakdown
        </div>
        <div style={{
          display: 'flex',
          gap: '12px',
          fontSize: '12px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            <div style={{
              width: '12px',
              height: '12px',
              backgroundColor: '#e74c3c',
              borderRadius: '2px'
            }} />
            <span>High: <strong>{analysis.complexity.high}</strong></span>
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            <div style={{
              width: '12px',
              height: '12px',
              backgroundColor: '#f39c12',
              borderRadius: '2px'
            }} />
            <span>Medium: <strong>{analysis.complexity.medium}</strong></span>
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            <div style={{
              width: '12px',
              height: '12px',
              backgroundColor: '#27ae60',
              borderRadius: '2px'
            }} />
            <span>Low: <strong>{analysis.complexity.low}</strong></span>
          </div>
        </div>
      </div>

      {/* Issues List */}
      {analysis.findings && analysis.findings.length > 0 && (
        <div style={{
          padding: '12px',
          backgroundColor: panelBg,
          borderRadius: '4px',
          border: `1px solid ${borderColor}`
        }}>
          <div style={{
            fontSize: '11px',
            fontWeight: 600,
            color: textColor,
            marginBottom: '8px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            🔍 Top Issues ({analysis.findings.length})
          </div>
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '6px',
            maxHeight: '200px',
            overflowY: 'auto'
          }}>
            {analysis.findings.slice(0, 5).map((finding, idx) => (
              <div
                key={idx}
                style={{
                  padding: '6px 8px',
                  backgroundColor: theme === 'light' ? '#f5f5f5' : '#1f1f1f',
                  borderRadius: '3px',
                  borderLeft: `3px solid ${
                    finding.severity === 'high' ? '#e74c3c' :
                    finding.severity === 'medium' ? '#f39c12' : '#27ae60'
                  }`,
                  fontSize: '10px'
                }}>
                <div style={{ fontWeight: 600, color: textColor, marginBottom: '2px' }}>
                  Line {finding.line}: {finding.type}
                </div>
                <div style={{ color: mutedColor }}>
                  {finding.message}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {isAnalyzing && (
        <div style={{
          padding: '12px',
          backgroundColor: '#f0f8ff',
          borderRadius: '4px',
          border: '1px solid #b3d9ff',
          fontSize: '12px',
          color: '#0066cc',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span>⏳</span>
          <span>Analyzing your code...</span>
        </div>
      )}
    </div>
  );
};

export default LiveMetricsPanel;
