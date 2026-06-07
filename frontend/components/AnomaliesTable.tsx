/**
 * Anomalies Table Component - displays detected anomalies with filtering
 *
 * Features:
 * - Sortable columns
 * - Severity filtering (low, medium, high, critical)
 * - Reviewed/unreviewed status
 * - Change percentage visualization
 * - Mark as reviewed action
 */

import React, { useState, useMemo, useCallback } from 'react';
import { SEVERITY_COLORS } from '../constants/caqi';

type SeverityLevel = 'low' | 'medium' | 'high' | 'critical';
type SortField = 'dimension' | 'changePercent' | 'severity' | 'detectedAt';
type SortOrder = 'asc' | 'desc';

interface Anomaly {
  id: string;
  dimension: string;
  previousScore: number;
  currentScore: number;
  changePercent: number;
  severity: SeverityLevel;
  detectedAt: string;
  reviewed: boolean;
  reviewedBy?: string;
  notes?: string;
}

interface AnomaliesTableProps {
  teamId: string;
  anomalies: Anomaly[];
  onReviewAnomaly?: (anomalyId: string, notes?: string) => void;
  onFilterChange?: (filters: { severity?: SeverityLevel; reviewed?: boolean }) => void;
}

const VALID_SEVERITIES: SeverityLevel[] = ['low', 'medium', 'high', 'critical'];

// Type-safe sort comparator
function compareValues<T>(aVal: T, bVal: T, isAscending: boolean): number {
  let a = aVal;
  let b = bVal;

  if (typeof a === 'string' && typeof b === 'string') {
    a = a.toLowerCase() as T;
    b = b.toLowerCase() as T;
  }

  if (a < b) return isAscending ? -1 : 1;
  if (a > b) return isAscending ? 1 : -1;
  return 0;
}

