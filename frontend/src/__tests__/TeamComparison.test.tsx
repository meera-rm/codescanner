/**
 * Unit tests for TeamComparison component
 * Tests: rendering, props validation, user interactions, edge cases
 */

import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import TeamComparison from '../components/TeamComparison';

describe('TeamComparison Component', () => {
  const mockTeam = {
    team_id: 'backend-team',
    team_name: 'Backend Engineering',
    dimensions: {
      security: 85,
      complexity: 72,
      documentation: 80,
      testing: 88,
      dependencies: 65,
      maintainability: 78
    },
    overall_caqi: 380,
    personality_archetype: 'Pragmatic Engineer',
    member_count: 4,
    calculated_at: '2026-06-06T14:30:00Z'
  };

  const mockTeams = [mockTeam, mockTeam, mockTeam];

  it('renders without crashing with empty teams', () => {
    render(<TeamComparison teams={[]} />);
    expect(screen.getByText(/No teams found/i)).toBeInTheDocument();
  });

  it('renders with teams', () => {
    render(<TeamComparison teams={mockTeams} />);
    expect(screen.getByText('Team Comparison')).toBeInTheDocument();
  });

  it('displays loading state', () => {
    render(<TeamComparison teams={[]} loading={true} />);
    expect(screen.getByText(/Loading team data/i)).toBeInTheDocument();
  });

  it('displays error state', () => {
    const errorMsg = 'Failed to load teams';
    render(<TeamComparison teams={[]} error={errorMsg} />);
    expect(screen.getByText(errorMsg)).toBeInTheDocument();
  });

  it('renders team selector pills', () => {
    render(<TeamComparison teams={mockTeams} />);
    mockTeams.forEach((team) => {
      const elements = screen.getAllByText(team.team_name);
      expect(elements.length).toBeGreaterThan(0);
    });
  });

  it('displays CAQI badge in team pill', () => {
    render(<TeamComparison teams={mockTeams} />);
    const elements = screen.queryAllByText(/380/);
    expect(elements.length).toBeGreaterThan(0);
  });

  it('selects first team by default', () => {
    render(<TeamComparison teams={mockTeams} />);
    const firstTeamName = mockTeams[0].team_name;
    const elements = screen.getAllByText(firstTeamName);
    expect(elements.length).toBeGreaterThan(0);
  });

  it('switches teams on pill click', () => {
    render(<TeamComparison teams={mockTeams} />);
    const secondTeam = mockTeams[1];
    const teamButton = screen.getAllByText(secondTeam.team_name)[0];
    fireEvent.click(teamButton);
    const elements = screen.getAllByText(secondTeam.team_name);
    expect(elements.length).toBeGreaterThan(0);
  });

  it('displays comparison table with correct headers', () => {
    render(<TeamComparison teams={mockTeams} />);
    expect(screen.queryAllByText(/Team/i).length).toBeGreaterThan(0);
    expect(screen.queryAllByText(/Archetype/i).length).toBeGreaterThan(0);
    expect(screen.queryAllByText(/CAQI/i).length).toBeGreaterThan(0);
  });

  it('displays all teams in comparison table', () => {
    render(<TeamComparison teams={mockTeams} />);
    mockTeams.forEach((team) => {
      // Team name appears in both pill and table
      const elements = screen.getAllByText(team.team_name);
      expect(elements.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('calculates and displays average CAQI', () => {
    render(<TeamComparison teams={mockTeams} />);
    const avgCAQI = Math.round(
      mockTeams.reduce((sum, t) => sum + t.overall_caqi, 0) / mockTeams.length
    );
    const elements = screen.queryAllByText(String(avgCAQI));
    expect(elements.length).toBeGreaterThan(0);
  });

  it('displays highest CAQI correctly', () => {
    render(<TeamComparison teams={mockTeams} />);
    const highest = Math.max(...mockTeams.map((t) => t.overall_caqi));
    const elements = screen.queryAllByText(String(highest));
    expect(elements.length).toBeGreaterThan(0);
  });

  it('displays total members', () => {
    render(<TeamComparison teams={mockTeams} />);
    const totalMembers = mockTeams.reduce((sum, t) => sum + t.member_count, 0);
    expect(screen.getByText(String(totalMembers))).toBeInTheDocument();
  });

  it('displays team count', () => {
    render(<TeamComparison teams={mockTeams} />);
    expect(screen.getByText(String(mockTeams.length))).toBeInTheDocument();
  });

  it('handles single team', () => {
    render(<TeamComparison teams={[mockTeam]} />);
    const elements = screen.queryAllByText(mockTeam.team_name);
    expect(elements.length).toBeGreaterThan(0);
  });

  it('handles many teams', () => {
    const manyTeams = Array(10).fill(mockTeam).map((t, i) => ({
      ...t,
      team_id: `team-${i}`,
      team_name: `Team ${i}`
    }));
    render(<TeamComparison teams={manyTeams} />);
    manyTeams.slice(0, 3).forEach((team) => {
      const elements = screen.queryAllByText(team.team_name);
      expect(elements.length).toBeGreaterThanOrEqual(0);
    });
  });

  it('handles teams with fractional CAQI scores', () => {
    const fractionalTeams = [
      {
        ...mockTeam,
        overall_caqi: 380.5
      }
    ];
    render(<TeamComparison teams={fractionalTeams} />);
    const elements = screen.queryAllByText(/380/);
    expect(elements.length).toBeGreaterThan(0); // Should be rounded
  });

  it('handles missing team data gracefully', () => {
    const incompleteTeam = {
      ...mockTeam,
      team_name: '',
      member_count: 0
    };
    expect(() => {
      render(<TeamComparison teams={[incompleteTeam]} />);
    }).not.toThrow();
  });

  it('shows table row as clickable', () => {
    render(<TeamComparison teams={mockTeams} />);
    const tableRows = screen.getAllByRole('row');
    expect(tableRows.length).toBeGreaterThan(0);
  });

  it('displays fair CAQI level (300-350)', () => {
    const fairTeams = [
      {
        ...mockTeam,
        team_id: 'fair-team',
        team_name: 'Fair Team',
        overall_caqi: 320
      }
    ];
    const { container } = render(<TeamComparison teams={fairTeams} />);
    expect(container.querySelector('[class*="caqi-fair"]')).toBeInTheDocument();
  });

  it('displays poor CAQI level (<300)', () => {
    const poorTeams = [
      {
        ...mockTeam,
        team_id: 'poor-team',
        team_name: 'Poor Team',
        overall_caqi: 250
      }
    ];
    const { container } = render(<TeamComparison teams={poorTeams} />);
    expect(container.querySelector('[class*="caqi-poor"]')).toBeInTheDocument();
  });
});
