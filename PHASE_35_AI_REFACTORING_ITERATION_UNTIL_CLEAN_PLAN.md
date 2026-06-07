# PHASE 3.5: AI Refactoring - Iteration Until Clean Design & Plan

**Project:** CODEPULSE AI Code Intelligence Platform  
**Phase:** 3.5 (Core Differentiator)  
**Status:** Planning COMPLETE ✅  
**Timeline:** 70-100 hours (1.5-2 weeks)  
**Priority:** CRITICAL — Differentiates CodePulse from all other scanners

---

## Purpose of Phase 3.5

**Iteration Until Clean** is the feature that makes CodePulse AI unique. Instead of finding bugs and letting developers fix them manually, CodePulse automatically improves code from its current grade (C, B-, B, etc.) up to Grade A through an intelligent multi-agent refactoring loop.

From CODEPULSE_AI_FEATURE_SET.md:
> "The ability to iteratively fix code until it reaches a target grade is what differentiates CodePulse AI from other linters."

---

## Executive Summary

### The Problem It Solves

**Current workflow (developers + other tools):**
```
1. Run linter → Find 20+ issues
2. Read findings → Understand each issue
3. Manually fix each issue → Hours of work
4. Verify no regressions → Test suite
5. Repeat if new issues appear → More hours
Total time: 2-4 hours per codebase
```

**CodePulse Iteration Until Clean:**
```
1. Run CodePulse with --fix-until-clean
2. System automatically improves code
3. Multi-agent safety review (3 perspectives + validation)
4. Apply best fix
5. Rescan and repeat
Total time: 15 minutes, zero manual work
```

### What Gets Built

| Component | Purpose |
|-----------|---------|
| **3 Refactoring Agents** | Independent perspectives (Simplicity, Architecture, Performance) |
| **Evaluation Agent** | Scores and picks best suggestion |
| **Validator Agent** | Ensures no errors before applying |
| **IterationCleanService** | Orchestrates the improvement loop |
| **REST API Endpoints** | /api/v1/iteration/fix-until-clean, /api/v1/iteration/{job_id} |
| **Job Tracking** | Database persistence of iteration history |
| **Background Tasks** | Celery integration for long-running iterations |

---

## Architecture Overview

### System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    ITERATION UNTIL CLEAN LOOP                   │
└─────────────────────────────────────────────────────────────────┘

USER INITIATES
  ↓
POST /api/v1/iteration/fix-until-clean
  ├─ directory_path: str
  ├─ target_grade: str = "A"
  └─ max_iterations: int = 10
  ↓
Returns job_id for tracking
  ↓
BACKGROUND TASK STARTS (Celery)
  ↓
┌──────────────────────────────────────────────────────────────┐
│                   ITERATION LOOP (0 to max)                   │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  STEP 1: SCAN & ASSESS                                       │
│  ├─ Scan codebase with full analyzer                        │
│  ├─ Calculate current grade (A, B-, C, etc.)               │
│  ├─ Identify all issues (23 issues, 15 smells, etc.)      │
│  └─ Check if target reached → EXIT LOOP if yes             │
│                                                               │
│  STEP 2: GENERATE SUGGESTIONS (PARALLEL)                   │
│  ├─ Agent A (Simplicity):                                  │
│  │  └─ "Extract 3 helper functions from analyze_code()"   │
│  ├─ Agent B (Architecture):                                │
│  │  └─ "Refactor into plugin-based architecture"          │
│  └─ Agent C (Performance):                                 │
│     └─ "Parallelize checks + add caching"                 │
│                                                               │
│  STEP 3: EVALUATE SUGGESTIONS                              │
│  ├─ Score each by:                                         │
│  │  ├─ Complexity reduction (30%)                          │
│  │  ├─ Risk level (40%)                                    │
│  │  ├─ Code clarity (20%)                                  │
│  │  └─ Implementation time (10%)                           │
│  └─ Pick best: AGENT A (score 78/100 - safest)           │
│                                                               │
│  STEP 4: VALIDATE SUGGESTION                               │
│  ├─ Syntax check:           ✅ PASS                        │
│  ├─ Import validation:      ✅ PASS                        │
│  ├─ Logic preservation:     ✅ PASS                        │
│  ├─ Test regression:        ✅ PASS                        │
│  └─ Performance impact:     ✅ PASS                        │
│     → APPROVED: Apply this fix                             │
│                                                               │
│  STEP 5: APPLY & RESCAN                                    │
│  ├─ Write changes to files                                 │
│  ├─ Scan entire codebase                                   │
│  ├─ Calculate new grade: B- (78/100) [+6 pts, -5 issues] │
│  └─ Log iteration history                                  │
│                                                               │
│  STEP 6: NEXT ITERATION (Loop back to STEP 1)             │
│                                                               │
└──────────────────────────────────────────────────────────────┘
  ↓
