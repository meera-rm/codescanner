# Component Integration Guide

## Overview

CodePulse AI frontend consists of 3 core components that work together to display code quality analytics. This guide shows how to integrate them into your dashboard.

---

## Component 1: CAQIGauge

**Purpose:** Display overall code quality score (0-500) with per-dimension breakdown  
**File:** `frontend/components/CAQIGauge.tsx`  
**Lines:** ~260

### Props Interface
```typescript
interface CAQIGaugeProps {
  teamId: string;                          // Team identifier
  overallCaqi: number;                     // Overall score (0-500)
  dimensions: {                            // Dimension scores (0-100 each)
    security: number;
    complexity: number;
    documentation: number;
    testing: number;
    dependencies: number;
    maintainability: number;
  };
  calculatedAt?: string;                   // ISO timestamp
  onDimensionClick?: (dimension: string) => void;  // Click handler
}
```

### Basic Usage
```typescript
<CAQIGauge
  teamId="backend-team"
  overallCaqi={380}
  dimensions={{
    security: 85,
    complexity: 72,
    documentation: 80,
    testing: 88,
    dependencies: 65,
    maintainability: 78,
  }}
  calculatedAt="2026-06-06T14:30:00Z"
  onDimensionClick={(dim) => console.log(`Clicked: ${dim}`)}
/>
```

### Features
- ✅ Circular gauge visualization
- ✅ Color-coded score (excellent/good/fair/poor)
- ✅ Grade assignment (A+, A, B+, B, C+, C, D+, D, F)
- ✅ Per-dimension breakdown with progress bars
- ✅ Keyboard navigation support (Enter/Space on dimension cards)
- ✅ WCAG 2.1 Level AA accessibility
- ✅ Last calculated timestamp

### Grade Scale
| Grade | Range | Meaning |
|-------|-------|---------|
| A+ | 450-500 | Excellent |
| A | 400-449 | Very Good |
| B+ | 350-399 | Good |
| B | 300-349 | Acceptable |
| C+ | 250-299 | Fair |
| C | 200-249 | Poor |
| D+ | 150-199 | Very Poor |
| D | 100-149 | Critical |
| F | 0-99 | Failing |

### Integration Example
```typescript
import CAQIGauge from '@/components/CAQIGauge';
import { apiClient, TeamCAQI } from '@/services/apiClient';
import { useState, useEffect } from 'react';

export const Dashboard = () => {
  const [caqi, setCAQI] = useState<TeamCAQI | null>(null);

  useEffect(() => {
    apiClient.getTeamCAQI('backend-team').then(setCAQI);
  }, []);

  if (!caqi) return <div>Loading...</div>;

  return (
    <CAQIGauge
      teamId={caqi.team_id}
      overallCaqi={caqi.overall_caqi}
      dimensions={caqi.dimensions}
      calculatedAt={caqi.calculated_at}
      onDimensionClick={(dim) => {
        // Navigate to dimension detail page
        window.location.href = `/dimensions/${dim}`;
      }}
    />
  );
};
```

---

## Component 2: AnomaliesTable

**Purpose:** Display detected score anomalies with filtering and review functionality  
**File:** `frontend/components/AnomaliesTable.tsx`  
**Lines:** ~250

### Props Interface
```typescript
interface AnomaliesTableProps {
  teamId: string;                                    // Team identifier
  anomalies: Anomaly[];                              // List of anomalies
  onReviewAnomaly?: (anomalyId: string, notes?: string) => void;  // Review callback
  onFilterChange?: (filters: FilterState) => void;   // Filter change callback
}

interface Anomaly {
  id: string;
  dimension: string;
  previousScore: number;
  currentScore: number;
  changePercent: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  detectedAt: string;
  reviewed: boolean;
  reviewedBy?: string;
  notes?: string;
}
```

