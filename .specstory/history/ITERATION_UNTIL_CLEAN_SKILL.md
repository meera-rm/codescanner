---
created_at: 2026-06-12T18:16:43Z
title: Iteration Until Clean Skill
source: claude-code
project: codescanner
---

# ITERATION UNTIL CLEAN — Core Differentiator Skill

**Feature:** Automated code improvement loop with multi-agent review  
**Status:** Ready to implement (BEFORE Phase 4)  
**Priority:** CRITICAL (Core differentiator vs other scanners)  
**Complexity:** High (multi-agent orchestration)  
**Effort:** 60-80 hours

---

## Overview

**fix_until_clean()** — The standout feature that makes CodePulse AI different.

Instead of:
```
Scan code → Find issues → Report findings → User manually fixes
```

CodePulse does:
```
Scan → Generate fixes (multiple agents) → Pick best → Validate → Apply → Rescan → Repeat
Until Grade A reached
```

---

## Part 1: The Loop

### Core Workflow

```
START
  ↓
Iteration 1:
  Grade: C (72/100) - 23 issues found
  ├─ Multiple agents generate suggestions independently:
  │  ├─ Agent A: "Extract methods from analyze_code()"
  │  ├─ Agent B: "Split into smaller functions"
  │  └─ Agent C: "Create helper classes"
  │
  ├─ System evaluates suggestions:
  │  ├─ Complexity reduction: A=60%, B=45%, C=70%
  │  ├─ Risk of errors: A=low, B=low, C=high
  │  ├─ Code clarity: A=good, B=excellent, C=ok
  │  └─ Pick BEST: Agent B (high reduction, lowest risk, clearest)
  │
  ├─ Validator Agent reviews Agent B's fix:
  │  ├─ Syntax check: ✅ PASS
  │  ├─ Import validation: ✅ PASS
  │  ├─ Logic preservation: ✅ PASS
  │  ├─ Test regression: ✅ PASS
  │  └─ VERDICT: ✅ APPROVED (safe to apply)
  │
  ├─ Apply changes to codebase
  ├─ Rescan entire codebase
  └─ Result: Grade: B- (78/100) - 18 issues found
        Improvement: +6 points, -5 issues

Iteration 2:
  Grade: B- (78/100) - 18 issues
  ├─ Multiple agents generate suggestions
  ├─ System picks best
  ├─ Validator reviews
  ├─ Apply changes
  ├─ Rescan
  └─ Result: Grade: B (83/100) - 12 issues
        Improvement: +5 points, -6 issues

Iteration 3:
  Grade: B (83/100) - 12 issues
  ├─ Multiple agents generate suggestions
  ├─ System picks best
  ├─ Validator reviews
  ├─ Apply changes
  ├─ Rescan
  └─ Result: Grade: A- (91/100) - 2 issues
        Improvement: +8 points, -10 issues

Iteration 4:
  Grade: A- (91/100) - 2 issues
  ├─ Multiple agents generate suggestions
  ├─ System picks best (final trivial fixes)
  ├─ Validator reviews
  ├─ Apply changes
  ├─ Rescan
  └─ Result: Grade: A (95/100) - 0 critical issues
        Improvement: +4 points, -2 issues

STOP - Grade A reached ✅
Final: Grade A (95/100)
Total improvement: +23 points
Iterations: 4
Time: ~15 minutes
```

---

## Part 2: Multi-Agent Orchestration

### Agent Roles

**1. Refactoring Agents (3 Independent)**
```
Agent A - "Simplicity First"
  Strategy: Minimal changes, extract smallest units
  Strengths: Low risk, clear diffs
  Approach: One concern per function

Agent B - "Architecture Focused"  
  Strategy: Redesign structure, optimize flow
  Strengths: Better organization, long-term maintainability
  Approach: Rethink entire module

Agent C - "Performance Optimized"
  Strategy: Speed and resource efficiency
  Strengths: Better performance, less overhead
  Approach: Optimize hot paths
```

**How they work:**
```
Issue: Function analyze_code() too complex (complexity 28)

Agent A suggests:
  "Extract helper functions for each check type
   - check_syntax()
   - check_security()
   - check_complexity()
   Changes: -15 lines of complexity, +3 new functions
   Risk: Low (each function is simple)"

Agent B suggests:
  "Refactor into Analyzer class with plugins
   - Base Analyzer class
   - SyntaxAnalyzer plugin
   - SecurityAnalyzer plugin
   - ComplexityAnalyzer plugin
   Changes: -20 lines, +40 new structure
   Risk: Medium (larger refactoring)"

Agent C suggests:
  "Parallelize checks and cache results
   - Use async for concurrent checks
   - Cache findings by hash
   - Return early on critical issues
   Changes: -8 lines, +async pattern
   Risk: Low (adds async, doesn't change logic)"
```

