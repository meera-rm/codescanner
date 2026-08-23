# Phase 4.1: Visual Dashboard — Implementation Plan

**Task:** Build interactive real-time dashboard for iteration progress  
**Effort:** 40 hours  
**Status:** In Progress  
**Start Date:** 2026-07-05

---

## Dashboard Requirements

### Core Views

#### 1. Job Status Dashboard (Main View)
**URL:** `/dashboard/{job_id}`

**Displays:**
- Current grade (large, prominent)
- Starting grade → Final grade (grade progression)
- Quality score (0-100 with colored bar)
- Iteration progress (1/10 iterations complete)
- Time elapsed
- Estimated time remaining

**Layout:**
```
┌─────────────────────────────────────────┐
│  Job: iterate_a1b2c3d4                  │
├─────────────────────────────────────────┤
│  Grade Progress                          │
│  C (72) → B- → B → B+ → A (95)          │
│  ████████████░░░░░░░░░░░░░░░ 40%       │
├─────────────────────────────────────────┤
│  Current Status                          │
│  Iteration 4/10 | Grade: B+ | Time: 2m  │
├─────────────────────────────────────────┤
│  Quality Score: 88/100                   │
│  ████████████░░░░░░░░░░░░░░░░░░░░░░░░  │
└─────────────────────────────────────────┘
```

#### 2. Iteration History Timeline
**Shows:** Each iteration as a card in a vertical timeline

**Per Iteration:**
- Iteration number (e.g., "Iteration 3")
- Grade change (e.g., "B → B+")
- Issues fixed (e.g., "8 issues")
- Agent used (e.g., "Agent A - Simplicity First")
- Agent strategy (e.g., "Extracted helper functions")
- Time taken (e.g., "2.3s")
- Validation status (✅ Passed)

**Timeline:**
```
Iteration 1: C → B-
├─ Agent: A (Simplicity)
├─ Fixed: 5 issues
├─ Time: 2.1s
└─ ✅ Validation: PASSED

Iteration 2: B- → B
├─ Agent: A (Simplicity)
├─ Fixed: 6 issues
├─ Time: 2.5s
└─ ✅ Validation: PASSED

... (vertical timeline continues)
```

#### 3. Metrics & Statistics
**Displays:**
- Total issues fixed (cumulative)
- Average complexity reduction per iteration
- Agent selection frequency (pie chart: Agent A 60%, B 30%, C 10%)
- Success rate (X% of suggestions validated)
- Average iteration time

#### 4. Real-Time Updates
**Auto-refresh:** Every 1 second while job is processing

**WebSocket Alternative:** If job is long-running, WebSocket for push updates

**Fallback:** REST API polling with exponential backoff

---

## Technical Stack

### Frontend
- **Framework:** React 18+ (TypeScript preferred)
- **UI Components:** Recharts (charts), React Bootstrap or Material-UI (layout)
- **State Management:** React Hooks + Context API
- **API Client:** Fetch or Axios with auto-retry
- **Charts:**
  - Line chart: Grade progression over iterations
  - Pie chart: Agent selection distribution
  - Bar chart: Issues fixed per iteration

### Backend (No Changes Needed)
- REST API already provides job status and history
- No additional endpoints required
- Current endpoints sufficient:
  - `GET /api/v1/iteration/{job_id}` — Full status + history
  - `GET /api/v1/iteration/{job_id}/progress` — Lightweight updates

### Styling
- **CSS Framework:** Tailwind CSS (recommended) or Bootstrap
- **Responsive:** Mobile-first design
- **Dark Mode:** Toggle between light/dark themes
- **Charts:** Recharts with custom styling

---

## Implementation Phases

### Phase 4.1a: Basic Layout & API Integration (8 hours)
**Deliverable:** Static dashboard with hard-coded data

1. Create React component structure
2. Build layout with grade display
3. Integrate with REST API
4. Display job metadata (ID, status, times)
5. Test API calls and error handling