### Basic Usage
```typescript
<AnomaliesTable
  teamId="backend-team"
  anomalies={[
    {
      id: 'anom-1',
      dimension: 'security',
      previousScore: 75,
      currentScore: 85,
      changePercent: 13.3,
      severity: 'high',
      detectedAt: '2026-06-05T10:00:00Z',
      reviewed: false,
    },
  ]}
  onReviewAnomaly={(id) => console.log(`Reviewed: ${id}`)}
  onFilterChange={(filters) => console.log('Filters:', filters)}
/>
```

### Features
- ✅ Sortable columns (dimension, change %, severity, date)
- ✅ Severity filtering (low, medium, high, critical)
- ✅ Review status filtering
- ✅ Color-coded severity badges
- ✅ Review status indicator
- ✅ Review button for unreviewed anomalies
- ✅ Change direction indicator (+/-)
- ✅ Type-safe sorting with custom comparator

### Integration Example
```typescript
import AnomaliesTable from '@/components/AnomaliesTable';
import { apiClient, Anomaly } from '@/services/apiClient';
import { useState, useEffect } from 'react';

export const AnomaliesPage = ({ teamId }: { teamId: string }) => {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [severity, setSeverity] = useState<string | undefined>();
  const [reviewed, setReviewed] = useState<boolean | undefined>();

  useEffect(() => {
    apiClient
      .getAnomalies(teamId, severity as any, reviewed)
      .then(setAnomalies);
  }, [teamId, severity, reviewed]);

  const handleReview = async (anomalyId: string) => {
    await apiClient.reviewAnomaly(teamId, anomalyId);
    // Refresh anomalies
    const updated = await apiClient.getAnomalies(teamId);
    setAnomalies(updated);
  };

  return (
    <AnomaliesTable
      teamId={teamId}
      anomalies={anomalies}
      onReviewAnomaly={handleReview}
      onFilterChange={(filters) => {
        setSeverity(filters.severity);
        setReviewed(filters.reviewed);
      }}
    />
  );
};
```

---

## Component 3: DeveloperContributions

**Purpose:** Show individual developer impact on code quality metrics  
**File:** `frontend/components/DeveloperContributions.tsx`  
**Lines:** ~320

### Props Interface
```typescript
interface DeveloperContributionsProps {
  teamId: string;
  developers: Developer[];
  period?: number;                         // Analysis period in days (default: 30)
  onDeveloperClick?: (developerId: string) => void;  // Click handler
}

interface Developer {
  developerId: string;
  teamId: string;
  contributions: {                         // Per-dimension scores
    [key: string]: {
      developerScore: number;
      teamAvg: number;
      contribution: number;
    };
  };
  overallContribution: number;
}
```

### Basic Usage
```typescript
<DeveloperContributions
  teamId="backend-team"
  developers={[
    {
      developerId: 'dev-1',
      teamId: 'backend-team',
      contributions: {
        security: {
          developerScore: 80,
          teamAvg: 75,
          contribution: 5.0,
        },
        // ... other dimensions
      },
      overallContribution: 6.17,
    },
  ]}
  period={30}
  onDeveloperClick={(devId) => console.log(`Clicked: ${devId}`)}
/>
```

### Features
- ✅ Expandable developer cards
- ✅ Overall contribution score (positive/negative)
- ✅ Impact labels (High/Medium/Low)
- ✅ Per-dimension contribution breakdown
- ✅ Color-coded bars (green for positive, red for negative)
- ✅ Keyboard navigation (Enter/Space to expand)
- ✅ Sorted by impact (highest first)
- ✅ Team average comparison

