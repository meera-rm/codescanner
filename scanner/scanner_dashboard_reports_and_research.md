# Code Scanner Dashboard — Reports, Charts, Research & Design Decisions

## Generated Report Outputs — JSON Example

```json
{
  "title": "examples/complex_logic.py",
  "language": "python",
  "lines_total": 95,
  "lines_code": 85,
  "lines_blank": 10,
  "lines_comment": 0,
  "function_count": 3,
  "complexity_average": 1.31,
  "complexity_max": 1.0,
  "lines_code": 85,
  "lines_blank": 10,
  "lines_comment": 0,
  "function_count": 3,
  "code_smells": 5,
  "doc_coverage_ratio": 1.0,
  "duplication_percentage": 2.1,
  "coupling_count": 0,
  "error_handling_count": 1,
  "logging_count": 0,
  "security_high_count": 0,
  "security_medium_count": 0,
  "security_findings": [ ]
}
```

## CSV Metrics Table Export

| File | Language | Lines | Code | Quality | Smells | Doc % | Dup % | Imports | Security | Functions | Complexity | Errors | Logging |
|------|----------|-------|------|---------|--------|-------|-------|---------|----------|-----------|------------|--------|---------|
| complex_logic.py | python | 95 | 85 | D | 5 | 100% | 21.2% | 0 | 0 | 3 | 2.3 | 0 | 0 |
| error_handling.py | python | 113 | 93 | B | 3 | 100% | - | 0 | 0 | 5 | 2.33 | 25 | 4 |
| insecure.py | python | 30 | 18 | C | 0 | 100% | - | 1 | 4 | 3 | 2.40 | 25 | 4 |
| logging_heavy.py | python | 132 | 103 | B | 3 | 100% | - | 2 | 0 | 5 | 2.60 | 1 | 39 |
| realistic_app.py | python | 227 | 181 | A | 4 | 100% | - | 3 | 0 | 10 | 2.50 | 29 | 41 |
| injection.sql | sql | 14 | 9 | C | - | - | - | 0 | 1 | 0 | 0.0 | 0 | 0 |
| sample.py | python | 18 | 5 | D | - | - | - | 0 | 0 | 2 | 1.0 | 0 | 0 |
| sample.js | javascript | 7 | 5 | C | - | - | - | 0 | 0 | 1 | 0.0 | 0 | 0 |
| sample.jsx | javascript | 35 | 28 | C | - | - | - | 0 | 0 | 2 | 0.0 | 0 | 0 |

---

## Generated Report Outputs — Charts & Visualizations

### Lines of Code Distribution
Shows breakdown of Code Lines (blue), Blank Lines (dark), Comment Lines (green) per file
- complex_logic.py: ~85 code
- error_handling.py: ~93 code
- insecure.py: ~18 code
- logging_heavy.py: ~103 code
- realistic_app.py: ~181 code
- sample.py: ~5 code

### Quality Score Breakdown (Radar/Pentagon Chart)
Dimensions (avg scores):
- Simplicity: ~60
- Documentation: ~80
- Error Handling: ~40
- Maintainability: ~50
- Logging: ~40

### Dependency Types (Donut Chart)
- Stdlib (7) — majority
- External (1) — single external
- Internal (0) — zero internal

### Cyclomatic Complexity (Top Functions - Bar Chart)
Red bars (high complexity):
- authenticate_user: 6
- create_session: 5
- validate_session: 5

Orange bars (medium):
- validate_request: 4
- validate_user_data: 3

Green bars (low):
- process_transaction: ~2
- fetch_data: ~2

### Security Findings by Severity (Distribution Chart)
Bell curve showing:
- High Severity: 3 findings (hardcoded secrets, SQL injection)
- Medium Severity: 3 findings (missing error handling)
- Files affected: complex_logic.py, error_handling.py, insecure.py, injection.sql, logging_heavy.py, realistic_app.py, sample.jsx

---

## Skills & Evolve Loop

### Available Skills

#### /plan — Design-Only Mode
Explore and design without writing code. Produces plan.md with approach, criteria, and decisions.
```
/plan Phase 4 design: read PLAN.md, produce detailed plan
```

#### /analyze — Parallel Impact Analysis
Spawn 3 parallel agents for codebase exploration. Synthesizes into grounded, submission-ready proposal.
```
/analyze CSV schema changes: which fields need remapping?
```

### Evolve Loop: Design → Build → Verify → Commit

The rhythm for clean, phased development:

**1. Design**
Use /plan to explore and produce plan.md

**2. Implement**
Code against the locked-in plan

**3. Test**
pytest tests/ -v until green

**4. Analyze**
Use /analyze for impact assessment

**5. Commit**
Clean commit with proper message

**6. Iterate**
Loop back to design for next phase

### Workflow Constraints (in CLAUDE.md)

Standing rules enforced across all sessions:

- **Workflow Modes** — Design-only, analysis-only, plan-then-build. No premature code.
- **Dashboard & HTML Files** — Confirm target file. Never modify master_dashboard.html unless told.
- **Tech Stack** — Static HTML, real CSV data, no fabrication. No Flask/backend unless approved.
- **Pre-Commit Gates** — Security gates block risky commits. Fix locally and retry.
- **Tests & Commits** — All tests pass before commit. Use documented commit convention.

---

## Process Rules & Team Conventions

### How to Work (Process Rules)

✅ **DO**
- ✓ Confirm design vs implementation mode before coding
- ✓ Restate the goal before big changes
- ✓ Read the plan/design doc before implementing
- ✓ Verify against acceptance criteria
- ✓ Apply to: Any AST-based metric calculation

❌ **DON'T**
- ✗ Jump straight to code without checking phase
- ✗ Assume intent from a vague prompt
- ✗ Re-invent from conversation memory
- ✗ Say "done" without checking

### Team Conventions

#### Commits
Standard: Conventional Commits via commit-formatter skill
Format: DETRNS-XXX prefix (e.g., DETRNS-199)
```bash
git commit -m "feat: DETRNS-xxx Add feature description"
```

#### Tests
Naming: Name after behavior, not function
Bad Example: test_count_lines()
Good Example: test_line_counting_ignores_blank_lines()
```python
def test_line_counting_ignores_blank_lines():
```

#### Pull Requests
Max Size: 100 lines changed per PR
Description: Explain what changed and why
Goal: Keep reviews focused and easy to understand

#### Comments
Rule: Only add comments when the "why" is non-obvious
Philosophy: Well-named code is better than comments
Avoid: Documenting what the code does (should be obvious)
Focus on: Non-obvious constraints, hidden invariants, workarounds

---

## Code Quality Standards

### Clear Naming & Structure
- ✓ One responsibility per function
- ✓ Descriptive variable and function names
- ✓ Consistent with existing patterns

### Error Handling
- ✓ Handle file I/O errors gracefully
- ✓ Handle parsing errors gracefully
- ✓ Validate system boundaries (user input, APIs)
- ✓ Trust internal code and framework guarantees

### Pattern Consistency
Follow patterns established in Phase 1 across all subsequent phases
If you're uncertain about style, look at existing similar code

---

## Scope Management

### ✅ DO INCLUDE
- ✓ Handle common cases correctly
- ✓ Deliver working features
- ✓ Save advanced metrics for bonus rounds
- ✓ Minimal diff for the task
- ✓ Match existing patterns
- ✓ Ask before large refactors

### ❌ DON'T INCLUDE
- ✗ Handle every edge case
- ✗ Build dashboards in Phase 1-2
- ✗ Over-engineer abstractions
- ✗ Support every language at once
- ✗ Add features outside current phase
- ✗ Touch unrelated files

---

## Key References

- **Design & Architecture:** design_doc.md
- **Implementation Plan:** PLAN.md
- **Design Rationale:** RESEARCH.md (Ground Rules section)
- **Team Conventions:** CLAUDE.md (Ground Rules section)

---

## Architecture Research & Ground Rules

### The 4 Core Ground Rules

These rules are now enforced in CLAUDE.md and all future code:

#### ✅ Rule 1: Recursive AST Traversal for Complexity — Exclude Nested Functions

Use recursive traversal that stops at nested ast.FunctionDef nodes, not ast.walk()

**Use Recursive Traversal that Skips Nested FunctionDef nodes. Scopes complexity to function's own branches only.**

**The Problem:** Phase 2 used ast.walk() which descends into nested functions, inflating parent scores. A parent with 1 branch containing a nested function with 5 branches was scored as 6 (should be 1).

**The Fix:** Use recursive traversal that skips nested FunctionDef nodes. Scopes complexity to function's own branches only.

**Why It Matters:** Accurate metrics are essential for meaningful quality assessment.

---

#### ✅ Rule 2: Handle Missing Keys Gracefully in Report Generation

Use .get(key, default) instead of direct key access when handling metrics dictionaries. Test fixtures may not include all optional bonus metric fields.

**Use .get(key, default) instead of direct key access when handling metrics dictionaries. Test fixtures may not include all optional bonus metric fields.**

**The Problem:** Phase 3 test fixtures don't always include optional bonus metric keys. Direct access like metrics['documented_count'] raised KeyError.

**The Fix:** Use metrics.get('lines_code', 0) for all report functions. Robust to partial metrics.

**Code Pattern:**
```python
✗ score = metrics['quality_score']  # KeyError if missing
✓ score = metrics.get('quality_score', 0)  # Safe fallback
```

---

#### ✅ Rule 3: Verify Scanner Output on Examples/ After Each Metric Change

Run the scanner on examples/after implementing or modifying metrics. Spot-check JSON, Markdown, and CSV outputs before relying on unit tests.

**Run the scanner on examples/ After implementing or modifying metrics. Spot-check JSON, Markdown, and CSV outputs before relying on unit tests.**

**The Problem:** Unit tests passed but real scanner output was incomplete. Functions missing from output if missed during enumeration.

**The Fix:** Always run on examples/ and manually inspect JSON, Markdown, CSV outputs after changes.