TARGET REACHED or MAX ITERATIONS HIT
  ↓
GENERATE FINAL REPORT
  ├─ Grade progression: C (72) → A (95)
  ├─ Improvement: +23 points
  ├─ Issues fixed: 23 → 0
  ├─ Complexity reduction: 71%
  ├─ Iteration history (4 iterations)
  └─ Metrics summary
  ↓
RETURN RESULT TO USER
```

---

## Detailed Component Design

### 1. Refactoring Agents

Three independent agents, each with different strategies.

#### Agent A: Simplicity First

**Philosophy:** Minimal changes, maximum clarity, low risk

```python
class AgentA_SimplityFirst:
    """Simplicity-first refactoring strategy."""
    
    async def suggest_refactoring(self, 
                                  codebase_path: str,
                                  issues: List[Issue]) -> Suggestion:
        """Generate refactoring suggestion focused on simplicity."""
        
        # Strategy: Find the most complex function and extract methods
        # Example issues: [ComplexityIssue(...), DuplicationIssue(...)]
        
        # Analysis: Which function has highest complexity?
        target_func = max(issues, key=lambda x: x.complexity)
        
        # Suggestion: Break it into smaller functions
        return Suggestion(
            agent="A (Simplicity)",
            description="Extract 3 helper functions from analyze_code()",
            changes=[
                "New: check_syntax() - validates syntax only",
                "New: check_security() - checks security issues",
                "New: check_complexity() - checks code complexity",
                "Modified: analyze_code() - orchestrates above"
            ],
            complexity_reduction=60,      # %
            risk_level="low",
            clarity_improvement="good",
            estimated_time="15 minutes"
        )
```

**Strengths:**
- Low risk of errors
- Easy to review
- Clear diffs
- Conservative approach

**Use Cases:**
- First iteration (safest)
- When code needs basic cleanup
- Conservative teams

#### Agent B: Architecture Focused

**Philosophy:** Long-term structure, optimization, maintainability

```python
class AgentB_ArchitectureFocused:
    """Architecture-focused refactoring strategy."""
    
    async def suggest_refactoring(self,
                                  codebase_path: str,
                                  issues: List[Issue]) -> Suggestion:
        """Generate refactoring suggestion focused on architecture."""
        
        # Strategy: Redesign entire module for better structure
        # Example: Convert monolithic function to plugin architecture
        
        return Suggestion(
            agent="B (Architecture)",
            description="Refactor into plugin-based architecture",
            changes=[
                "New: BaseAnalyzer class (plugin interface)",
                "New: SyntaxAnalyzer plugin",
                "New: SecurityAnalyzer plugin",
                "New: ComplexityAnalyzer plugin",
                "Modified: Main coordinator - uses plugins"
            ],
            complexity_reduction=70,
            risk_level="medium",
            clarity_improvement="excellent",
            estimated_time="1 hour"
        )