### Integration Example
```typescript
import DeveloperContributions from '@/components/DeveloperContributions';
import { apiClient, Developer } from '@/services/apiClient';
import { useState, useEffect } from 'react';

export const TeamAnalytics = ({ teamId }: { teamId: string }) => {
  const [developers, setDevelopers] = useState<Developer[]>([]);
  const [period, setPeriod] = useState(30);

  useEffect(() => {
    apiClient
      .getDeveloperContributions(teamId, period)
      .then(setDevelopers);
  }, [teamId, period]);

  return (
    <div>
      <select value={period} onChange={(e) => setPeriod(Number(e.target.value))}>
        <option value={7}>Last 7 days</option>
        <option value={30}>Last 30 days</option>
        <option value={90}>Last 90 days</option>
      </select>

      <DeveloperContributions
        teamId={teamId}
        developers={developers}
        period={period}
        onDeveloperClick={(devId) => {
          // Show developer detail page
          window.location.href = `/developers/${devId}`;
        }}
      />
    </div>
  );
};
```

---

## Complete Dashboard Integration

Here's a full dashboard component combining all three:

```typescript
import React, { useState, useEffect } from 'react';
import CAQIGauge from '@/components/CAQIGauge';
import AnomaliesTable from '@/components/AnomaliesTable';
import DeveloperContributions from '@/components/DeveloperContributions';
import { apiClient, TeamCAQI, Anomaly, Developer } from '@/services/apiClient';

interface DashboardState {
  caqi: TeamCAQI | null;
  anomalies: Anomaly[];
  developers: Developer[];
  loading: boolean;
  error: string | null;
}

export const Dashboard = ({ teamId }: { teamId: string }) => {
  const [state, setState] = useState<DashboardState>({
    caqi: null,
    anomalies: [],
    developers: [],
    loading: true,
    error: null,
  });

  const [filters, setFilters] = useState({
    anomalySeverity: undefined,
    anomalyReviewed: undefined,
    developerPeriod: 30,
  });

  // Load all data
  useEffect(() => {
    const loadData = async () => {
      try {
        setState((prev) => ({ ...prev, loading: true, error: null }));

        const [caqi, anomalies, developers] = await Promise.all([
          apiClient.getTeamCAQI(teamId),
          apiClient.getAnomalies(
            teamId,
            filters.anomalySeverity as any,
            filters.anomalyReviewed
          ),
          apiClient.getDeveloperContributions(teamId, filters.developerPeriod),
        ]);

        setState({
          caqi,
          anomalies,
          developers,
          loading: false,
          error: null,
        });
      } catch (error) {
        setState((prev) => ({
          ...prev,
          loading: false,
          error: error instanceof Error ? error.message : 'Unknown error',
        }));
      }
    };

    loadData();
  }, [teamId, filters]);

  if (state.loading) {
    return <div className="dashboard-loading">Loading dashboard...</div>;
  }

  if (state.error) {
    return <div className="dashboard-error">Error: {state.error}</div>;
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>{teamId} - Code Quality Dashboard</h1>
      </header>

      <section className="dashboard-section">
        <h2>Overall Score</h2>
        {state.caqi && (
          <CAQIGauge
            teamId={state.caqi.team_id}
            overallCaqi={state.caqi.overall_caqi}
            dimensions={state.caqi.dimensions}
            calculatedAt={state.caqi.calculated_at}
            onDimensionClick={(dim) => {
              console.log(`Viewing dimension: ${dim}`);
            }}
          />
        )}
      </section>

      <section className="dashboard-section">
        <h2>Anomalies & Issues</h2>
        <AnomaliesTable
          teamId={teamId}
          anomalies={state.anomalies}
          onReviewAnomaly={async (id, notes) => {
            await apiClient.reviewAnomaly(teamId, id, notes);
            // Refresh anomalies
            const updated = await apiClient.getAnomalies(
              teamId,
              filters.anomalySeverity as any,
              filters.anomalyReviewed
            );
            setState((prev) => ({ ...prev, anomalies: updated }));
          }}
          onFilterChange={(newFilters) => {
            setFilters((prev) => ({
              ...prev,
              anomalySeverity: newFilters.severity,
              anomalyReviewed: newFilters.reviewed,
            }));
          }}
        />
      </section>

      <section className="dashboard-section">
        <h2>Developer Impact</h2>
        <DeveloperContributions
          teamId={teamId}
          developers={state.developers}
          period={filters.developerPeriod}
          onDeveloperClick={(devId) => {
            console.log(`Viewing developer: ${devId}`);
          }}
        />
      </section>
    </div>
  );
};

export default Dashboard;
```

