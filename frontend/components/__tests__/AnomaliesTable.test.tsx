/**
 * Tests for AnomaliesTable Component
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import AnomaliesTable from '../AnomaliesTable';

describe('AnomaliesTable', () => {
  const mockAnomalies = [
    {
      id: 'anom-1',
      dimension: 'security',
      previousScore: 75,
      currentScore: 85,
      changePercent: 13.3,
      severity: 'high' as const,
      detectedAt: '2026-06-05T10:00:00Z',
      reviewed: false,
    },
    {
      id: 'anom-2',
      dimension: 'complexity',
      previousScore: 70,
      currentScore: 65,
      changePercent: -7.1,
      severity: 'medium' as const,
      detectedAt: '2026-06-04T14:00:00Z',
      reviewed: true,
      reviewedBy: 'user-1',
    },
    {
      id: 'anom-3',
      dimension: 'documentation',
      previousScore: 80,
      currentScore: 72,
      changePercent: -10.0,
      severity: 'critical' as const,
      detectedAt: '2026-06-03T09:00:00Z',
      reviewed: false,
    },
  ];

  const defaultProps = {
    teamId: 'backend-team',
    anomalies: mockAnomalies,
  };

  describe('Rendering', () => {
    it('should render table container', () => {
      render(<AnomaliesTable {...defaultProps} />);
      expect(screen.getByTestId('anomalies-table')).toBeInTheDocument();
    });

    it('should display team ID in header', () => {
      render(<AnomaliesTable {...defaultProps} />);
      expect(screen.getByText(/backend-team - Anomalies/)).toBeInTheDocument();
    });

    it('should render table with all anomalies', () => {
      render(<AnomaliesTable {...defaultProps} />);
      const table = screen.getByTestId('anomalies-data-table');
      expect(table).toBeInTheDocument();

      expect(screen.getByTestId('anomaly-row-anom-1')).toBeInTheDocument();
      expect(screen.getByTestId('anomaly-row-anom-2')).toBeInTheDocument();
      expect(screen.getByTestId('anomaly-row-anom-3')).toBeInTheDocument();
    });

    it('should display column headers', () => {
      render(<AnomaliesTable {...defaultProps} />);
      expect(screen.getByTestId('dimension-header')).toBeInTheDocument();
      expect(screen.getByTestId('change-header')).toBeInTheDocument();
      expect(screen.getByTestId('severity-header')).toBeInTheDocument();
    });

    it('should display anomaly data', () => {
      render(<AnomaliesTable {...defaultProps} />);
      expect(screen.getByText('Security')).toBeInTheDocument();
      expect(screen.getByText('Complexity')).toBeInTheDocument();
      expect(screen.getByText(/\+13\.3%/)).toBeInTheDocument();
      expect(screen.getByText(/-10\.0%/)).toBeInTheDocument();
    });
  });

  describe('Filtering', () => {
    it('should filter by severity', () => {
      render(<AnomaliesTable {...defaultProps} />);
      const severityFilter = screen.getByTestId('severity-filter') as HTMLSelectElement;

      fireEvent.change(severityFilter, { target: { value: 'critical' } });

      expect(screen.getByTestId('anomaly-row-anom-3')).toBeInTheDocument();
      expect(screen.queryByTestId('anomaly-row-anom-1')).not.toBeInTheDocument();
    });

    it('should filter by reviewed status', () => {
      render(<AnomaliesTable {...defaultProps} />);
      const reviewedFilter = screen.getByTestId('reviewed-filter') as HTMLSelectElement;

      fireEvent.change(reviewedFilter, { target: { value: 'reviewed' } });

      expect(screen.getByTestId('anomaly-row-anom-2')).toBeInTheDocument();
      expect(screen.queryByTestId('anomaly-row-anom-1')).not.toBeInTheDocument();
    });
  });

  describe('Severity Badges', () => {
    it('should display severity for all anomalies', () => {
      render(<AnomaliesTable {...defaultProps} />);
      expect(screen.getByTestId('severity-badge-anom-1')).toHaveTextContent('HIGH');
      expect(screen.getByTestId('severity-badge-anom-2')).toHaveTextContent('MEDIUM');
      expect(screen.getByTestId('severity-badge-anom-3')).toHaveTextContent('CRITICAL');
    });
  });

  describe('Review Status', () => {
    it('should show reviewed status for reviewed anomalies', () => {
      render(<AnomaliesTable {...defaultProps} />);
      expect(screen.getByText('✓ Reviewed')).toBeInTheDocument();
    });

    it('should show unreviewed status for unreviewed anomalies', () => {
      render(<AnomaliesTable {...defaultProps} />);
      expect(screen.getAllByText('Unreviewed')).toHaveLength(2);
    });

    it('should show review button for unreviewed anomalies', () => {
      render(<AnomaliesTable {...defaultProps} />);
      expect(screen.getByTestId('review-btn-anom-1')).toBeInTheDocument();
      expect(screen.getByTestId('review-btn-anom-3')).toBeInTheDocument();
    });

    it('should not show review button for reviewed anomalies', () => {
      render(<AnomaliesTable {...defaultProps} />);
      expect(screen.queryByTestId('review-btn-anom-2')).not.toBeInTheDocument();
    });
  });

  describe('Callbacks', () => {
    it('should call onReviewAnomaly when review button clicked', () => {
      const mockReview = jest.fn();
      render(<AnomaliesTable {...defaultProps} onReviewAnomaly={mockReview} />);

      const reviewBtn = screen.getByTestId('review-btn-anom-1');
      fireEvent.click(reviewBtn);

      expect(mockReview).toHaveBeenCalledWith('anom-1');
    });

    it('should call onFilterChange when severity filter changes', () => {
      const mockFilterChange = jest.fn();
      render(<AnomaliesTable {...defaultProps} onFilterChange={mockFilterChange} />);

      const severityFilter = screen.getByTestId('severity-filter') as HTMLSelectElement;
      fireEvent.change(severityFilter, { target: { value: 'high' } });

      expect(mockFilterChange).toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('should have aria-label on review button', () => {
      render(<AnomaliesTable {...defaultProps} />);
      const reviewBtn = screen.getByTestId('review-btn-anom-1');
      expect(reviewBtn).toHaveAttribute('aria-label', expect.stringContaining('Review anomaly'));
    });
  });

  describe('Edge Cases', () => {
    it('should display empty state when no anomalies', () => {
      render(<AnomaliesTable {...{ ...defaultProps, anomalies: [] }} />);
      expect(screen.getByText('No anomalies found')).toBeInTheDocument();
    });

    it('should handle positive change percentage', () => {
      render(<AnomaliesTable {...defaultProps} />);
      expect(screen.getByText('+13.3%')).toBeInTheDocument();
    });

    it('should handle negative change percentage', () => {
      render(<AnomaliesTable {...defaultProps} />);
      expect(screen.getByText('-10.0%')).toBeInTheDocument();
    });

    it('should filter out anomalies with invalid severity', () => {
      const invalidAnomaly = {
        ...mockAnomalies[0],
        id: 'invalid',
        severity: 'invalid-severity' as any,
      };
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      render(<AnomaliesTable {...{ ...defaultProps, anomalies: [...mockAnomalies, invalidAnomaly] }} />);
      expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('Invalid severity'));
      consoleSpy.mockRestore();
    });
  });
});