```

**Strengths:**
- Better long-term structure
- Improved maintainability
- Extensibility
- Professional design patterns

**Use Cases:**
- When redesign makes sense
- Growing codebases
- Teams ready for architectural changes

#### Agent C: Performance Optimized

**Philosophy:** Speed, efficiency, resource optimization

```python
class AgentC_PerformanceOptimized:
    """Performance-optimized refactoring strategy."""
    
    async def suggest_refactoring(self,
                                  codebase_path: str,
                                  issues: List[Issue]) -> Suggestion:
        """Generate refactoring suggestion focused on performance."""
        
        # Strategy: Add parallelization and caching
        
        return Suggestion(
            agent="C (Performance)",
            description="Parallelize checks and cache results",
            changes=[
                "New: async/await for concurrent checks",
                "New: @lru_cache decorator for repeated checks",
                "Modified: analyze_code() - now runs checks in parallel",
                "New: Result caching by file hash"
            ],
            complexity_reduction=40,
            risk_level="low",
            clarity_improvement="good",
            estimated_time="30 minutes"
        )
```

**Strengths:**
- Better performance
- Lower resource usage
- Async patterns
- Good for large codebases

**Use Cases:**
- Large codebases with performance concerns
- Teams familiar with async patterns
- When speed is bottleneck

---

### 2. Evaluation Agent

Scores and compares all suggestions to pick the best one.

```python
class EvaluationAgent:
    """Evaluate and score refactoring suggestions."""
    
    WEIGHTS = {
        "complexity_reduction": 0.30,  # 30%
        "risk_level": 0.40,            # 40%
        "clarity_improvement": 0.20,   # 20%
        "implementation_time": 0.10    # 10%
    }
    
    def pick_best(self, suggestions: List[Suggestion]) -> Suggestion:
        """Score all suggestions and return best."""
        
        scores = []
        for suggestion in suggestions:
            score = self._calculate_score(suggestion)
            scores.append((suggestion, score))
        
        # Return highest scored suggestion
        best = max(scores, key=lambda x: x[1])
        return best[0]
    
    def _calculate_score(self, suggestion: Suggestion) -> float:
        """Calculate composite score for suggestion."""
        
        # Normalize each dimension to 0-100
        complexity_score = suggestion.complexity_reduction  # Already 0-100
        risk_score = self._risk_to_score(suggestion.risk_level)  # low=100, med=60, high=20
        clarity_score = self._clarity_to_score(suggestion.clarity_improvement)  # good=75, excellent=100
        time_score = self._time_to_score(suggestion.estimated_time)  # quick=100, slow=20
        
        # Weighted sum
        total = (
            complexity_score * self.WEIGHTS["complexity_reduction"] +
            risk_score * self.WEIGHTS["risk_level"] +
            clarity_score * self.WEIGHTS["clarity_improvement"] +
            time_score * self.WEIGHTS["implementation_time"]
        )
        
        return total
    
    def _risk_to_score(self, risk: str) -> float:
        """Convert risk level to score."""
        return {"low": 100, "medium": 60, "high": 20}.get(risk, 0)
    
    def _clarity_to_score(self, clarity: str) -> float:
        """Convert clarity to score."""
        return {"good": 75, "excellent": 100, "ok": 50}.get(clarity, 0)
    
    def _time_to_score(self, time_str: str) -> float:
        """Convert time estimate to score (prefer quick)."""
        time_map = {
            "quick": 100,      # < 15 min
            "medium": 75,      # 15-30 min
            "slow": 50,        # 30-60 min
            "very slow": 20    # > 60 min
        }
        for key, score in time_map.items():
            if key in time_str.lower():
                return score
        return 50
```

**Scoring Example:**

```
Issue: Function analyze_code() complexity = 28 (too high)

Agent A Suggestion: Extract helper functions
  Complexity reduction: 60% × 0.30 = 18.0
  Risk (low) = 100 × 0.40 = 40.0
  Clarity (good) = 75 × 0.20 = 15.0
  Time (quick) = 100 × 0.10 = 10.0
  TOTAL: 83/100

Agent B Suggestion: Refactor to plugin architecture
  Complexity reduction: 70% × 0.30 = 21.0
  Risk (medium) = 60 × 0.40 = 24.0
  Clarity (excellent) = 100 × 0.20 = 20.0
  Time (slow) = 50 × 0.10 = 5.0
  TOTAL: 70/100