**2. Evaluation Agent**
```
Role: Compare and score suggestions

Criteria:
- Complexity reduction (weight: 30%)
- Risk of errors/regressions (weight: 40%)
- Code clarity (weight: 20%)
- Implementation time (weight: 10%)

Scoring:
  Agent A: (60% reduction × 0.3) + (low risk × 0.4) + (good clarity × 0.2) + (quick × 0.1) = 65/100
  Agent B: (70% reduction × 0.3) + (medium risk × 0.4) + (excellent clarity × 0.2) + (slow × 0.1) = 58/100
  Agent C: (40% reduction × 0.3) + (low risk × 0.4) + (good clarity × 0.2) + (medium × 0.1) = 52/100

WINNER: Agent A (highest score, acceptable safety)
```

**3. Validator Agent**
```
Role: Review chosen fix for errors/pitfalls before applying

Validates:
1. Syntax Check
   ✅ All imports present
   ✅ All functions defined
   ✅ No undefined variables
   ✅ Type hints correct

2. Logic Preservation
   ✅ Input/output unchanged
   ✅ Side effects preserved
   ✅ Error handling intact
   ✅ Comments updated

3. Test Regression Check
   ✅ Existing unit tests still pass
   ✅ No new test failures
   ✅ Coverage maintained
   ✅ Edge cases still handled

4. Performance Check
   ✅ No new bottlenecks
   ✅ Memory usage unchanged
   ✅ Execution speed same/better
   ✅ No memory leaks

Verdict: ✅ APPROVED (safe to apply)
         or
         ❌ REJECTED (needs refinement)
```

---

## Part 3: Implementation Architecture

### Backend Service: IterationCleanService

```python
class IterationCleanService:
    """Orchestrate iteration until clean loop."""
    
    def __init__(self):
        self.refactoring_agents = [
            AgentA_SimplivityFirst(),
            AgentB_ArchitectureFocused(),
            AgentC_PerformanceOptimized(),
        ]
        self.evaluator = EvaluationAgent()
        self.validator = ValidatorAgent()
    
    async def fix_until_clean(self,
                             codebase_path: str,
                             target_grade: str = "A",
                             max_iterations: int = 10) -> IterationResult:
        """Main loop: iterate until target grade reached."""
        
        iteration = 0
        current_grade = None
        history = []
        
        while iteration < max_iterations:
            iteration += 1
            
            # Scan current state
            scan_result = await self._scan_codebase(codebase_path)
            current_grade = scan_result["grade"]
            issues = scan_result["issues"]
            
            # Check if done
            if self._grade_value(current_grade) >= self._grade_value(target_grade):
                return self._create_final_result(current_grade, history)
            
            # Get suggestions from multiple agents
            suggestions = await self._get_suggestions(
                codebase_path, 
                issues,
                iteration
            )
            
            if not suggestions:
                break  # No more suggestions
            
            # Evaluate and pick best
            best_suggestion = self.evaluator.pick_best(suggestions)
            
            # Validate before applying
            validation = await self.validator.validate(best_suggestion)
            
            if not validation["approved"]:
                # Skip this suggestion, try next best
                continue
            
            # Apply the fix
            await self._apply_fix(codebase_path, best_suggestion)
            
            # Track iteration
            history.append({
                "iteration": iteration,
                "grade_before": scan_result["grade"],
                "issues_fixed": len(issues) - len(scan_result["remaining_issues"]),
                "suggestion_source": best_suggestion["agent"],
                "applied_fix": best_suggestion["description"],
            })
        
        return self._create_final_result(current_grade, history)
    
    async def _get_suggestions(self, path, issues, iteration):
        """Get parallel suggestions from multiple agents."""
        suggestions = await asyncio.gather(
            *[
                agent.suggest_refactoring(path, issues)
                for agent in self.refactoring_agents
            ]
        )
        return [s for s in suggestions if s]  # Filter None
    
    def _grade_value(self, grade: str) -> float:
        """Convert letter grade to numeric value."""
        grades = {"F": 0, "D": 1, "C": 2, "B": 3, "A": 4}
        return grades.get(grade[0], 0) + (0.5 if "-" in grade else 0)
```

### API Endpoint

