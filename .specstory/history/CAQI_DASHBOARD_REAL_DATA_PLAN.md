---
created_at: 2026-06-12T18:16:43Z
title: Caqi Dashboard Real Data Plan
source: claude-code
project: codescanner
---

# CAQI Dashboard: From Mock Data to Real Data
**Date:** June 7, 2026  
**Status:** ⏳ Planning Phase  
**Priority:** High - Improve user value

---

## The Problem

The CAQI Dashboard currently uses **mock data** (hardcoded teams with fake CAQI scores):

```json
{
  "team_id": "backend-team",
  "team_name": "Backend Engineering",
  "overall_caqi": 380,
  "dimensions": { ... }
}
```

### Why It Uses Mock Data

The CAQI Dashboard is designed for **team-level tracking over time**, which requires:

1. **Database storage** for teams
   - team_id, team_name, member_count
   - Team metadata and configuration

2. **Historical snapshots** of CAQI scores
   - Monthly/quarterly score records
   - Archetype changes over time

3. **Trend calculations**
   - How did quality change from Apr → May → Jun?
   - Which dimension improved/degraded?

The backend routes depend on a database:
```python
@router.get("/team/{team_id}")
async def get_team_caqi(team_id: str, db: Session = Depends(get_db)):
    service = TeamAggregationService(db)
    result = service.aggregate_team_scores(team_id)
    # Queries database for team data
```

**We haven't set up a database yet**, so it uses mock data as a placeholder.

---

## What We Should Do Instead

I propose we change the Dashboard to use **real codebase data**:

### Option 1: Simple Approach (Recommended) ⭐
**Analyze Multiple Codebases, Show Real Aggregated Metrics**

- Dashboard accepts multiple codebase paths
- Analyzes each codebase in parallel
- Treats each as a "team member"
- Aggregates their CAQI scores into team metrics
- Shows real data, no database needed
- Easy to implement, provides immediate value

**Example:**
```
Input: 
  - catfacts (CAQI: 212)
  - codescanner (CAQI: 438)
  - another-project (CAQI: 180)

Output:
  Team Avg CAQI: 277
  Team Health: Fair
  Member Breakdown: 3 projects analyzed
```

**Pros:**
- ✅ No database setup needed
- ✅ Real data immediately
- ✅ Fast to implement
- ✅ Works for multi-repo teams

**Cons:**
- ❌ No historical trend data
- ❌ Can't track changes over time

---

### Option 2: Full Team Tracking (More Complex)
**Set Up Database + Team Registration System**

- Set up SQLite or PostgreSQL database
- Create team registration system
- Allow users to add codebases to teams
- Track historical CAQI snapshots
- Calculate trends over time

**Example:**
```
Team: "Backend Engineering"
Members:
  - api-service (CAQI: 420)
  - database-layer (CAQI: 380)
  - auth-service (CAQI: 350)

Team CAQI: 383
Trend (last 3 months):
  Apr: 360 → May: 370 → Jun: 383
Status: Improving ↗️
```

**Pros:**
- ✅ Full historical tracking
- ✅ Trend analysis
- ✅ Team management UI
- ✅ Scalable for organizations

**Cons:**
- ❌ Database setup complexity
- ❌ More code to write
- ❌ Longer implementation time
- ❌ Requires migration management

---

## Recommendation: Implement Option 1 First

**Why:**
1. **Immediate value** - Real data now, not mock
2. **Fast delivery** - Can complete in hours, not days
3. **Low complexity** - No database, no migrations
4. **User-friendly** - Simple input (paste codebase paths)
5. **Can upgrade later** - Option 2 builds on this

**Implementation Plan for Option 1:**

1. **Create `MultiRepoAnalyzer` component**
   - Input: List of codebase paths (comma-separated or line-by-line)
   - Button: "Analyze Team"
   - State: Track analysis progress for each repo

2. **Parallel Analysis**
   - Send POST requests for each codebase
   - Track all job_ids
   - Poll for completion concurrently
   - Display progress: "Analyzed 2/3 codebases"

3. **Aggregation**
   - Collect all CAQI results
   - Calculate team-level metrics:
     - Average CAQI score
     - Min/Max scores
     - Aggregated dimensions (avg security, complexity, etc.)
     - Overall team health status

4. **Display**
   - Team comparison table (each codebase as a row)
   - Aggregated radar chart
   - Team-level health gauge
   - Dimension breakdown

5. **Visualization**
   - Reuse existing charts (Recharts)
   - Show individual codebase scores
   - Show team aggregates
   - Color-code by health status

---

## Implementation Steps

### Step 1: Create MultiRepoAnalyzer Component
- Input field for comma-separated paths or textarea
- "Analyze Team" button
- Progress indicator
- Results display

### Step 2: Implement Parallel Analysis
- Submit multiple analysis jobs simultaneously
- Track all job IDs
- Poll all in parallel
- Show progress: "1/3 analyzed, 2/3 analyzed, etc."

### Step 3: Aggregation Logic
```typescript
function aggregateTeamMetrics(caqi_results: CAQIData[]): TeamMetrics {
  return {
    team_caqi: avg(caqi_results.map(c => c.score)),
    team_level: determineLevel(team_caqi),
    dimensions: {
      complexity: avg(caqi_results.map(c => c.pollutants.complexity)),
      security: avg(caqi_results.map(c => c.pollutants.security)),
      smells: avg(caqi_results.map(c => c.pollutants.smells)),
      docs: avg(caqi_results.map(c => c.pollutants.docs)),
      duplication: avg(caqi_results.map(c => c.pollutants.duplication)),
      coupling: avg(caqi_results.map(c => c.pollutants.coupling)),
    },
    members: caqi_results,
    analyzed_at: new Date()
  }
}
```

### Step 4: Display Results
- Table: One row per codebase, columns for CAQI + 6 dimensions
- Team-level summary card
- Radar chart of aggregated metrics
- Health status indicator

---

## Current State

**Live Now:**
- ✅ CAQIAnalyzer: Analyzes single codebase (real data)
- ✅ CAQIDashboard: Team comparison (mock data)
- ✅ CAQILanding: Choose between both options

**To Do:**
- ⏳ Replace CAQIDashboard mock data with real multi-codebase analysis
- ⏳ Add input form for multiple codebases
- ⏳ Implement parallel analysis
- ⏳ Build aggregation logic
- ⏳ Visualize team-level metrics

---

## Decision Required

**Which approach do you prefer?**

- **Option 1 (Recommended):** Implement real multi-codebase analysis now
  - Timeline: ~2-3 hours
  - Complexity: Low
  - Immediate value: High

- **Option 2:** Set up full database + team tracking system
  - Timeline: ~8-12 hours
  - Complexity: High
  - Immediate value: Medium (but future value: Very High)

---

## References

- **CAQI Analyzer:** Real single-codebase analysis (working)
- **CAQI Dashboard:** Team comparison with mock data (current)
- **Backend:** `/api/v1/creative-suite/analyze` returns real CAQI
- **Frontend:** CAQIDashboard.tsx uses mock data (lines 84-133)

---

**Last Updated:** 2026-06-07  
**Owner:** Code Quality Initiative  
**Status:** Awaiting decision for next phase