Agent C Suggestion: Parallelize and cache
  Complexity reduction: 40% × 0.30 = 12.0
  Risk (low) = 100 × 0.40 = 40.0
  Clarity (good) = 75 × 0.20 = 15.0
  Time (medium) = 75 × 0.10 = 7.5
  TOTAL: 74.5/100

WINNER: Agent A (83/100) - Best balance of improvement + safety
```

---

### 3. Validator Agent

Reviews chosen suggestion before applying to ensure safety.

```python
class ValidatorAgent:
    """Validate refactoring suggestions before applying."""
    
    async def validate(self, suggestion: Suggestion) -> ValidationResult:
        """Comprehensive validation checklist."""
        
        checks = []
        
        # 1. Syntax Check
        checks.append(await self._check_syntax(suggestion))
        
        # 2. Import Validation
        checks.append(await self._check_imports(suggestion))
        
        # 3. Logic Preservation
        checks.append(await self._check_logic(suggestion))
        
        # 4. Test Regression
        checks.append(await self._check_tests(suggestion))
        
        # 5. Performance Impact
        checks.append(await self._check_performance(suggestion))
        
        # All must pass
        approved = all(check["passed"] for check in checks)
        
        return ValidationResult(
            approved=approved,
            checks=checks,
            summary=self._summarize(checks)
        )
    
    async def _check_syntax(self, suggestion: Suggestion) -> Dict:
        """Validate Python syntax using AST."""
        try:
            import ast
            # Parse the modified code
            ast.parse(suggestion.modified_code)
            return {"passed": True, "check": "Syntax", "details": "Valid Python"}
        except SyntaxError as e:
            return {"passed": False, "check": "Syntax", "details": str(e)}
    
    async def _check_imports(self, suggestion: Suggestion) -> Dict:
        """Ensure all imports are defined."""
        missing = []
        for import_stmt in suggestion.new_imports:
            try:
                __import__(import_stmt)
            except ImportError:
                missing.append(import_stmt)
        
        if missing:
            return {"passed": False, "check": "Imports", "details": f"Missing: {missing}"}
        return {"passed": True, "check": "Imports", "details": "All imports available"}
    
    async def _check_logic(self, suggestion: Suggestion) -> Dict:
        """Verify input/output unchanged, side effects preserved."""
        # Compare function signatures, return types, side effects
        # Use AST analysis to ensure logic preservation
        
        # Placeholder: In real implementation, would use CFG analysis
        return {"passed": True, "check": "Logic", "details": "Input/output preserved"}
    
    async def _check_tests(self, suggestion: Suggestion) -> Dict:
        """Verify existing tests still pass."""
        try:
            # Run test suite against modified code
            # Placeholder: Would run pytest
            return {"passed": True, "check": "Tests", "details": "All tests pass"}
        except Exception as e:
            return {"passed": False, "check": "Tests", "details": str(e)}
    
    async def _check_performance(self, suggestion: Suggestion) -> Dict:
        """Ensure no performance regressions."""
        # Compare execution time, memory usage
        # Placeholder: Would benchmark before/after
        return {"passed": True, "check": "Performance", "details": "No regression"}
