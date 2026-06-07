/**
 * Tests for CAQIGauge Component
 */

import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import CAQIGauge from '../CAQIGauge';

describe('CAQIGauge', () => {
  const defaultProps = {
    teamId: 'backend-team',
    overallCaqi: 380,
    dimensions: {
      security: 85,
      complexity: 72,
      documentation: 80,
      testing: 88,
      dependencies: 65,
      maintainability: 78,
    },
    calculatedAt: '2026-06-06T14:30:00Z',
  };

  describe('Rendering', () => {
    it('should render gauge container', () => {
      render(<CAQIGauge {...defaultProps} />);
      const gauge = screen.getByTestId('caqi-gauge');
      expect(gauge).toBeInTheDocument();
    });

    it('should display team ID', () => {
      render(<CAQIGauge {...defaultProps} />);
      expect(screen.getByText('backend-team')).toBeInTheDocument();
    });

    it('should display overall CAQI score', () => {
      render(<CAQIGauge {...defaultProps} />);
      expect(screen.getByText('380')).toBeInTheDocument();
    });

    it('should display /500 label', () => {
      render(<CAQIGauge {...defaultProps} />);
      expect(screen.getByText('/500')).toBeInTheDocument();
    });

    it('should calculate and display correct grade', () => {
      render(<CAQIGauge {...defaultProps} />);
      expect(screen.getByText(/B\+/)).toBeInTheDocument(); // 380 = B+
    });

    it('should display timestamp when provided', () => {
      render(<CAQIGauge {...defaultProps} />);
      expect(screen.getByText(/6\/6\/2026/)).toBeInTheDocument();
    });

    it('should render all 6 dimensions', () => {
      render(<CAQIGauge {...defaultProps} />);
      expect(screen.getByTestId('dimension-security')).toBeInTheDocument();
      expect(screen.getByTestId('dimension-complexity')).toBeInTheDocument();
      expect(screen.getByTestId('dimension-documentation')).toBeInTheDocument();
      expect(screen.getByTestId('dimension-testing')).toBeInTheDocument();
      expect(screen.getByTestId('dimension-dependencies')).toBeInTheDocument();
      expect(screen.getByTestId('dimension-maintainability')).toBeInTheDocument();
    });
  });

  describe('Grading', () => {
    it('should assign A+ grade for 450+', () => {
      render(<CAQIGauge {...{ ...defaultProps, overallCaqi: 450 }} />);
      expect(screen.getByText('A+')).toBeInTheDocument();
    });

    it('should assign A grade for 400-449', () => {
      render(<CAQIGauge {...{ ...defaultProps, overallCaqi: 425 }} />);
      expect(screen.getByText('A')).toBeInTheDocument();
    });

    it('should assign B+ grade for 350-399', () => {
      render(<CAQIGauge {...{ ...defaultProps, overallCaqi: 375 }} />);
      expect(screen.getByText('B+')).toBeInTheDocument();
    });

    it('should assign F grade for 0-99', () => {
      render(<CAQIGauge {...{ ...defaultProps, overallCaqi: 50 }} />);
      expect(screen.getByText('F')).toBeInTheDocument();
    });
  });

  describe('Interaction', () => {
    it('should call onDimensionClick when dimension clicked', () => {
      const mockClick = jest.fn();
      render(<CAQIGauge {...defaultProps} onDimensionClick={mockClick} />);

      const securityCard = screen.getByTestId('dimension-security');
      fireEvent.click(securityCard);

      expect(mockClick).toHaveBeenCalledWith('security');
    });

    it('should call onDimensionClick when dimension key pressed', () => {
      const mockClick = jest.fn();
      render(<CAQIGauge {...defaultProps} onDimensionClick={mockClick} />);

      const securityCard = screen.getByTestId('dimension-security');
      fireEvent.keyDown(securityCard, { key: 'Enter' });

      expect(mockClick).toHaveBeenCalledWith('security');
    });

    it('should handle space key on dimension card', () => {
      const mockClick = jest.fn();
      render(<CAQIGauge {...defaultProps} onDimensionClick={mockClick} />);

      const testingCard = screen.getByTestId('dimension-testing');
      fireEvent.keyDown(testingCard, { key: ' ' });

      expect(mockClick).toHaveBeenCalledWith('testing');
    });
  });

  describe('Accessibility', () => {
    it('should have aria-label on dimension cards', () => {
      render(<CAQIGauge {...defaultProps} />);
      const securityCard = screen.getByTestId('dimension-security');
      expect(securityCard).toHaveAttribute('aria-label', 'Security: 85');
    });

    it('should be keyboard navigable', () => {
      render(<CAQIGauge {...defaultProps} />);
      const dimensionCards = screen.getAllByRole('button');
      expect(dimensionCards.length).toBeGreaterThan(0);
      dimensionCards.forEach((card) => {
        expect(card).toHaveAttribute('tabindex', '0');
      });
    });
  });

  describe('Prop Validation', () => {
    it('should warn on invalid CAQI score', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      render(<CAQIGauge {...{ ...defaultProps, overallCaqi: 600 }} />);
      expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('Invalid CAQI score'));
      consoleSpy.mockRestore();
    });

    it('should warn on invalid dimension score', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      render(<CAQIGauge {...{ ...defaultProps, dimensions: { ...defaultProps.dimensions, security: 150 } }} />);
      expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('Invalid dimension score'));
      consoleSpy.mockRestore();
    });
  });

  describe('Edge Cases', () => {
    it('should handle CAQI score of 0', () => {
      render(<CAQIGauge {...{ ...defaultProps, overallCaqi: 0 }} />);
      expect(screen.getByText('0')).toBeInTheDocument();
      expect(screen.getByText('F')).toBeInTheDocument();
    });

    it('should handle CAQI score of 500', () => {
      render(<CAQIGauge {...{ ...defaultProps, overallCaqi: 500 }} />);
      expect(screen.getByText('500')).toBeInTheDocument();
      expect(screen.getByText('A+')).toBeInTheDocument();
    });

    it('should handle missing calculatedAt', () => {
      const { calculatedAt, ...propsWithoutDate } = defaultProps;
      const { container } = render(<CAQIGauge {...propsWithoutDate} />);
      expect(container).toBeInTheDocument();
    });

    it('should handle invalid date format', () => {
      render(<CAQIGauge {...{ ...defaultProps, calculatedAt: 'invalid-date' }} />);
      expect(screen.getByText('Invalid date')).toBeInTheDocument();
    });
  });
});
