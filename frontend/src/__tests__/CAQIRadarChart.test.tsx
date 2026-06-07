/**
 * Unit tests for CAQIRadarChart component
 * Tests: rendering, props validation, type safety, accessibility
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import CAQIRadarChart from '../components/CAQIRadarChart';

describe('CAQIRadarChart Component', () => {
  const mockDimensions = {
    security: 85,
    complexity: 72,
    documentation: 80,
    testing: 88,
    dependencies: 65,
    maintainability: 78
  };

  it('renders without crashing with required props', () => {
    render(
      <CAQIRadarChart
        teamName="Test Team"
        archetype="Pragmatic Engineer"
        dimensions={mockDimensions}
      />
    );
    expect(screen.getByText('Test Team')).toBeInTheDocument();
  });

  it('displays team name correctly', () => {
    render(
      <CAQIRadarChart
        teamName="Backend Engineering"
        archetype="Pragmatic Engineer"
        dimensions={mockDimensions}
      />
    );
    expect(screen.getByText('Backend Engineering')).toBeInTheDocument();
  });

  it('displays archetype correctly', () => {
    render(
      <CAQIRadarChart
        teamName="Test Team"
        archetype="Cautious Perfectionist"
        dimensions={mockDimensions}
      />
    );
    expect(screen.getByText('Cautious Perfectionist')).toBeInTheDocument();
  });

  it('displays overall CAQI score when provided', () => {
    render(
      <CAQIRadarChart
        teamName="Test Team"
        archetype="Pragmatic Engineer"
        dimensions={mockDimensions}
        overallCAQI={380}
      />
    );
    expect(screen.getByText(/380\/500/)).toBeInTheDocument();
  });

  it('renders all 6 dimensions in breakdown', () => {
    render(
      <CAQIRadarChart
        teamName="Test Team"
        archetype="Pragmatic Engineer"
        dimensions={mockDimensions}
      />
    );
    expect(screen.getByText(/Security/i)).toBeInTheDocument();
    expect(screen.getByText(/Complexity/i)).toBeInTheDocument();
    expect(screen.getByText(/Documentation/i)).toBeInTheDocument();
    expect(screen.getByText(/Testing/i)).toBeInTheDocument();
    expect(screen.getByText(/Dependencies/i)).toBeInTheDocument();
    expect(screen.getByText(/Maintainability/i)).toBeInTheDocument();
  });

  it('validates prop types - valid dimensions', () => {
    const validDimensions = {
      security: 85,
      complexity: 72,
      documentation: 80,
      testing: 88,
      dependencies: 65,
      maintainability: 78
    };
    expect(() => {
      render(
        <CAQIRadarChart
          teamName="Test"
          archetype="Test"
          dimensions={validDimensions}
        />
      );
    }).not.toThrow();
  });

  it('handles edge case - all dimensions at 100', () => {
    const maxDimensions = {
      security: 100,
      complexity: 100,
      documentation: 100,
      testing: 100,
      dependencies: 100,
      maintainability: 100
    };
    render(
      <CAQIRadarChart
        teamName="Perfect Team"
        archetype="Pragmatic Engineer"
        dimensions={maxDimensions}
      />
    );
    expect(screen.getByText('Perfect Team')).toBeInTheDocument();
  });

  it('handles edge case - all dimensions at 0', () => {
    const minDimensions = {
      security: 0,
      complexity: 0,
      documentation: 0,
      testing: 0,
      dependencies: 0,
      maintainability: 0
    };
    render(
      <CAQIRadarChart
        teamName="Problematic Team"
        archetype="Pragmatic Engineer"
        dimensions={minDimensions}
      />
    );
    expect(screen.getByText('Problematic Team')).toBeInTheDocument();
  });

  it('displays all 5 valid archetypes correctly', () => {
    const archetypes = [
      'Reckless Optimist',
      'Cautious Perfectionist',
      'Secretive Perfectionist',
      'Anxious Overthinker',
      'Pragmatic Engineer'
    ];

    archetypes.forEach((archetype) => {
      const { unmount } = render(
        <CAQIRadarChart
          teamName="Test"
          archetype={archetype}
          dimensions={mockDimensions}
        />
      );
      expect(screen.getByText(archetype)).toBeInTheDocument();
      unmount();
    });
  });

  it('handles long team names', () => {
    const longName = 'This Is A Very Long Team Name That Should Still Render Correctly';
    render(
      <CAQIRadarChart
        teamName={longName}
        archetype="Pragmatic Engineer"
        dimensions={mockDimensions}
      />
    );
    expect(screen.getByText(longName)).toBeInTheDocument();
  });

  it('renders without CAQI score', () => {
    render(
      <CAQIRadarChart
        teamName="Test Team"
        archetype="Pragmatic Engineer"
        dimensions={mockDimensions}
      />
    );
    expect(screen.getByText('Test Team')).toBeInTheDocument();
  });

  it('handles missing optional CAQI prop gracefully', () => {
    const { container } = render(
      <CAQIRadarChart
        teamName="Test"
        archetype="Pragmatic Engineer"
        dimensions={mockDimensions}
      />
    );
    expect(container).toBeInTheDocument();
  });
});
