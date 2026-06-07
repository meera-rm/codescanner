/**
 * Tests for DeveloperContributions Component
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import DeveloperContributions from '../DeveloperContributions';

describe('DeveloperContributions', () => {
  const mockDevelopers = [
    {
      developerId: 'dev-1',
      teamId: 'backend-team',
      contributions: {
        security: { developerScore: 80, teamAvg: 75, contribution: 5.0 },
        complexity: { developerScore: 72, teamAvg: 70, contribution: 2.0 },
        documentation: { developerScore: 75, teamAvg: 65, contribution: 10.0 },
        testing: { developerScore: 85, teamAvg: 80, contribution: 5.0 },
        dependencies: { developerScore: 70, teamAvg: 60, contribution: 10.0 },
        maintainability: { developerScore: 80, teamAvg: 75, contribution: 5.0 },
      },
      overallContribution: 6.17,
    },
    {
      developerId: 'dev-2',
      teamId: 'backend-team',
      contributions: {
        security: { developerScore: 70, teamAvg: 75, contribution: -5.0 },
        complexity: { developerScore: 68, teamAvg: 70, contribution: -2.0 },
        documentation: { developerScore: 60, teamAvg: 65, contribution: -5.0 },
        testing: { developerScore: 75, teamAvg: 80, contribution: -5.0 },
        dependencies: { developerScore: 50, teamAvg: 60, contribution: -10.0 },
        maintainability: { developerScore: 70, teamAvg: 75, contribution: -5.0 },
      },
      overallContribution: -5.33,
    },
  ];

  const defaultProps = {
    teamId: 'backend-team',
    developers: mockDevelopers,
    period: 30,
  };

  describe('Rendering', () => {
    it('should render component container', () => {
      render(<DeveloperContributions {...defaultProps} />);
      expect(screen.getByTestId('developer-contributions')).toBeInTheDocument();
    });

    it('should display team ID in header', () => {
      render(<DeveloperContributions {...defaultProps} />);
      expect(screen.getByText(/backend-team - Developer Contributions/)).toBeInTheDocument();
    });

    it('should display period in header', () => {
      render(<DeveloperContributions {...defaultProps} />);
      expect(screen.getByText('(30 days)')).toBeInTheDocument();
    });

    it('should render developer cards for all developers', () => {
      render(<DeveloperContributions {...defaultProps} />);
      expect(screen.getByTestId('dev-card-dev-1')).toBeInTheDocument();
      expect(screen.getByTestId('dev-card-dev-2')).toBeInTheDocument();
    });

    it('should display developer IDs', () => {
      render(<DeveloperContributions {...defaultProps} />);
      expect(screen.getByText('dev-1')).toBeInTheDocument();
      expect(screen.getByText('dev-2')).toBeInTheDocument();
    });

    it('should display overall contribution scores', () => {
      render(<DeveloperContributions {...defaultProps} />);
      expect(screen.getByText('+6.17')).toBeInTheDocument();
      expect(screen.getByText('-5.33')).toBeInTheDocument();
    });
  });

  describe('Impact Labels', () => {
    it('should display impact label for positive contribution', () => {
      render(<DeveloperContributions {...defaultProps} />);
      expect(screen.getByText('High Impact')).toBeInTheDocument();
    });

    it('should display impact label for negative contribution', () => {
      render(<DeveloperContributions {...defaultProps} />);
      expect(screen.getByText('Medium Impact')).toBeInTheDocument();
    });
  });

  describe('Expansion/Collapse', () => {
    it('should expand developer details on click', () => {
      render(<DeveloperContributions {...defaultProps} />);
      const card = screen.getByTestId('dev-card-dev-1');

      fireEvent.click(card);

      expect(screen.getByTestId('dim-dev-1-security')).toBeInTheDocument();
    });

    it('should collapse developer details on second click', () => {
      render(<DeveloperContributions {...defaultProps} />);
      const card = screen.getByTestId('dev-card-dev-1');

      fireEvent.click(card);
      fireEvent.click(card);

      expect(screen.queryByTestId('dim-dev-1-security')).not.toBeInTheDocument();
    });
  });

  describe('Dimension Breakdown', () => {
    it('should display dimension contributions when expanded', () => {
      render(<DeveloperContributions {...defaultProps} />);
      const card = screen.getByTestId('dev-card-dev-1');

      fireEvent.click(card);

      expect(screen.getByText('Security')).toBeInTheDocument();
      expect(screen.getByText('Complexity')).toBeInTheDocument();
      expect(screen.getByText('Documentation')).toBeInTheDocument();
    });

    it('should display contribution values', () => {
      render(<DeveloperContributions {...defaultProps} />);
      const card = screen.getByTestId('dev-card-dev-1');

      fireEvent.click(card);

      expect(screen.getByText('+5.00')).toBeInTheDocument();
      expect(screen.getByText('+10.00')).toBeInTheDocument();
    });
  });

  describe('Sorting by Impact', () => {
    it('should sort developers by absolute contribution', () => {
      render(<DeveloperContributions {...defaultProps} />);
      const cards = screen.getAllByTestId(/dev-card-/);

      // First should be dev-1 (highest impact: +6.17)
      expect(cards[0]).toHaveTextContent('dev-1');
      // Second should be dev-2 (negative impact: -5.33)
      expect(cards[1]).toHaveTextContent('dev-2');
    });
  });

  describe('Callbacks', () => {
    it('should call onDeveloperClick when developer card clicked', () => {
      const mockClick = jest.fn();
      render(<DeveloperContributions {...defaultProps} onDeveloperClick={mockClick} />);

      const card = screen.getByTestId('dev-card-dev-1');
      fireEvent.click(card);

      expect(mockClick).toHaveBeenCalledWith('dev-1');
    });

    it('should call onDeveloperClick when Enter key pressed', () => {
      const mockClick = jest.fn();
      render(<DeveloperContributions {...defaultProps} onDeveloperClick={mockClick} />);

      const card = screen.getByTestId('dev-card-dev-1');
      fireEvent.keyDown(card, { key: 'Enter' });

      expect(mockClick).toHaveBeenCalledWith('dev-1');
    });

    it('should call onDeveloperClick when Space key pressed', () => {
      const mockClick = jest.fn();
      render(<DeveloperContributions {...defaultProps} onDeveloperClick={mockClick} />);

      const card = screen.getByTestId('dev-card-dev-1');
      fireEvent.keyDown(card, { key: ' ' });

      expect(mockClick).toHaveBeenCalledWith('dev-1');
    });
  });

  describe('Accessibility', () => {
    it('should have aria-label on developer cards', () => {
      render(<DeveloperContributions {...defaultProps} />);
      const card = screen.getByTestId('dev-card-dev-1');
      expect(card).toHaveAttribute('aria-label', expect.stringContaining('dev-1'));
    });

    it('should have aria-expanded attribute', () => {
      render(<DeveloperContributions {...defaultProps} />);
      const card = screen.getByTestId('dev-card-dev-1');
      expect(card).toHaveAttribute('aria-expanded', 'false');
    });

    it('should update aria-expanded when expanded', () => {
      render(<DeveloperContributions {...defaultProps} />);
      const card = screen.getByTestId('dev-card-dev-1');

      fireEvent.click(card);

      expect(card).toHaveAttribute('aria-expanded', 'true');
    });
  });

  describe('Edge Cases', () => {
    it('should display empty state when no developers', () => {
      render(<DeveloperContributions {...{ ...defaultProps, developers: [] }} />);
      expect(screen.getByText('No developer data available')).toBeInTheDocument();
    });

    it('should handle different periods', () => {
      render(<DeveloperContributions {...defaultProps} period={90} />);
      expect(screen.getByText('(90 days)')).toBeInTheDocument();
    });

    it('should handle single developer', () => {
      render(
        <DeveloperContributions
          {...{ ...defaultProps, developers: [mockDevelopers[0]] }}
        />
      );

      expect(screen.getByTestId('dev-card-dev-1')).toBeInTheDocument();
      expect(screen.queryByTestId('dev-card-dev-2')).not.toBeInTheDocument();
    });
  });
});
