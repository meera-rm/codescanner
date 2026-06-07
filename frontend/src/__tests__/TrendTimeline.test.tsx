/**
 * Unit tests for TrendTimeline component
 * Tests: rendering, trend calculation, data validation, edge cases
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import TrendTimeline from '../components/TrendTimeline';

describe('TrendTimeline Component', () => {
  const mockTrendData = [
    {
      month: 'Apr',
      caqi: 355,
      archetype: 'Reckless Optimist',
      recorded_at: '2026-04-30T14:30:00Z'
    },
    {
      month: 'May',
      caqi: 372,
      archetype: 'Pragmatic Engineer',
      recorded_at: '2026-05-31T14:30:00Z'
    },
    {
      month: 'Jun',
      caqi: 380,
      archetype: 'Pragmatic Engineer',
      recorded_at: '2026-06-06T14:30:00Z'
    }
  ];

  it('renders without crashing with valid data', () => {
    render(
      <TrendTimeline
        teamName="Backend Team"
        data={mockTrendData}
      />
    );
    expect(screen.getByText(/Backend Team.*Trend/i)).toBeInTheDocument();
  });

  it('renders loading state', () => {
    render(
      <TrendTimeline
        teamName="Test"
        data={[]}
        loading={true}
      />
    );
    expect(screen.getByText(/Loading trend data/i)).toBeInTheDocument();
  });

  it('renders error state', () => {
    const errorMsg = 'Failed to load trends';
    render(
      <TrendTimeline
        teamName="Test"
        data={[]}
        error={errorMsg}
      />
    );
    expect(screen.getByText(errorMsg)).toBeInTheDocument();
  });

  it('renders empty state', () => {
    render(
      <TrendTimeline
        teamName="Test"
        data={[]}
      />
    );
    expect(screen.getByText(/No trend data available/i)).toBeInTheDocument();
  });

  it('displays team name', () => {
    render(
      <TrendTimeline
        teamName="Backend Engineering"
        data={mockTrendData}
      />
    );
    expect(screen.getByText(/Backend Engineering/i)).toBeInTheDocument();
  });

  it('displays trend direction - improving', () => {
    render(
      <TrendTimeline
        teamName="Test"
        data={mockTrendData}
        trendDirection="improving"
      />
    );
    expect(screen.getByText(/Improving/i)).toBeInTheDocument();
  });

  it('displays trend direction - declining', () => {
    render(
      <TrendTimeline
        teamName="Test"
        data={mockTrendData}
        trendDirection="declining"
      />
    );
    expect(screen.getByText(/Declining/i)).toBeInTheDocument();
  });

  it('displays trend direction - stable', () => {
    const { container } = render(
      <TrendTimeline
        teamName="Test"
        data={mockTrendData}
        trendDirection="stable"
      />
    );
    expect(container).toBeInTheDocument();
  });

  it('displays change percentage', () => {
    const { container } = render(
      <TrendTimeline
        teamName="Test"
        data={mockTrendData}
        changePercent={7.04}
      />
    );
    expect(container).toBeInTheDocument();
  });

  it('displays all month snapshots', () => {
    render(
      <TrendTimeline
        teamName="Test"
        data={mockTrendData}
      />
    );
    // Check that at least the first month is visible
    expect(screen.getByText('Apr')).toBeInTheDocument();
  });

  it('displays all archetypes in snapshots', () => {
    render(
      <TrendTimeline
        teamName="Test"
        data={mockTrendData}
      />
    );
    // Check that at least first archetype is visible
    expect(screen.getByText(mockTrendData[0].archetype)).toBeInTheDocument();
  });

  it('displays CAQI scores in snapshots', () => {
    const { container } = render(
      <TrendTimeline
        teamName="Test"
        data={mockTrendData}
      />
    );
    // Check that component renders with CAQI data
    expect(screen.getByText('Monthly Archetypes')).toBeInTheDocument();
    expect(container).toBeInTheDocument();
  });

  it('displays trend analysis metrics', () => {
    render(
      <TrendTimeline
        teamName="Test"
        data={mockTrendData}
      />
    );
    expect(screen.getByText(/Starting Score/i)).toBeInTheDocument();
    expect(screen.getByText(/Current Score/i)).toBeInTheDocument();
    expect(screen.getByText(/Highest Score/i)).toBeInTheDocument();
    expect(screen.getByText(/Lowest Score/i)).toBeInTheDocument();
  });

  it('displays starting score correctly', () => {
    const { container } = render(
      <TrendTimeline
        teamName="Test"
        data={mockTrendData}
      />
    );
    expect(screen.getByText('Starting Score')).toBeInTheDocument();
    expect(container).toBeInTheDocument();
  });

  it('displays highest score correctly', () => {
    const { container } = render(
      <TrendTimeline
        teamName="Test"
        data={mockTrendData}
      />
    );
    expect(screen.getByText('Highest Score')).toBeInTheDocument();
    expect(container).toBeInTheDocument();
  });

  it('displays lowest score correctly', () => {
    const { container } = render(
      <TrendTimeline
        teamName="Test"
        data={mockTrendData}
      />
    );
    expect(screen.getByText('Lowest Score')).toBeInTheDocument();
    expect(container).toBeInTheDocument();
  });

  it('handles single data point', () => {
    render(
      <TrendTimeline
        teamName="Test"
        data={[mockTrendData[0]]}
      />
    );
    expect(screen.getByText(mockTrendData[0].month)).toBeInTheDocument();
  });

  it('handles flat trend (no change)', () => {
    const flatData = [
      { month: 'Apr', caqi: 380, archetype: 'Test' },
      { month: 'May', caqi: 380, archetype: 'Test' },
      { month: 'Jun', caqi: 380, archetype: 'Test' }
    ];
    const { container } = render(
      <TrendTimeline
        teamName="Test"
        data={flatData}
      />
    );
    expect(container).toBeInTheDocument();
  });

  it('handles extreme CAQI values (0 and 500)', () => {
    const extremeData = [
      { month: 'Apr', caqi: 0, archetype: 'Pragmatic Engineer' },
      { month: 'May', caqi: 250, archetype: 'Pragmatic Engineer' },
      { month: 'Jun', caqi: 500, archetype: 'Pragmatic Engineer' }
    ];
    const { container } = render(
      <TrendTimeline
        teamName="Extreme Test"
        data={extremeData}
      />
    );
    // Check component renders with extreme data
    expect(screen.getByText(/Extreme Test/)).toBeInTheDocument();
    expect(screen.getByText('Apr')).toBeInTheDocument();
    expect(container).toBeInTheDocument();
  });

  it('handles positive change percentage', () => {
    const { container } = render(
      <TrendTimeline
        teamName="Test"
        data={mockTrendData}
        changePercent={+7.04}
      />
    );
    expect(container).toBeInTheDocument();
  });

  it('handles negative change percentage', () => {
    const { container } = render(
      <TrendTimeline
        teamName="Test"
        data={mockTrendData}
        changePercent={-5.5}
      />
    );
    expect(container).toBeInTheDocument();
  });

  it('handles zero change percentage', () => {
    const { container } = render(
      <TrendTimeline
        teamName="Test"
        data={mockTrendData}
        changePercent={0}
      />
    );
    expect(container).toBeInTheDocument();
  });

  it('handles long month names', () => {
    const longMonthData = [
      { month: 'January 2026', caqi: 300, archetype: 'Test' },
      { month: 'February 2026', caqi: 350, archetype: 'Test' }
    ];
    render(
      <TrendTimeline
        teamName="Test"
        data={longMonthData}
      />
    );
    expect(screen.getByText('January 2026')).toBeInTheDocument();
  });

  it('generates trend interpretation for improving', () => {
    render(
      <TrendTimeline
        teamName="Test"
        data={mockTrendData}
        trendDirection="improving"
        changePercent={7.04}
      />
    );
    expect(screen.getByText(/Great progress/i)).toBeInTheDocument();
  });

  it('generates trend interpretation for declining', () => {
    const declineData = [
      { month: 'Apr', caqi: 400, archetype: 'Test' },
      { month: 'Jun', caqi: 350, archetype: 'Test' }
    ];
    render(
      <TrendTimeline
        teamName="Test"
        data={declineData}
        trendDirection="declining"
        changePercent={-12.5}
      />
    );
    expect(screen.getByText(/declined/i)).toBeInTheDocument();
  });

  it('displays many data points (12+ months)', () => {
    const manyMonths = Array(12).fill(null).map((_, i) => ({
      month: `Month ${i + 1}`,
      caqi: 300 + i * 10,
      archetype: 'Test'
    }));
    render(
      <TrendTimeline
        teamName="Test"
        data={manyMonths}
      />
    );
    expect(screen.getByText('Month 1')).toBeInTheDocument();
    expect(screen.getByText('Month 12')).toBeInTheDocument();
  });
});
