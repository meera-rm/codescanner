---
created_at: 2026-06-12T18:16:43Z
title: Phase 3.5 Realtime Analysis Plan
source: claude-code
project: codescanner
---

# Phase 3.5: Real-time Code Analysis Implementation Plan

**Scope:** Add live code editor with instant scanning and quality feedback  
**Effort:** 4-6 sprints  
**Integration:** Parallel stream alongside current project scanning

---

## Architecture Decision

### Hybrid Approach: Live Editor Tab + Snippet Analysis

**Design:**
- Add "Live Editor" tab to CodeScanner.tsx alongside existing tabs (Overview, Complexity, Smells, etc.)
- Lightweight API endpoint `/api/v1/scanner/analyze-snippet` for code fragments
- Client-side debouncing (300ms) to reduce server load
- Results cached in localStorage by code hash for repeat patterns
- No database persistence—ephemeral analysis per session

**Why this approach:**
1. **Minimal disruption**: Doesn't replace existing project workflow
2. **Fast feedback**: Snippet analysis < 500ms vs. full project scan (2-5s)
3. **Composable**: Works with current hooks architecture
4. **Testable**: Separate from project-level scanning logic

---

## New Components & Hooks

### Frontend (React)

**New Hook: `useLiveCodeAnalysis.ts`**
```typescript
interface LiveAnalysisResult {
  quality_score: number;
  complexity: number;
  issues: Array<{
    type: string;      // 'security', 'style', 'complexity'
    severity: string;  // 'CRITICAL', 'WARNING', 'INFO'
    message: string;
    line?: number;
  }>;
  detectedLanguage?: 'python' | 'javascript' | 'sql';
  executionTime: number;
}

useLiveCodeAnalysis(code: string, language: string):
  - analysisResult: LiveAnalysisResult | null
  - isAnalyzing: boolean
  - error: string | null
  - abortAnalysis: () => void
```

**Features:**
- Internal debounce (300ms, configurable)
- Cache layer: key = `sha256(code)` → result
- Abort previous requests if new code arrives
- Return null while debouncing (no stale results)

---

**New Component: `LiveCodeEditor.tsx`**
```typescript
interface LiveCodeEditorProps {
  onAnalysisResult: (result: LiveAnalysisResult) => void;
  initialCode?: string;
  language?: 'python' | 'javascript' | 'sql';
}
```

**Features:**
- Syntax highlighting (react-syntax-highlighter)
- Language selector dropdown
- Split view: code (left) + metrics (right)
- Copy/clear buttons
- Quick action buttons: "Refactor This" → opens refactor modal
- Metrics panel shows: Quality score, Complexity, Issue count by severity

---

**New Component: `LiveMetricsPanel.tsx`**
```typescript
interface MetricsPanelProps {
  analysis: LiveAnalysisResult;
  isAnalyzing: boolean;
  code: string;
}
```

**Features:**
- 3 gauge charts: Quality (0-100), Complexity (0-50), Security risk (0-100)
- Issue breakdown: 3 bars (CRITICAL, WARNING, INFO)
- Line-by-line annotations in code editor
- "Fix This Issue" button for each finding

---

### Backend (FastAPI)

**New Route: `POST /api/v1/scanner/analyze-snippet`**
```json
Request:
{
  "code": "def foo(x):\n    if x > 0:\n        return x\n    else:\n        return -x",
  "language": "python",
  "include_metrics": ["quality_score", "complexity", "security"]
}

Response:
{
  "quality_score": 75,
  "complexity": 3,
  "issues": [
    {
      "type": "complexity",
      "severity": "WARNING",
      "message": "Function has 2 paths; keep under 10",
      "line": 1
    }
  ],
  "detectedLanguage": "python",
  "executionTime": 0.045
}
```

**Implementation:**
- Extract logic from `PythonScanner.scan_file()` → reusable `analyze_code_string()` method
- No file I/O, no imports to discover
- Return findings filtered to only detected language
- Validate max code length (10KB to prevent abuse)
- Response cached in Redis (optional, Phase 3.5.1)

---

## Debounce Strategy

**Client-side debounce only** (simplest, works for MVP):
- Editor onChange → queue analysis
- Wait 300ms with no new input
- Fire API call
- Show spinner while pending
- Cache result by code hash
- If user types again before result → cancel previous request

**Future optimization (Phase 3.5.1):**
- Add Redis cache layer: `cache_key = hash(code + language)` → TTL 1 hour
- Return cached result immediately if available
- Only hit scanner if cache miss

**Why not debounce on server:**
- Server can't know when user stops typing
- Client debounce is simpler, faster, more transparent

---

## Metrics for Real-time Feedback

**Priority ranking (MVP includes first 4):**

1. **Quality Score** (0-100) — Aggregate health metric
   - Weighted sum: security (40%), complexity (30%), coverage (20%), style (10%)
   - Update every keystroke

2. **Complexity** (cyclomatic) — Per-function or snippet-level
   - Alert if > 10 (hard to test)
   - Show per-line paths for if/elif/else chains