```python
@router.post("/iteration/fix-until-clean")
async def fix_until_clean(req: Request,
                         directory_path: str,
                         target_grade: str = "A",
                         max_iterations: int = 10):
    """
    Iterate on code until it reaches target grade.
    
    Returns job_id for async tracking.
    """
    job_id = f"iterate_{uuid.uuid4().hex[:8]}"
    
    # Start background job
    background_tasks.add_task(
        iteration_service.fix_until_clean,
        directory_path,
        target_grade,
        max_iterations
    )
    
    return {
        "job_id": job_id,
        "status": "processing",
        "message": f"Starting iteration until {target_grade}..."
    }

@router.get("/iteration/{job_id}")
async def get_iteration_status(job_id: str):
    """Get status and progress of iteration job."""
    result = jobs[job_id]
    return {
        "job_id": job_id,
        "status": result["status"],
        "current_iteration": result.get("iteration", 0),
        "current_grade": result.get("current_grade"),
        "target_grade": result.get("target_grade"),
        "history": result.get("history", []),
        "progress": f"{result.get('iteration', 0)}/{result.get('max_iterations')}",
    }
```

---

## Part 4: Example Output

### CLI Usage

```bash
$ python scanner/scanner.py /code --fix-until-clean --target-grade A --max-iterations 10

🔄 Starting Iteration Until Clean...

Iteration 1:
  Grade: C (72/100) - 23 issues
  └─ Finding best fix from 3 agents...
     ├─ Agent A (Simplicity): Extract methods - Score: 65/100
     ├─ Agent B (Architecture): Refactor structure - Score: 58/100
     └─ Agent C (Performance): Parallelize - Score: 52/100
  └─ Selected: Agent A (highest safety + simplicity)
  └─ Validating fix...
     ├─ Syntax: ✅
     ├─ Logic: ✅
     ├─ Tests: ✅
     └─ Performance: ✅
  └─ Applying changes... ✅
  └─ Rescanning... New grade: B- (78/100) [+6 points, -5 issues]

Iteration 2:
  Grade: B- (78/100) - 18 issues
  └─ Finding best fix from 3 agents...
     ├─ Agent A: Remove duplication - Score: 70/100
     ├─ Agent B: Merge utilities - Score: 62/100
     └─ Agent C: Cache results - Score: 55/100
  └─ Selected: Agent A
  └─ Validating... ✅
  └─ Applying... ✅
  └─ New grade: B (83/100) [+5 points, -6 issues]

Iteration 3:
  Grade: B (83/100) - 12 issues
  └─ Finding best fix from 3 agents...
     ├─ Agent A: Extract utilities - Score: 72/100
     ├─ Agent B: Add type hints - Score: 60/100
     └─ Agent C: Optimize loops - Score: 58/100
  └─ Selected: Agent A
  └─ Validating... ✅
  └─ Applying... ✅
  └─ New grade: A- (91/100) [+8 points, -10 issues]

Iteration 4:
  Grade: A- (91/100) - 2 issues
  └─ Finding best fix from 3 agents...
     ├─ Agent A: Fix remaining issues - Score: 75/100
     ├─ Agent B: Minor cleanup - Score: 61/100
     └─ Agent C: Add docstrings - Score: 59/100
  └─ Selected: Agent A
  └─ Validating... ✅
  └─ Applying... ✅
  └─ New grade: A (95/100) [+4 points, -2 issues]

✅ GOAL REACHED: Grade A!

═══════════════════════════════════════════════════════
📊 FINAL REPORT

Start Grade:    C (72/100)
Final Grade:    A (95/100)
Total Improvement: +23 points

Iterations:     4
Issues Fixed:   23 → 0 critical
Time:          ~15 minutes

🎯 Success Metrics:
  ✅ Complexity: 28 → 8 (reduced 71%)
  ✅ Duplication: 45% → 12%
  ✅ Test Coverage: 65% → 89%
  ✅ Security Issues: 7 → 0
  ✅ Code Smells: 14 → 0

📝 Changes Summary:
  Iteration 1: Extracted 3 helper functions
  Iteration 2: Removed 45 lines of duplication
  Iteration 3: Added type hints, improved structure
  Iteration 4: Fixed final 2 edge cases

🤖 Agent Summary:
  Agent A (Simplicity): Used 3 times (best performer)
  Agent B (Architecture): Not selected (too risky)
  Agent C (Performance): Not selected (didn't address issues)

═══════════════════════════════════════════════════════
```

### REST API Response