```

**Validation Checklist:**
```
✅ Syntax Check          — Python code is valid
✅ Import Validation     — All imports exist
✅ Logic Preservation    — Input/output unchanged
✅ Test Regression       — Existing tests still pass
✅ Performance Check     — No slowdowns
→ APPROVED: Safe to apply
```

---

### 4. IterationCleanService (Main Orchestrator)

Coordinates the entire loop.

```python
class IterationCleanService:
    """Orchestrate iteration until clean loop."""
    
    def __init__(self):
        self.refactoring_agents = [
            AgentA_SimplityFirst(),
            AgentB_ArchitectureFocused(),
            AgentC_PerformanceOptimized(),
        ]
        self.evaluator = EvaluationAgent()
        self.validator = ValidatorAgent()
        self.scanner = ScannerService()  # Full code analyzer
    
    async def fix_until_clean(self,
                             job_id: str,
                             codebase_path: str,
                             target_grade: str = "A",
                             max_iterations: int = 10) -> IterationResult:
        """Main loop: iterate until target grade reached."""
        
        iteration = 0
        current_grade = None
        history = []
        
        # Store in database for progress tracking
        job = IterationJob(
            job_id=job_id,
            codebase_path=codebase_path,
            target_grade=target_grade,
            max_iterations=max_iterations,
            status="in_progress"
        )
        db.add(job)
        
        while iteration < max_iterations:
            iteration += 1
            
            # STEP 1: SCAN & ASSESS
            scan_result = await self.scanner.scan(codebase_path)
            current_grade = scan_result["grade"]
            issues = scan_result["issues"]
            
            # Check if target reached
            if self._grade_value(current_grade) >= self._grade_value(target_grade):
                break
            
            # STEP 2: GENERATE SUGGESTIONS (PARALLEL)
            suggestions = await asyncio.gather(
                *[agent.suggest_refactoring(codebase_path, issues)
                  for agent in self.refactoring_agents]
            )
            suggestions = [s for s in suggestions if s]
            
            if not suggestions:
                break
            
            # STEP 3: EVALUATE
            best_suggestion = self.evaluator.pick_best(suggestions)
            
            # STEP 4: VALIDATE
            validation = await self.validator.validate(best_suggestion)
            
            if not validation["approved"]:
                # Skip and try next best
                suggestions.remove(best_suggestion)
                continue
            
            # STEP 5: APPLY & RESCAN
            await self._apply_fix(codebase_path, best_suggestion)
            rescan_result = await self.scanner.scan(codebase_path)
            new_grade = rescan_result["grade"]
            
            # Track iteration
            history.append({
                "iteration": iteration,
                "grade_before": current_grade,
                "grade_after": new_grade,
                "issues_fixed": len(issues) - len(rescan_result["issues"]),
                "agent_selected": best_suggestion.agent,
                "fix_description": best_suggestion.description,
                "validation_passed": True
            })
            
            # Update job in database
            job.current_iteration = iteration
            job.current_grade = new_grade
            job.history = history
            db.commit()
        
        # FINAL RESULT
        return IterationResult(
            job_id=job_id,
            status="completed",
            start_grade=history[0]["grade_before"] if history else current_grade,
            final_grade=current_grade,
            iterations=iteration,
            history=history,
            metrics=self._calculate_metrics(history)
        )
```

---

## API Specification

### Endpoints

#### POST /api/v1/iteration/fix-until-clean

**Start iteration job**

```
Request:
  POST /api/v1/iteration/fix-until-clean
  Content-Type: application/json
  
  {
    "directory_path": "/Users/meera/Documents/codescanner",
    "target_grade": "A",
    "max_iterations": 10
  }

Response: 202 Accepted
  {
    "job_id": "iterate_abc12345",
    "status": "processing",
    "message": "Starting iteration until A...",
    "created_at": "2026-06-06T14:30:00Z"
  }
```

#### GET /api/v1/iteration/{job_id}

**Get iteration status and progress**

```
Response: 200 OK
  {
    "job_id": "iterate_abc12345",
    "status": "completed",
    "current_iteration": 4,
    "max_iterations": 10,
    "current_grade": "A",
    "target_grade": "A",
    "start_grade": "C",
    "grade_improvement": 23,
    "progress": "4/10",
    "estimated_time_remaining": "completed",
    "history": [
      {
        "iteration": 1,
        "grade_before": "C",
        "grade_after": "B-",
        "issues_fixed": 5,
        "agent_selected": "Agent A (Simplicity)",
        "fix_description": "Extracted 3 helper functions from analyze_code()",
        "validation_passed": true,
        "applied_at": "2026-06-06T14:31:00Z"
      },
      {
        "iteration": 2,
        "grade_before": "B-",
        "grade_after": "B",
        "issues_fixed": 6,
        "agent_selected": "Agent A (Simplicity)",
        "fix_description": "Removed 45 lines of code duplication",
        "validation_passed": true,
        "applied_at": "2026-06-06T14:34:00Z"
      },
      {
        "iteration": 3,
        "grade_before": "B",
        "grade_after": "A-",
        "issues_fixed": 10,
        "agent_selected": "Agent A (Simplicity)",
        "fix_description": "Added type hints and restructured modules",
        "validation_passed": true,
        "applied_at": "2026-06-06T14:37:00Z"
      },
      {
        "iteration": 4,
        "grade_before": "A-",
        "grade_after": "A",
        "issues_fixed": 2,
        "agent_selected": "Agent A (Simplicity)",
        "fix_description": "Fixed final edge cases",
        "validation_passed": true,
        "applied_at": "2026-06-06T14:40:00Z"
      }
    ],
    "metrics": {
      "start_grade": "C",
      "final_grade": "A",
      "grade_improvement": 23,
      "issues_found": 23,
      "issues_remaining": 0,
      "complexity_reduction": "28 → 8 (71%)",
      "duplication_reduction": "45% → 12%",
      "test_coverage_improvement": "65% → 89%",
      "security_issues_fixed": 7,
      "code_smells_fixed": 14,
      "total_time": "10 minutes"
    }
  }
