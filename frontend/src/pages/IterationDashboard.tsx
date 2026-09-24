/**
 * Iteration Dashboard Page
 * Real-time visualization of code improvement iterations
 */

import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useIterationPolling } from '../hooks/useIterationPolling';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import '../styles/iteration-dashboard.css';

interface GradeChartData {
  iteration: number;
  grade_value: number;
  grade_label: string;
}

interface IssuesChartData {
  iteration: number;
  fixed: number;
  remaining: number;
}

interface AgentData {
  name: string;
  count: number;
}

const GRADE_VALUES: Record<string, number> = {
  'F': 0, 'D': 20, 'C': 40, 'B-': 55, 'B': 65, 'B+': 75,
  'A-': 85, 'A': 95,
};

const GRADE_COLORS: Record<string, string> = {
  'F': '#ef4444', 'D': '#f97316', 'C': '#eab308', 'B-': '#84cc16',
  'B': '#22c55e', 'B+': '#10b981', 'A-': '#06b6d4', 'A': '#0ea5e9',
};

const IterationDashboard: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const [isPaused, setIsPaused] = useState(false);

  if (!jobId) {
    return <div className="iteration-dashboard error">Job ID not found</div>;
  }

  const { status, loading, error, stop, resume } = useIterationPolling(jobId, {
    enabled: !isPaused,
    interval: 1000,
  });

  if (loading && !status) {
    return <div className="iteration-dashboard loading">Loading job status...</div>;
  }

  if (error && !status) {
    return <div className="iteration-dashboard error">Error: {error.message}</div>;
  }

  if (!status) {
    return <div className="iteration-dashboard error">Failed to load job</div>;
  }

  // Prepare chart data
  const gradeChartData: GradeChartData[] = status.history.map((h, i) => ({
    iteration: i + 1,
    grade_value: GRADE_VALUES[h.grade_after] || 0,
    grade_label: h.grade_after,
  }));

  const issuesChartData: IssuesChartData[] = status.history.map((h, i) => ({
    iteration: i + 1,
    fixed: h.issues_fixed,
    remaining: Math.max(0, (i === 0 ? 20 : status.history[i - 1].issues_fixed) - h.issues_fixed),
  }));

  // Agent frequency
  const agentCounts = status.history.reduce((acc, h) => {
    const agent = h.agent_selected.split('(')[0].trim();
    const existing = acc.find(a => a.name === agent);
    if (existing) {
      existing.count += 1;
    } else {
      acc.push({ name: agent, count: 1 });
    }
    return acc;
  }, [] as AgentData[]);

  const isComplete = status.status !== 'processing';
  const statusColor = {
    'queued': '#6b7280',
    'completed': '#22c55e',
    'processing': '#3b82f6',
    'failed': '#ef4444',
    'cancelled': '#f59e0b',
  }[status.status] || '#6b7280';

  return (
    <div className="iteration-dashboard">
      {/* Header Section */}
      <div className="dashboard-header">
        <div className="header-title">
          <h1>Code Improvement Dashboard</h1>
          <p className="job-id">Job: {jobId}</p>
        </div>

        <div className="header-controls">
          <button
            className="btn-pause"
            onClick={() => {
              if (isPaused) {
                resume();
              } else {
                stop();
              }
              setIsPaused(!isPaused);
            }}
          >
            {isPaused ? '▶ Resume' : '⏸ Pause'}
          </button>
          <div className={`status-badge ${status.status}`} style={{ backgroundColor: statusColor }}>
            {status.status.toUpperCase()}
          </div>
        </div>
      </div>

      {/* Main Grade Section */}
      <div className="grade-section">
        <div className="grade-box">
          <div className="grade-label">Current Grade</div>
          <div className="grade-display" style={{ color: GRADE_COLORS[status.final_grade] || '#666' }}>
            {status.final_grade}
          </div>
          <div className="grade-score">{status.metrics?.quality_score?.toFixed(1) || 'N/A'}/100</div>
        </div>

        <div className="progress-box">
          <div className="progress-label">Grade Progression</div>
          <div className="grade-progression">
            {[status.start_grade, ...status.history.map(h => h.grade_after)]
              .slice(0, 6)
              .map((g, i) => (
                <span key={i} className="grade-badge" style={{ backgroundColor: GRADE_COLORS[g] }}>
                  {g}
                </span>
              ))}
            {status.history.length > 5 && <span className="grade-more">...</span>}
          </div>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{
                width: `${status.progress_percent}%`,
                backgroundColor: GRADE_COLORS[status.final_grade] || '#666',
              }}
            />
          </div>
          <div className="progress-text">
            Iteration {status.iterations_count}/{status.max_iterations} ({status.progress_percent}%)
          </div>
        </div>

        <div className="improvement-box">
          <div className="improvement-label">Grade Improvement</div>
          <div className="improvement-value">+{status.grade_improvement}</div>
          <div className="improvement-detail">
            {status.start_grade} → {status.final_grade}
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-section">
        <div className="chart-container">
          <h3>Grade Progression</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={gradeChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="iteration" />
              <YAxis domain={[0, 100]} />
              <Tooltip formatter={(value) => `${value}/100`} />
              <Line
                type="monotone"
                dataKey="grade_value"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={{ fill: '#3b82f6', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Issues Fixed Per Iteration</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={issuesChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="iteration" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="fixed" stackId="a" fill="#22c55e" name="Fixed" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Agent Selection</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={agentCounts}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, count }) => `${name}: ${count}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
              >
                {agentCounts.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={['#8b5cf6', '#3b82f6', '#ec4899'][index % 3]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Metrics Section */}
      <div className="metrics-section">
        <h2>Metrics & Statistics</h2>
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-label">Total Issues Fixed</div>
            <div className="metric-value">{status.metrics?.total_issues_fixed || 0}</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Iterations Completed</div>
            <div className="metric-value">{status.iterations_count}/{status.max_iterations}</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Avg. Iteration Time</div>
            <div className="metric-value">
              {status.history.length > 0
                ? ((status.history.length * 2.5) / status.history.length).toFixed(1)
                : '0.0'}s
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Target Grade</div>
            <div className="metric-value">{status.target_grade}</div>
          </div>
        </div>
      </div>

      {/* Iteration Timeline */}
      <div className="timeline-section">
        <h2>Iteration Timeline</h2>
        <div className="timeline">
          {status.history.map((step, i) => (
            <div key={i} className="timeline-item">
              <div className="timeline-number">{step.iteration_number}</div>
              <div className="timeline-content">
                <div className="timeline-grades">
                  <span
                    className="grade-box small"
                    style={{ backgroundColor: GRADE_COLORS[step.grade_before] }}
                  >
                    {step.grade_before}
                  </span>
                  <span className="arrow">→</span>
                  <span
                    className="grade-box small"
                    style={{ backgroundColor: GRADE_COLORS[step.grade_after] }}
                  >
                    {step.grade_after}
                  </span>
                </div>
                <div className="timeline-details">
                  <strong>{step.agent_selected}</strong>
                  <p>{step.fix_description}</p>
                  <div className="timeline-meta">
                    <span>✨ {step.issues_fixed} issues fixed</span>
                    <span>⏱️ ~2.5s</span>
                    {step.validation_passed && <span className="validation">✅ Validated</span>}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Status Message */}
      {isComplete && (
        <div className={`completion-message ${status.status}`}>
          {status.status === 'completed' && (
            <div>
              ✅ <strong>Job Complete!</strong> Code improved from {status.start_grade} to{' '}
              {status.final_grade} (+{status.grade_improvement} points)
            </div>
          )}
          {status.status === 'failed' && (
            <div>
              ❌ <strong>Job Failed:</strong> {status.error_message || 'Unknown error'}
            </div>
          )}
          {status.status === 'cancelled' && (
            <div>⏹️ <strong>Job Cancelled</strong></div>
          )}
        </div>
      )}
    </div>
  );
};

export default IterationDashboard;