```json
{
  "job_id": "iterate_abc12345",
  "status": "completed",
  "start_grade": "C",
  "final_grade": "A",
  "grade_improvement": 23,
  "iterations": 4,
  "max_iterations": 10,
  "target_grade": "A",
  "issues_fixed": 23,
  "start_issues": 23,
  "final_issues": 0,
  "estimated_time": "15 minutes",
  "history": [
    {
      "iteration": 1,
      "grade_before": "C",
      "grade_after": "B-",
      "issues_fixed": 5,
      "agent_selected": "Agent A (Simplicity)",
      "fix_applied": "Extracted 3 helper functions from analyze_code()",
      "validation_passed": true
    },
    {
      "iteration": 2,
      "grade_before": "B-",
      "grade_after": "B",
      "issues_fixed": 6,
      "agent_selected": "Agent A (Simplicity)",
      "fix_applied": "Removed 45 lines of code duplication",
      "validation_passed": true
    },
    {
      "iteration": 3,
      "grade_before": "B",
      "grade_after": "A-",
      "issues_fixed": 10,
      "agent_selected": "Agent A (Simplicity)",
      "fix_applied": "Added type hints and restructured modules",
      "validation_passed": true
    },
    {
      "iteration": 4,
      "grade_before": "A-",
      "grade_after": "A",
      "issues_fixed": 2,
      "agent_selected": "Agent A (Simplicity)",
      "fix_applied": "Fixed final edge cases",
      "validation_passed": true
    }
  ],
  "metrics": {
    "complexity_reduction": "28 → 8 (71%)",
    "duplication_reduction": "45% → 12%",
    "test_coverage_improvement": "65% → 89%",
    "security_issues_fixed": 7,
    "code_smells_fixed": 14
  }
}
```

---

## Part 5: Implementation Plan

### Phase Components

**Phase 3.5A: Agent System (20-30 hours)**
- [ ] Create RefactoringAgent base class
- [ ] Implement 3 specialized agents (Simplicity, Architecture, Performance)
- [ ] Implement EvaluationAgent (scoring algorithm)
- [ ] Implement ValidatorAgent (validation logic)
- [ ] Create agent communication framework

**Phase 3.5B: Orchestration Service (20-30 hours)**
- [ ] Create IterationCleanService
- [ ] Implement fix_until_clean() loop
- [ ] Grade evaluation logic
- [ ] Job tracking and persistence
- [ ] Error handling and rollback

**Phase 3.5C: API & Integration (15-20 hours)**
- [ ] Create REST endpoints
- [ ] Job status tracking
- [ ] WebSocket for real-time updates
- [ ] Integration with existing services
- [ ] Error handling

**Phase 3.5D: Testing & Validation (15-20 hours)**
- [ ] Unit tests for each agent
- [ ] Integration tests for loop
- [ ] End-to-end test on sample codebases
- [ ] Performance testing
- [ ] Edge case handling

**Total Estimate: 70-100 hours (1.5-2 weeks)**

---

## Part 6: Success Criteria

✅ **Multi-Agent System**
- 3 independent refactoring agents working in parallel
- Evaluation agent picking best suggestion
- Validator agent checking for safety

✅ **Iteration Loop**
- Scans → Suggests → Evaluates → Validates → Applies → Rescans
- Repeats until target grade reached
- Tracks progress and history

✅ **Safety First**
- No code changes without validation
- All changes reversible
- Tests must still pass
- No logic changes (only refactoring)

✅ **User Experience**
- Clear progress feedback (iteration 1/4)
- Shows which agent was selected and why
- Final report with metrics
- Option to accept/reject changes

---

## Part 7: Key Differentiators

vs. Other Code Scanners:

| Feature | CodePulse | Others |
|---------|-----------|--------|
| Find issues | ✅ | ✅ |
| Suggest fixes | ✅ | ⏳ Limited |
| **Automatically apply** | ✅ | ❌ |
| **Multi-agent review** | ✅ | ❌ |
| **Validate safety** | ✅ | ❌ |
| **Iterate until clean** | ✅ | ❌ |
| **Reach Grade A** | ✅ | ❌ |

---

## Part 8: Timeline

```
BEFORE Phase 4:
├─ Week 1: Agents + Orchestration (3.5A + 3.5B)
├─ Week 2: API + Testing (3.5C + 3.5D)
└─ Week 3: Polish + Documentation

THEN: Phase 4 (PR Workflow)
├─ Implement visual UI
├─ Add GitHub integration
└─ Deploy to production
```

---

## Conclusion

**"Iteration Until Clean"** is the core differentiator that transforms CodePulse from "find bugs" to "fix code automatically until it's perfect."

This is the feature mentioned in CODEPULSE_AI_FEATURE_SET.md as:
> "The ability to iteratively fix code until it reaches a target grade is what differentiates CodePulse AI from other linters."

**Status: READY TO IMPLEMENT**

Priority: Implement BEFORE Phase 4 PR Workflow

See also:
- `CODEPULSE_AI_FEATURE_SET.md` — Part 8 (core feature)
- `CODE_SCANNER_DEVELOPMENT.md` — Project journey