```

#### GET /api/v1/iteration/{job_id}/history

**Get detailed iteration history**

```
Response: 200 OK
  {
    "job_id": "iterate_abc12345",
    "iterations": [
      { /* same as above */ }
    ],
    "agent_usage": {
      "Agent A (Simplicity)": { "used": 4, "success_rate": 100 },
      "Agent B (Architecture)": { "used": 0, "success_rate": null },
      "Agent C (Performance)": { "used": 0, "success_rate": null }
    }
  }
```

---

## Database Schema

### New Tables

#### iteration_jobs
```sql
CREATE TABLE iteration_jobs (
    job_id VARCHAR(50) PRIMARY KEY,
    codebase_path TEXT NOT NULL,
    target_grade VARCHAR(2) NOT NULL,
    max_iterations INT NOT NULL,
    current_iteration INT DEFAULT 0,
    current_grade VARCHAR(2),
    status VARCHAR(20) NOT NULL,  -- processing, completed, failed
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    history JSONB,  -- Full iteration history
    metrics JSONB   -- Final metrics
);

CREATE TABLE iteration_history (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(50) REFERENCES iteration_jobs(job_id),
    iteration_number INT NOT NULL,
    grade_before VARCHAR(2),
    grade_after VARCHAR(2),
    issues_fixed INT,
    agent_selected VARCHAR(50),
    fix_description TEXT,
    validation_passed BOOLEAN,
    applied_at TIMESTAMP,
    changes JSONB  -- Detailed changes made
);
```

---

## Implementation Phases

### Phase 3.5A: Agent System (20-30 hours)

**Goal:** Build core agent classes that can suggest refactorings

**Deliverables:**
- [ ] RefactoringAgent base class
  - Abstract method: suggest_refactoring()
  - Common utilities for AST analysis
  - Code modification helpers

- [ ] AgentA_SimplityFirst implementation
  - Extract small functions strategy
  - Identify complex functions
  - Generate extraction suggestions

- [ ] AgentB_ArchitectureFocused implementation
  - Identify architectural issues
  - Suggest design patterns
  - Plugin/module restructuring

- [ ] AgentC_PerformanceOptimized implementation
  - Identify performance bottlenecks
  - Suggest parallelization
  - Caching opportunities

- [ ] EvaluationAgent implementation
  - Scoring algorithm
  - Comparison logic
  - Best suggestion selection

**Testing:**
- Unit tests for each agent
- Verify suggestion format
- Test scoring algorithm

**Files to Create:**
- `api/services/agents/refactoring_agent.py`
- `api/services/agents/agent_a_simplicity.py`
- `api/services/agents/agent_b_architecture.py`
- `api/services/agents/agent_c_performance.py`
- `api/services/agents/evaluation_agent.py`

---

### Phase 3.5B: Orchestration Service (20-30 hours)

**Goal:** Build the main iteration loop service

**Deliverables:**
- [ ] ValidatorAgent implementation
  - Syntax validation
  - Import checking
  - Logic preservation
  - Test regression detection
  - Performance validation

- [ ] IterationCleanService implementation
  - Main fix_until_clean() loop
  - Integration with scanner service
  - Job tracking
  - History persistence
  - Grade comparison logic

- [ ] Database models
  - IterationJob ORM model
  - IterationHistory ORM model

- [ ] Background task integration
  - Celery task for iteration job
  - Progress callbacks
  - Error handling

**Testing:**
- Integration tests for full loop
- Test with sample codebases
- Verify grade progression
- Test max_iterations limit

**Files to Create:**
- `api/services/agents/validator_agent.py`
- `api/services/iteration_clean_service.py`
- `api/db/models.py` (add IterationJob, IterationHistory)
- `api/tasks/iteration.py`

---

### Phase 3.5C: API & Integration (15-20 hours)

**Goal:** Expose iteration functionality via REST API

**Deliverables:**
- [ ] IterationCleanService routes
  - POST /api/v1/iteration/fix-until-clean
  - GET /api/v1/iteration/{job_id}
  - GET /api/v1/iteration/{job_id}/history
  - DELETE /api/v1/iteration/{job_id} (cancel)

- [ ] Request/response models
  - FixUntilCleanRequest
  - IterationStatusResponse
  - IterationHistoryResponse

- [ ] WebSocket integration (optional)
  - Real-time progress updates
  - Iteration completion notifications

- [ ] Job cleanup
  - Auto-cleanup old jobs
  - Configurable retention

**Testing:**
- API endpoint tests
- Request validation
- Response format validation
- Job tracking tests

**Files to Create:**
- `api/routes/iteration.py`
- `api/models/iteration_requests.py`
- `api/models/iteration_responses.py`

---

### Phase 3.5D: Testing & Validation (15-20 hours)

**Goal:** Comprehensive testing and edge case handling

**Deliverables:**
- [ ] Unit tests
  - Each agent independently
  - Evaluator scoring
  - Validator checks

- [ ] Integration tests
  - Full iteration loop
  - Multiple iterations
  - Grade progression

- [ ] End-to-end tests
  - Real codebase iteration
  - Sample projects: small, medium, large
  - Verify final grades

- [ ] Edge case tests
  - No suggestions available
  - All suggestions rejected by validator
  - Target grade already met
  - Max iterations reached mid-improvement
  - Concurrent iteration jobs

- [ ] Performance tests
  - Timing for different codebases
  - Memory usage tracking
  - Database query optimization

**Files to Create:**
- `tests/test_agents.py`
- `tests/test_evaluator.py`
- `tests/test_validator.py`
- `tests/test_iteration_service.py`
- `tests/test_iteration_api.py`

**Test Coverage:**
- [ ] Agent coverage: 90%+
- [ ] Service coverage: 85%+
- [ ] API coverage: 90%+
- [ ] Overall: 85%+

---

## CLI Integration

### Usage Examples

**Basic usage:**
```bash
python scanner/scanner.py /code --fix-until-clean
```

**With options:**
```bash
python scanner/scanner.py /code --fix-until-clean --target-grade A --max-iterations 10
```

**Watch progress:**
```bash
# In terminal 1
python scanner/scanner.py /code --fix-until-clean --watch