**Why It Matters:** Real-world behavior is the true spec. The scanner's behavior on real code.

---

#### ✅ Rule 4: CLI Supports Multiple Output Formats as Separate Flags (Not Choices)

Users should be able to generate multiple report formats in one scan. Use separate --report-md FILE and --report-csv FILE flags instead of a single --report {md,csv,json} choice flag.

**Separate --report-md FILE and --report-csv FILE flags. Users can combine: --output report.json --report-md report.md --report-csv report.csv**

**The Problem:** Phase 3 used a single --report {json,markdown,csv} choice flag, forcing users to pick one format per run. CI/CD needed multiple formats per scan.

**The Fix:** Use --report-md FILE and --report-csv FILE flags. Users can combine: --output report.json --report-md report.md --report-csv report.csv

**User Feedback:** Flexibility enables real-world CI/CD pipelines without re-scanning.

---

## How These Rules Emerged (Phase 2-3 Incidents)

### Incident 1: Recursive Complexity vs ast.walk()

**Phase 2 Problem:** ast.walk() descended into nested functions, inflating parent scores. A parent with 1 branch containing a nested function with 5 branches scored as 6 (should be 1).

**The Fix:** Use recursive traversal that skips nested FunctionDef nodes. Scopes complexity to function's own branches only.

**Why It Matters:** Accurate metrics are essential for meaningful quality assessment.

---

### Incident 2: Handle Missing Keys Gracefully

**Phase 3 Problem:** Test fixtures don't always include optional bonus metric keys. Direct access like metrics['documented_count'] raised KeyError.

**The Fix:** Use metrics.get('lines_code', 0) for all report functions. Robust to partial metrics.

**Code Pattern:**
```python
✗ score = metrics['quality_score']  # KeyError if missing
✓ score = metrics.get('quality_score', 0)  # Safe fallback
```

---

### Incident 3: Verify Scanner Output on Examples/

**Phase 3 Problem:** Unit tests passed but real scanner output was incomplete. Functions missing from output if missed during enumeration.

**The Fix:** Always run on examples/ and manually inspect JSON, Markdown, CSV outputs after changes.

**Why It Matters:** Real-world behavior is the true spec. The scanner's behavior on real code.

---

### Incident 4: Separate CLI Flags, Not Single Choice

**Phase 3 Problem:** Phase 3 used a single --report {json,markdown,csv} choice flag, forcing users to pick one format per run. CI/CD needed multiple formats per scan.

**The Fix:** Use --report-md FILE and --report-csv FILE flags. Users can combine:
```bash
--output report.json --report-md report.md --report-csv report.csv
```

**User Feedback:** Flexibility enables real-world CI/CD pipelines without re-scanning.

---

## Design Decisions (8 Architectural Choices)

### 1. AST Parse-Once Design
Parse Python files once. Metrics functions read the AST once, reuse across all metric functions (avoid O(n) redundancy)

### 2. Recursive Complexity vs AST Walk
Explicit nested-function skipping for accuracy. Prevents parent scope inflation.

### 3. Regex vs AST (Logging/Secrets)
Regex for cross-language detection (Python, JS, SQL).
AST for Python-specific patterns (complexity, errors, functions).

### 4. Per-language Optimization
Full AST for Python; regex-based for JavaScript; SQL statement regex.
Filter: --lang python,sql,js

### 5. Quality Score Weighting
30% Simplicity + 20% Documentation + 20% Error Handling + 15% Maintainability + 15% Logging

### 6. Multi-Language Strategy
Full AST for Python (accurate).
Regex for JS (cross-language detection).
SQL statement regex + filter --lang python,sql,js

### 7. Static HTML Dashboard (No Server)
Portable, zero-runtime overhead. Aligns with scanner's "works out-of-the-box" design.

---

## Pre-Commit Gate Use Cases

### ✅ Clean Code Passes
Developer commits safe utility functions without security issues or code smells.
Gate allows commit immediately.

### ❌ Hardcoded Secrets Blocked
Developer accidentally copies code with API keys and secrets.
Gate blocks commit before secrets reach repository.

### 🔄 Fix & Retry Workflow
Developer receives gate violation, replaces hardcoded secret with env var.
Re-commits successfully.

### 📊 Quality Gate Enforcement
Team enables strict quality policies (min score 70, max complexity 8).
Gate blocks low-quality commits until refactored.

### 👥 Developer Onboarding
New team members learn "never hardcode secrets" through immediate, actionable gate feedback on first commit.

### 🔧 CI/CD Integration
GitHub Actions, GitLab CI, or Jenkins runs gate on every push.
Prevents risky merges to main.

---

## Core Learning: "Specification Must Align with Reality"

**Unit tests are necessary but insufficient. The true spec is the scanner's behavior on real code.**

All tests passing ≠ feature complete. Test edge cases, verify output, iterate on real examples.

### Related Documentation
- scanner.py — 1,215 lines implementing these decisions
- CLAUDE.md — Team conventions and ground rules
- design_doc.md — Original requirements and phase breakdown
- RESEARCH.md — Full detailed version of this documentation