**Files to Create:**
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/components/JobHeader.tsx`
- `frontend/src/components/IterationTimeline.tsx`
- `frontend/src/services/iterationApi.ts`

### Phase 4.1b: Charts & Visualizations (12 hours)
**Deliverable:** Interactive charts showing iteration progress

1. Grade progression line chart
2. Issue count chart
3. Agent selection pie chart
4. Metrics summary cards
5. Responsive design for mobile

**Files to Create:**
- `frontend/src/components/GradeChart.tsx`
- `frontend/src/components/IssuesChart.tsx`
- `frontend/src/components/MetricsCards.tsx`
- `frontend/src/styles/dashboard.css`

### Phase 4.1c: Real-Time Updates (10 hours)
**Deliverable:** Live-updating dashboard as job runs

1. Auto-refresh every 1 second
2. Smooth animations on updates
3. Handle job completion/failure
4. Show estimated time remaining
5. Skeleton loading states

**Files to Create:**
- `frontend/src/hooks/useJobPolling.ts`
- `frontend/src/components/LoadingSkeletons.tsx`
- Update existing components with animation

### Phase 4.1d: UI Polish & Testing (10 hours)
**Deliverable:** Production-ready dashboard

1. Theme switching (light/dark mode)
2. Error boundaries and error messages
3. Loading and empty states
4. Mobile responsive testing
5. Performance optimization
6. E2E tests with Cypress/Playwright

**Files to Create:**
- `frontend/src/hooks/useTheme.ts`
- `frontend/src/components/ErrorBoundary.tsx`
- `frontend/tests/dashboard.test.tsx`

---

## API Integration Details

### GET `/api/v1/iteration/{job_id}` Response Used

```json
{
  "job_id": "iterate_a1b2c3d4",
  "status": "processing",
  "start_grade": "C",
  "final_grade": "B+",
  "grade_improvement": 16,
  "iterations_count": 3,
  "max_iterations": 10,
  "current_iteration": 3,
  "target_grade": "A",
  "progress_percent": 30,
  "history": [
    {
      "iteration_number": 1,
      "grade_before": "C",
      "grade_after": "B-",
      "issues_fixed": 5,
      "agent_selected": "Agent A (Simplicity First)",
      "fix_description": "Extracted 3 helper functions",
      "validation_passed": true,
      "applied_at": "2026-07-05T10:23:45Z"
    },
    ...
  ],
  "metrics": {
    "total_iterations": 3,
    "total_issues_fixed": 18,
    "complexity_reduction": "28 → 18 (36%)",
    "agents_used": ["Agent A", "Agent B"]
  },
  "created_at": "2026-07-05T10:20:00Z",
  "started_at": "2026-07-05T10:20:15Z",
  "completed_at": null
}
```

---

## File Structure

```
frontend/
├── src/
│   ├── pages/
│   │   └── DashboardPage.tsx          (Main dashboard page)
│   ├── components/
│   │   ├── JobHeader.tsx              (Top section with grade)
│   │   ├── GradeChart.tsx             (Line chart progression)
│   │   ├── IssuesChart.tsx            (Issues fixed bar chart)
│   │   ├── AgentPieChart.tsx          (Agent selection)
│   │   ├── IterationTimeline.tsx      (Iteration cards)
│   │   ├── MetricsCards.tsx           (Statistics)
│   │   ├── LoadingSkeletons.tsx       (Loading states)
│   │   ├── ErrorBoundary.tsx          (Error handling)
│   │   └── ThemeToggle.tsx            (Dark mode)
│   ├── hooks/
│   │   ├── useJobPolling.ts           (Auto-refresh logic)
│   │   └── useTheme.ts                (Theme management)
│   ├── services/
│   │   └── iterationApi.ts            (API calls)
│   ├── styles/
│   │   ├── dashboard.css              (Dashboard styles)
│   │   └── animations.css             (Smooth transitions)
│   └── types/
│       └── iteration.ts               (TypeScript types)
└── tests/
    └── dashboard.test.tsx             (Component tests)
```

---

## Success Criteria

- ✅ Dashboard displays real job status
- ✅ Grade progression visible with chart
- ✅ Iteration timeline shows all history
- ✅ Auto-refreshes every 1 second
- ✅ Mobile responsive (tested on mobile devices)
- ✅ Handles job completion state
- ✅ Shows error messages gracefully
- ✅ < 100ms response time
- ✅ Dark mode toggle works
- ✅ E2E tests passing (Cypress)

---

## Next Steps

1. Set up React project structure
2. Create API service with TypeScript types
3. Build basic layout component
4. Integrate with real API
5. Add charts using Recharts
6. Implement auto-refresh
7. Add error handling and loading states
8. Test on mobile devices
9. Write E2E tests
10. Polish UI and animations