# In terminal 2
curl http://localhost:8000/api/v1/iteration/{job_id}
```

### CLI Output

```
🔄 Starting Iteration Until Clean...

Iteration 1/10:
  Current grade: C (72/100)
  Issues: 23
  └─ Finding best fix from 3 agents...
  └─ Evaluating suggestions...
  └─ Validating fix...
     ├─ Syntax: ✅
     ├─ Logic: ✅
     ├─ Tests: ✅
     └─ Performance: ✅
  └─ Applying changes... ✅
  └─ New grade: B- (78/100) [+6 points, -5 issues]
  
Iteration 2/10:
  Current grade: B- (78/100)
  Issues: 18
  └─ Selected: Agent A (Simplicity)
  └─ New grade: B (83/100) [+5 points, -6 issues]

Iteration 3/10:
  Current grade: B (83/100)
  Issues: 12
  └─ Selected: Agent A (Simplicity)
  └─ New grade: A- (91/100) [+8 points, -10 issues]

Iteration 4/10:
  Current grade: A- (91/100)
  Issues: 2
  └─ Selected: Agent A (Simplicity)
  └─ New grade: A (95/100) [+4 points, -2 issues]

✅ TARGET REACHED: Grade A!

═══════════════════════════════════════════════════
📊 FINAL REPORT
Start: C (72/100) → Final: A (95/100)
Improvement: +23 points over 4 iterations in ~15 minutes