export const AnomaliesTable: React.FC<AnomaliesTableProps> = ({
  teamId,
  anomalies,
  onReviewAnomaly,
  onFilterChange,
}) => {
  const [sortField, setSortField] = useState<SortField>('detectedAt');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [severityFilter, setSeverityFilter] = useState<SeverityLevel | undefined>();
  const [reviewedFilter, setReviewedFilter] = useState<boolean | undefined>();

  // Validate anomalies data
  const validAnomalies = useMemo(() =>
    anomalies.filter((a) => {
      if (!VALID_SEVERITIES.includes(a.severity)) {
        console.warn(`Invalid severity: ${a.severity}`);
        return false;
      }
      return true;
    }),
    [anomalies]
  );

  const filteredAndSorted = useMemo(() => {
    let filtered = validAnomalies;

    if (severityFilter) {
      filtered = filtered.filter((a) => a.severity === severityFilter);
    }

    if (reviewedFilter !== undefined) {
      filtered = filtered.filter((a) => a.reviewed === reviewedFilter);
    }

    const sorted = [...filtered].sort((a, b) => {
      const aVal = a[sortField];
      const bVal = b[sortField];
      return compareValues(aVal, bVal, sortOrder === 'asc');
    });

    return sorted;
  }, [validAnomalies, sortField, sortOrder, severityFilter, reviewedFilter]);

  const handleSortChange = useCallback((field: SortField) => {
    setSortField((prev) => {
      if (prev === field) {
        setSortOrder((prevOrder) => (prevOrder === 'asc' ? 'desc' : 'asc'));
      } else {
        setSortOrder('desc');
      }
      return prev === field ? prev : field;
    });
  }, []);

  const handleFilterChange = useCallback((newSeverity?: SeverityLevel, newReviewed?: boolean) => {
    setSeverityFilter(newSeverity);
    setReviewedFilter(newReviewed);
    onFilterChange?.({ severity: newSeverity, reviewed: newReviewed });
  }, [onFilterChange]);

  const handleReviewClick = useCallback((anomalyId: string) => {
    onReviewAnomaly?.(anomalyId);
  }, [onReviewAnomaly]);

  return (
    <div className="anomalies-table" data-testid="anomalies-table">
      <div className="table-header">
        <h2>{teamId} - Anomalies</h2>
        <div className="filter-controls">
          <select
            value={severityFilter || ''}
            onChange={(e) => handleFilterChange((e.target.value as SeverityLevel) || undefined)}
            data-testid="severity-filter"
          >
            <option value="">All Severities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>

          <select
            value={reviewedFilter === undefined ? '' : reviewedFilter ? 'reviewed' : 'unreviewed'}
            onChange={(e) => {
              if (e.target.value === '') handleFilterChange(severityFilter, undefined);
              else if (e.target.value === 'reviewed') handleFilterChange(severityFilter, true);
              else handleFilterChange(severityFilter, false);
            }}
            data-testid="reviewed-filter"
          >
            <option value="">All Status</option>
            <option value="unreviewed">Unreviewed</option>
            <option value="reviewed">Reviewed</option>
          </select>
        </div>
      </div>

      <div className="table-wrapper">
        <table data-testid="anomalies-data-table">
          <thead>
            <tr>
              <th
                onClick={() => handleSortChange('dimension')}
                className={`sortable ${sortField === 'dimension' ? `sort-${sortOrder}` : ''}`}
                data-testid="dimension-header"
              >
                Dimension
              </th>
              <th>Previous Score</th>
              <th
                onClick={() => handleSortChange('changePercent')}
                className={`sortable ${sortField === 'changePercent' ? `sort-${sortOrder}` : ''}`}
                data-testid="change-header"
              >
                Change %
              </th>
              <th
                onClick={() => handleSortChange('severity')}
                className={`sortable ${sortField === 'severity' ? `sort-${sortOrder}` : ''}`}
                data-testid="severity-header"
              >
                Severity
              </th>
              <th>Detected</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredAndSorted.length === 0 ? (
              <tr>
                <td colSpan={7} className="no-data">
                  No anomalies found
                </td>
              </tr>
            ) : (
              filteredAndSorted.map((anomaly) => (
                <tr key={anomaly.id} data-testid={`anomaly-row-${anomaly.id}`}>
                  <td className="dimension-cell">
                    <strong>{anomaly.dimension.charAt(0).toUpperCase() + anomaly.dimension.slice(1)}</strong>
                  </td>
                  <td>{anomaly.previousScore.toFixed(1)}</td>
                  <td>
                    <div className="change-cell">
                      <span
                        className="change-value"
                        style={{
                          color: anomaly.changePercent > 0 ? '#22c55e' : '#ef4444',
                        }}
                      >
                        {anomaly.changePercent > 0 ? '+' : ''}{anomaly.changePercent.toFixed(1)}%
                      </span>
                      <span className="current-score">({anomaly.currentScore.toFixed(1)})</span>
                    </div>
                  </td>
                  <td>
                    <span
                      className="severity-badge"
                      style={{ backgroundColor: SEVERITY_COLORS[anomaly.severity] }}
                      data-testid={`severity-badge-${anomaly.id}`}
                    >
                      {anomaly.severity.toUpperCase()}
                    </span>
                  </td>
                  <td className="date-cell">
                    {new Date(anomaly.detectedAt).toLocaleDateString()}
                  </td>
                  <td>
                    {anomaly.reviewed ? (
                      <span className="status-reviewed">✓ Reviewed</span>
                    ) : (
                      <span className="status-unreviewed">Unreviewed</span>
                    )}
                  </td>
                  <td>
                    {!anomaly.reviewed && (
                      <button
                        onClick={() => handleReviewClick(anomaly.id)}
                        aria-label={`Review anomaly ${anomaly.id}`}
                        data-testid={`review-btn-${anomaly.id}`}
                      >
                        Review
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <style jsx>{`
        .anomalies-table {
          width: 100%;
          padding: 24px;
          background: white;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .table-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .table-header h2 {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
        }

        .filter-controls {
          display: flex;
          gap: 12px;
        }

        .filter-controls select {
          padding: 8px 12px;
          border: 1px solid #d1d5db;
          border-radius: 6px;
          font-size: 14px;
          background: white;
          cursor: pointer;
        }

        .table-wrapper {
          overflow-x: auto;
        }

        table {
          width: 100%;
          border-collapse: collapse;
        }

        thead {
          background: #f9fafb;
        }

        th {
          padding: 12px;
          text-align: left;
          font-weight: 600;
          font-size: 12px;
          color: #374151;
          border-bottom: 2px solid #e5e7eb;
        }

        th.sortable {
          cursor: pointer;
          user-select: none;
        }

        th.sortable:hover {
          background: #f3f4f6;
        }

        th.sort-asc::after {
          content: ' ↑';
        }

        th.sort-desc::after {
          content: ' ↓';
        }

        td {
          padding: 12px;
          border-bottom: 1px solid #e5e7eb;
        }

        tr:hover {
          background: #f9fafb;
        }

        .dimension-cell {
          font-weight: 500;
        }

        .change-cell {
          display: flex;
          gap: 8px;
          align-items: center;
        }

        .change-value {
          font-weight: 600;
        }

        .current-score {
          color: #6b7280;
          font-size: 12px;
        }

        .severity-badge {
          display: inline-block;
          padding: 4px 8px;
          border-radius: 4px;
          color: white;
          font-size: 11px;
          font-weight: 600;
        }

        .date-cell {
          color: #6b7280;
          font-size: 14px;
        }

        .status-reviewed {
          color: #22c55e;
          font-weight: 500;
        }

        .status-unreviewed {
          color: #f97316;
          font-weight: 500;
        }

        button {
          padding: 6px 12px;
          background: #3b82f6;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 12px;
          cursor: pointer;
          transition: background-color 200ms;
        }

        button:hover {
          background: #2563eb;
        }

        .no-data {
          text-align: center;
          color: #6b7280;
          padding: 32px 12px;
        }
      `}</style>
    </div>
  );
};

export default AnomaliesTable;