3. **Security Issues** (count) — Hardcoded secrets, injection risks
   - Show as CRITICAL count
   - Highlight in editor

4. **Code Smells** (count) — Dead code, unused variables, long functions
   - Show as WARNING count
   - Categorize by type

5. **Code Duplication** (%) — Repeated patterns in snippet
   - Low priority for snippets (better at file level)
   - Deferred to Phase 3.5.1

---

## New API Endpoints Summary

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/scanner/analyze-snippet` | Analyze code string, return metrics |
| GET | `/api/v1/scanner/snippet-cache/{hash}` | Retrieve cached result (optional) |
| DELETE | `/api/v1/scanner/snippet-cache/{hash}` | Clear cache (optional) |

**API contract notes:**
- Snippet max 10KB (enforced in validation)
- Language detection optional (can be specified)
- All results include `executionTime` for perf tracking
- No auth required for MVP (enable in Phase 3.5.1)

---

## UX Flow

**1. User opens CodeScanner → clicks "Live Editor" tab**
- Empty editor with language selector
- Placeholder: "Paste or type code to analyze"

**2. User pastes code**
- Syntax highlighting applied immediately
- Spinner shows "Analyzing..."
- After 300ms idle: API call fires

**3. Results appear (< 500ms)**
- Left: Code with issue annotations (red/yellow squiggles)
- Right: Quality gauge, complexity graph, issue list
- Each issue has "Fix This" button

**4. User clicks "Fix This"**
- Opens refactor modal (existing) with code pre-filled
- Returns to editor with refactored code option
- User can apply or keep original

**5. History (Phase 3.5.1)**
- Recent snippets in sidebar (name, language, grade)
- Click to restore analysis
- localStorage: max 20 saved snippets

---

## Implementation Phases

### Phase 3.5.0 (MVP: 1 sprint)
- [ ] `useLiveCodeAnalysis` hook (debounce + cache)
- [ ] `LiveCodeEditor` component (CodeMirror or ace editor)
- [ ] `LiveMetricsPanel` component (gauges + issue list)
- [ ] `POST /api/v1/scanner/analyze-snippet` endpoint
- [ ] Tab integration in CodeScanner.tsx
- [ ] 5 unit tests + 2 integration tests

### Phase 3.5.1 (Polish: 1-2 sprints)
- [ ] Redis caching layer
- [ ] Recent snippets history (localStorage sidebar)
- [ ] Auth + rate limiting for API
- [ ] Performance monitoring (log execution times)
- [ ] Error recovery (retry + fallback)

### Phase 3.5.2 (Advanced: 2 sprints)
- [ ] Multi-file snippet (analyze entire module)
- [ ] Inline refactor suggestions (AI)
- [ ] Diff viewer (original vs. refactored)
- [ ] Export snippet + analysis as PDF

---

## Expected Outcomes

**User Experience:**
- Type/paste code → get instant feedback (< 500ms)
- See quality score trend as code improves
- One-click refactor with instant re-analysis
- No context switching between project scanner + editor

**Technical:**
- Reusable snippet analysis logic (base for future CLI `--live` mode)
- Separate test suite for live analysis (10-15 tests)
- <100ms avg response time for snippets < 1KB
- 90%+ cache hit rate for repeated patterns

**Metrics:**
- 30% faster iteration cycle (snippet feedback vs. full project scan)
- 80%+ user adoption for quick edits
- Quality score improvement: avg B+ → A- for active users

---

## Files to Create/Modify

### Create
- `frontend/src/hooks/useLiveCodeAnalysis.ts` (150 lines)
- `frontend/src/components/LiveCodeEditor.tsx` (250 lines)
- `frontend/src/components/LiveMetricsPanel.tsx` (180 lines)
- `api/routes/live_analysis.py` (80 lines)
- `api/services/snippet_analyzer.py` (120 lines)
- `tests/test_live_analysis_e2e.py` (60 lines)

### Modify
- `frontend/src/pages/CodeScanner.tsx` (+30 lines: add tab + state)
- `api/main.py` (+3 lines: include live_analysis router)
- `frontend/src/hooks/index.ts` (+2 lines: export new hook)

**Total LOC:** ~950 new + ~35 modified

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Snippet analysis too slow | Enforce 10KB max, use cached rules, timeout at 1s |
| High API load from rapid typing | Client debounce (300ms), cache by code hash |
| False positives on fragments | Skip import checking, context-agnostic rules only |
| UX confusion (live vs. project scan) | Clear tab naming, separate results pane |
| Storage bloat (cache) | Limit localStorage to 50 snippets max, cleanup old entries |

---

## Success Criteria

- [ ] Live analysis returns results < 500ms for snippets < 1KB
- [ ] Quality score updates visually as user edits (debounced, smooth)
- [ ] At least one security issue detected in test snippets
- [ ] Cache hits > 70% in QA testing
- [ ] Zero crashes on malformed code input
- [ ] All 15 tests pass, > 80% coverage for new code