### Styling the Dashboard
```css
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  background: #f5f5f5;
}

.dashboard-header {
  margin-bottom: 40px;
}

.dashboard-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.dashboard-section {
  margin-bottom: 40px;
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.dashboard-section h2 {
  font-size: 20px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 20px 0;
}

.dashboard-loading,
.dashboard-error {
  text-align: center;
  padding: 60px 20px;
  font-size: 18px;
  color: #6b7280;
}

.dashboard-error {
  color: #dc2626;
  background: #fee2e2;
  border-radius: 12px;
}
```

---

## Component Composition Patterns

### Pattern 1: Isolated Components
Use components independently for specific views:
```typescript
// Just the CAQI gauge
<CAQIGauge {...props} />

// Just the anomalies table
<AnomaliesTable {...props} />

// Just developer contributions
<DeveloperContributions {...props} />
```

### Pattern 2: Side-by-Side Layout
```typescript
<div className="grid grid-cols-2 gap-8">
  <div>
    <CAQIGauge {...props} />
  </div>
  <div>
    <AnomaliesTable {...props} />
  </div>
</div>
```

### Pattern 3: Tabs
```typescript
const [activeTab, setActiveTab] = useState('caqi');

return (
  <div>
    <div className="tabs">
      <button onClick={() => setActiveTab('caqi')}>Quality Score</button>
      <button onClick={() => setActiveTab('anomalies')}>Issues</button>
      <button onClick={() => setActiveTab('developers')}>Team</button>
    </div>

    {activeTab === 'caqi' && <CAQIGauge {...props} />}
    {activeTab === 'anomalies' && <AnomaliesTable {...props} />}
    {activeTab === 'developers' && <DeveloperContributions {...props} />}
  </div>
);
```

---

## Data Flow Diagram

```
Dashboard Component
    ↓
┌───────────────────────────────────────────┐
│ Load Data via apiClient                   │
├───────────────────────────────────────────┤
│ ├─ getTeamCAQI()                          │
│ ├─ getAnomalies()                         │
│ └─ getDeveloperContributions()            │
└───────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────┐
│ Update Component State                    │
└───────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────┐
│ Render Components                         │
├───────────────────────────────────────────┤
│ ├─ CAQIGauge                              │
│ ├─ AnomaliesTable                         │
│ └─ DeveloperContributions                 │
└───────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────┐
│ User Interactions                         │
├───────────────────────────────────────────┤
│ ├─ onDimensionClick()                     │
│ ├─ onReviewAnomaly()                      │
│ ├─ onFilterChange()                       │
│ └─ onDeveloperClick()                     │
└───────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────┐
│ Update State & Refetch                    │
└───────────────────────────────────────────┘
```

---

## Accessibility Features

All components include:
- ✅ Keyboard navigation (Tab, Enter, Space)
- ✅ ARIA labels and roles
- ✅ Color contrast (WCAG AA)
- ✅ Focus indicators
- ✅ Screen reader support
- ✅ Semantic HTML

---

## Performance Tips

1. **Memoize components** to prevent unnecessary re-renders:
   ```typescript
   const MemoizedDashboard = React.memo(Dashboard);
   ```

2. **Use useCallback** for event handlers:
   ```typescript
   const handleReview = useCallback((id) => {
     apiClient.reviewAnomaly(teamId, id);
   }, [teamId]);
   ```

3. **Lazy load sections** below the fold:
   ```typescript
   const DeveloperSection = lazy(() => import('./DeveloperSection'));
   ```

---

**Last Updated:** 2026-06-06