Metrics:
  ✅ Complexity: 28 → 8 (71%)
  ✅ Duplication: 45% → 12%
  ✅ Coverage: 65% → 89%
  ✅ Security: 7 → 0
═══════════════════════════════════════════════════
```

---

## Success Criteria

✅ **Multi-Agent System**
- [ ] 3 agents work independently
- [ ] Each generates unique suggestions
- [ ] Suggestions in correct format

✅ **Evaluation System**
- [ ] Scoring algorithm correct
- [ ] Best suggestion selected reliably
- [ ] Weights properly balanced

✅ **Validation System**
- [ ] Syntax checking works
- [ ] Logic preservation verified
- [ ] Test regression detection works
- [ ] No invalid changes applied

✅ **Iteration Loop**
- [ ] Scans → Suggests → Evaluates → Validates → Applies
- [ ] Repeats correctly
- [ ] Stops at target or max_iterations
- [ ] Grade improves each iteration

✅ **API**
- [ ] Endpoints working
- [ ] Job tracking accurate
- [ ] History properly recorded
- [ ] Response format correct

✅ **Database**
- [ ] Schema created
- [ ] Jobs persist
- [ ] History recorded
- [ ] Cleanup working

✅ **Testing**
- [ ] 85%+ code coverage
- [ ] All edge cases handled
- [ ] Performance acceptable
- [ ] No regressions

---

## Timeline Estimate

| Phase | Hours | Duration |
|-------|-------|----------|
| 3.5A: Agent System | 20-30 | 3-4 days |
| 3.5B: Orchestration | 20-30 | 3-4 days |
| 3.5C: API | 15-20 | 2-3 days |
| 3.5D: Testing | 15-20 | 2-3 days |
| **TOTAL** | **70-100** | **10-14 days** |

**Realistic Timeline:** 1.5-2 weeks with focused development

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Agent suggestions too conservative | Medium | Low | Test with real code |
| Validator too strict (blocks good fixes) | Medium | Medium | Adjust validation thresholds |
| Performance (long iterations) | Low | Medium | Optimize scanner |
| Circular suggestions (A → B → A) | Low | Medium | Add history checking |
| Database contention | Low | Low | Add connection pooling |

---

## Success Metrics

**When complete, Phase 3.5 will enable:**

1. **Automatic Code Improvement**
   - Grade C → A in 15 minutes
   - Complexity reduction: 71%
   - Security issues: 23 → 0

2. **Multi-Agent Collaboration**
   - 3 perspectives evaluated
   - Safest option selected
   - Validated before applying

3. **Safety First**
   - Zero invalid changes applied
   - All tests still passing
   - Logic preserved

4. **Developer Experience**
   - One command: `--fix-until-clean`
   - Clear progress feedback
   - Detailed improvement report

---

## Next After Phase 3.5

Once Phase 3.5 is complete and stable:

**Phase 4: AI Refactoring with PR Workflow**
- Visual refactoring interface (file browser + diff viewer)
- GitHub PR creation workflow
- Team notifications
- 110-140 hours (2-3 weeks)

---

## References

- **Memory:** [[iteration-until-clean-skill]]
- **Conversation Archive:** `CONVERSATION_SESSION_2_PHASE_35_ITERATION_UNTIL_CLEAN.md`
- **Feature Set:** CODEPULSE_AI_FEATURE_SET.md
- **Previous Phases:** PHASE_3_ADVANCED_FEATURES_IMPLEMENTATION_COMPLETE.md

---

**Status: Planning COMPLETE ✅**  
**Ready for implementation when you begin Phase 3.5**

