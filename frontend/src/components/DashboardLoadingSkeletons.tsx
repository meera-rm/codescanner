/**
 * Loading Skeleton Screens
 * Show placeholder content while data loads
 */

import React from 'react';
import '../styles/loading-skeletons.css';

export const GradeBoxSkeleton: React.FC = () => (
  <div className="grade-box skeleton">
    <div className="skeleton-text-sm" />
    <div className="skeleton-heading-lg" />
    <div className="skeleton-text-sm" />
  </div>
);

export const ProgressBoxSkeleton: React.FC = () => (
  <div className="progress-box skeleton">
    <div className="skeleton-text-sm" />
    <div className="skeleton-badges" />
    <div className="skeleton-bar" />
    <div className="skeleton-text-sm" />
  </div>
);

export const ImprovementBoxSkeleton: React.FC = () => (
  <div className="improvement-box skeleton">
    <div className="skeleton-text-sm" />
    <div className="skeleton-heading-lg" />
    <div className="skeleton-text-sm" />
  </div>
);

export const ChartSkeleton: React.FC = () => (
  <div className="chart-container skeleton">
    <div className="skeleton-text-md" style={{ marginBottom: '1rem' }} />
    <div className="skeleton-chart" />
  </div>
);

export const MetricsCardSkeleton: React.FC = () => (
  <div className="metric-card skeleton">
    <div className="skeleton-text-sm" />
    <div className="skeleton-heading-md" />
  </div>
);

export const TimelineItemSkeleton: React.FC = () => (
  <div className="timeline-item skeleton">
    <div className="timeline-number-skeleton" />
    <div className="timeline-content-skeleton">
      <div className="skeleton-badges" style={{ marginBottom: '0.5rem' }} />
      <div className="skeleton-text-md" style={{ marginBottom: '0.5rem' }} />
      <div className="skeleton-text-sm" />
    </div>
  </div>
);

export const DashboardSkeleton: React.FC = () => (
  <div className="iteration-dashboard">
    <div className="dashboard-header">
      <div>
        <div className="skeleton-text-lg" style={{ marginBottom: '0.5rem' }} />
        <div className="skeleton-text-sm" style={{ width: '200px' }} />
      </div>
    </div>

    <div className="grade-section">
      <GradeBoxSkeleton />
      <ProgressBoxSkeleton />
      <ImprovementBoxSkeleton />
    </div>

    <div className="charts-section">
      <ChartSkeleton />
      <ChartSkeleton />
      <ChartSkeleton />
    </div>

    <div className="metrics-section">
      <div className="skeleton-text-lg" style={{ marginBottom: '1.5rem' }} />
      <div className="metrics-grid">
        <MetricsCardSkeleton />
        <MetricsCardSkeleton />
        <MetricsCardSkeleton />
        <MetricsCardSkeleton />
      </div>
    </div>

    <div className="timeline-section">
      <div className="skeleton-text-lg" style={{ marginBottom: '2rem' }} />
      <div className="timeline">
        <TimelineItemSkeleton />
        <TimelineItemSkeleton />
        <TimelineItemSkeleton />
      </div>
    </div>
  </div>
);

export default DashboardSkeleton;
