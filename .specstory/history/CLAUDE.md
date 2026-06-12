---
created_at: 2026-06-12T18:16:43Z
title: Claude
source: claude-code
project: codescanner
---


## Code Scanner Project — Context & Architecture

**Status:** ✅ Production Ready (103 tests, 100% passing, 89% coverage)

**Read this first to understand the project:** [`CONVERSATION.md`](CONVERSATION.md)
- Complete conversation history from design through production
- All architectural decisions and rationale
- Full implementation details and test coverage
- Usage examples and deployment path

**Project Quick Reference:**
- **What**: EPA-style code quality health score (CAQI: 0-500) across 6 dimensions
- **Components**: 4 detectors + metrics aggregator + CAQI engine
- **Languages**: Python (primary), JS, SQL (detection)
- **Tests**: 103+ tests, 89% coverage, 0.16s execution
- **Status**: Production-ready with comprehensive test suite

**Key Files:**
- `CONVERSATION.md` — Full project history and context (READ THIS FIRST)
- `PROJECT_SUMMARY.md` — Complete project overview
- `TESTING.md` — Testing guide and infrastructure
- `CAQI.md` — CAQI specifications and formulas
- `scanner/` — Core implementation (1,720 LOC)
- `tests/` — Test suite (3,500+ LOC, 103 tests)

---

## Previous Session Context

**Read before working:** Start with [`CONVERSATION.md`](CONVERSATION.md) for the complete project history, architectural decisions, and design rationale. This avoids repeating context from scratch.

---

## Project

CLI code scanner per core requirements in `design_doc.md`.

- **Design & Requirements**: `design_doc.md` | **Implementation plans**: `PLAN.md` (create next via `/plan`)

## Project - do / don’t

- **Do**: Build a code scanner. Full design design_doc.md.
- **Don’t**: 50 lines of phase plans and architecture

-----

## Four loop

Gather context → Take action → Verify results.
Complete `design_doc.md` before Phase 1 code. Check alignment after each major feature.

## Workflow Nodes

**When you request design, planning, or analysis workitm:**

- **Do NOT write implementation code**
- **Do NOT fabricate data or examples**
- **Do NOT choose a tech stack or pick tools**
- Confirm scope and approach first, then wait for approval before building

This keeps work deliberate and prevents false starts. Use code keywords:

- `'design-only'` - Explore plan, on code
- `'analysis-only'` - Investigate and report, no fabrication
- `'plan-then-build'` - Design first, verify. Then implement after approval

When the mode isn’t explicit, do before jumping to implementation.

-----

## Dashboard & HTML Files

**Before editing any dashboard or HTML files:**

- Confirm the exact target file name
- Scan existing edit history before making changes
- **Default to the user-specified file**

**Examples of what to do:**

- ✗ Wrong: “I’ll add a feature to master_dashboard.html”
- ✓ Right: “Should I add this to scanner_dashboard.html or create a new file?”
- ✗ Wrong: Silently edit a dashboard and commit
- ✓ Right: “Here’s the diff for scanner_dashboard.html. Ready to commit?”

-----

## Scan outputs live in `'output/'`

All scanner-generated artifacts (reports, demo HTML, creative-suite outputs) go in `'output/'` at the repo root - not the project root or `examples/`.

|Path                             |Contents                                                             |
|---------------------------------|---------------------------------------------------------------------|
|`'output/report.json'`           |JSON scan results                                                    |
|`'output/report.md'`             |Markdown report                                                      |
|`'output/report.csv'`            |CSV export (one row per file)                                        |
|`'output/caqi.html'`             |`'CAQI gauge viewer'`                                                |
|`'output/DEMO_*.md'`             |Demo scripts (CAQI, personality, inheritance, pre-commit, onboarding)|
|`'output/scanner_dashboard.html'`|Master analytics dashboard & creative-suite outputs                  |
|`'output/DEMO_CONVERSATION.md'`  |Append-only session archive (see Conversation archive below)         |
|`'output/scanner_dashboard.html'`|CAQI, personality, inheritance, pre-commit, onboarding profiles      |

**CLI use: Always pass explicit paths under `'output/'`:**

```bash
python -m scanner examples/ \
  --output output/report.json \
  --report-md output/report.md \
  --report-csv output/report.csv
```

**Dashboard [‘scanner_dashboard.html’] use:**

- Demo doc links → `'output/DEMO_*.md'`
- CAQI gauge link → `'output/caqi.html'`
- CLI examples in the dashboard use `'output/'` paths

**DO NOT rename `'output/'` → `'output/'` without updating CLAUDE.md, the skill, and all dashboard links in the same change.

-----

## Tech Stack

**For this static-site project:**

- Build single-file static HTML apps (no servers, no frameworks)
- Read from existing CSV files (no fabricated data)
- Use vanilla HTML/CSS/JavaScript (no Flask, pandas, React, or external frameworks)

**Why NOTE:** use browser-blocked approaches (AppleScript, shell scripts, etc.)

**Why**. Several sessions ended in rejected work when Claude chose Flask/pandas or attempted AppleScript-based run buttons.

**Allowed:**

- ✓ Single HTML file with embedded CSS and JavaScript
- ✓ CSV data loaded via `fetch()` or embedded as JSON
- ✓ Standard HTML form inputs and `<canvas>` for charts

**Not allowed:**

- ✗ Flask, Django, FastAPI, or any server framework
- ✗ pandas, NumPy, or Python data processing libraries
- ✗ React, Vue, or frontend frameworks
- ✗ AppleScript or system-level shell commands
- ✗ Fabricated or dummy CSV data

-----

## How to work (process rules)

## Rules the agent should follow every time:

- **Do:**
  Confirm design vs implementation mode before coding
  Restart the goal before big changes
  Read the plan/design doc before implementing
  Verify against acceptance criteria
- **Don’ts:**
  Jump straight to code without checking phase
  Assume intent from a vague prompt
  Re-invent from conversation memory
  Say “done” without checking

-----

## Team conventions

### Commits: Conventional Commits via commit-formatter skill (‘DETRMS-XXX’ prefix)

- **Tests**: Name after behavior, not function = e.g., ‘test_line_counting_ignores_blank_lines’
- **Raises**: Max 100 lines changed; describe what and why
- **Code styles**: naming, comments, error handling expectations

## Team conventions - do / don’t

- **Do**: Tests named after behavior, not function names
- **Don’ts**: Paste entire style guides - Link to them

-----

## Code quality

- Clear naming: one responsibility per function
- Handle file I/O and parsing errors gracefully
- Follow patterns established in Phase 1 across Phase 2

-----

## Scope - do / don’t

**Do:**

- Handle every edge case
- Build UI or dashboards in Phase 1-2 (bonus round)
- Over-engineer abstractions
- **Don’ts:**
- Handle every edge case
- Build UI or dashboards in Phase 1-2 (bonus round)
- Over-engineer abstractions

-----

## Ground Rules (From Phases 1-3)

**Rule 3: Recursive AST traversal for complexity – exclude nested functionsDef**

When calculating cyclomatic complexity per function, use recursive traversal that stops at nested `ast_FunctionDef` nodes, not `ast.walk()`.

When calculating cyclomatic complexity per function, use recursive traversal that excludes `isinstance(child, ast.FunctionDef)`. Use this for any function-scoped metrics.

-----

## Rule 2: Handle missing keys gracefully in report generation**

Report functions should use `.get(key, default)` instead of direct key access, especially when handling test fixtures that may not include all optional keys.

**Why Phase 2 iteration - initial implementation used `ast.walk()`, causing `validate_request()` in test fixtures to report inflated complexity scores on utility functions with nested helpers. This was discovered during verification on the `examples/` directory.

**Allow so apply:** After each metric function lands, run the scanner on examples/ directory and review the generated reports.

-----

## Rule 5: Pre-Commit Gates Block Risky Commits (Not Punishment)**

Pre-commit hooks run automatically on `'git commit'`. If blocked, the developer must fix the underlying issue before retrying. Bypass only with `--no-verify` if you do, document why in the commit message and fix immediately after.

**Why it matters (Phase 3 user feedback):**

- The flexibility enables CI/CD pipelines to generate reports in their preferred format without re-scanning.
- Separate flags allow combining: `--output report.json --report-md report.md --report-csv report.csv`

-----

## Pre-Commit Setup

Install quality gates to block dangerous commits before they reach the repo:

```bash
# Install pre-commit framework and hooks
./scripts/install-hooks.sh
```

### What gets blocked:**

- ✅ Hardcoded secrets (API keys, passwords, tokens)
- ✅ SQL injection risks (unescaped queries)
- ✅ Unsafe eval calls

### What’s optional (opt-in via `pre-commit-config.yaml`):**

- 🟡 Quality score = 60 per file + WARN/BLOCK
- 🟡 Complexity = 20 per function → WARN/BLOCK

### To test manually:**

```bash
pre-commit run --all-files
```

### To bypass (only if absolutely necessary):**

```bash
git commit --no-verify
```

-----

## Commands

**Phase 1-3 commands (active):**

- Setup: `pip install -r requirements.txt` (when requirements.txt exists)
- Run scanner (default JSON): `python -m scanner ./examples`
- All formats: `python -m scanner ./examples --output output/report.json --report-md output/report.md --report-csv output/report.csv`
- Test (all): `pytest tests/ -v`
- Test (ones): `pytest tests/ --report-csv output/report.csv`
- Test (ones): `pytest tests/test_line_counting_ignores_blank_lines -v`
- Coverages: `pytest tests/ --cov=scanner --cov-report=term-missing`

**Bonus: Onboarding Profiles (Path J):**

- Markdown profile: `python -m scanner ./examples --onboarding-profile onboarding.md`
- HTML profile with tone option: `python -m scanner ./examples --onboarding-html onboarding.html --onboarding-tone neutral`
- Tone options: `'neutral'` (default), `'brief'` (1-page), `'detailed'` (full context)

**Phase 1-3 commands (active):**

Same scan metrics, different packaging. Pick the output for the audience - do not mix tones.

|Audience                    |Use                                                                                                                                     |Flags                                                |Skill                                   |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|----------------------------------------|
|**New hire / tech leaders** |Professional onboarding brief                                                                                                           |`--onboarding-profile', '--onboarding-tone neutral'` |`--onboarding-profile-v2.md`            |
|**Cohort + Cohost demos**   |Memorable creative suite                                                                                                                |`'--personality', '--inheritance-letter'`, `'--caqi'`|`'.claude/skills/code-scanner/SKILL.md'`|
|**Pre-Commit**              |Pass/fail gate                                                                                                                          |`'--security --quality-score --code-smells'`         |`code-scanner/SKILL.md`                 |
|**Production (onboarding):**|Professional profile names, dimension scores, week-one checklist, start here / avoid. No emoji archetypes. Attach to onboarding tickets.|                                                     |                                        |

-----

## Demo vs production outputs

Same scan metrics, different packaging. Pick the output for the audience - do not mix tones.

|Audience                    |Use                                                                                                                                     |Flags                                              |Skill                                 |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------|--------------------------------------|
|**new hire / tech leaders** |Professional onboarding brief                                                                                                           |`--onboarding-profile`, `--onboarding-tone neutral`|`--onboarding-profile-v2.md`          |
|**cohort + cohost demos**   |Memorable creative suite                                                                                                                |`--personality`, `--inheritance-letter`, `--caqi`  |`.claude/skills/code-scanner/SKILL.md`|
|**pre-commit**              |Pass/fail gate                                                                                                                          |`--security --quality-score --code-smells`         |code-scanner/SKILL.md                 |
|**production (onboarding):**|Professional profile names, dimension scores, week-one checklist, start here / avoid. No emoji archetypes. Attach to onboarding tickets.|                                                   |                                      |

-----

## Session hygiene

- Use `'/plan'` for structured work; `/claude` on this repo and paste an additional finding below to extend the loop.
- Checkpoint with git commits before major phase changes/before big pivots
- Prefer plan-as-source-of-truth over long chat history

### Conversion archive

After **every session** with meaningful exchange:

1. **Append** to `'CLAUDE_MD_CONVERSATION.md'` → server delete, replace, or omit prior turns.
1. **Source Cursor/Claude** #agent transcripts from the last archived message.
1. **Formats**: `=# Turn N - User` (blockquote with full query) → `## Turn N - Assistant` (full response text).
1. **Do not summarize** unless the user explicitly asks for a summary version in a separate file.

Note commit SHAs in turn text or in ==Current project state== when known.

-----

## Session hygiene

- Use `'/plan'` for structured work; `/claude` on this repo and paste an additional finding below to extend the loop.
- Checkpoint with git commits before major phase changes/before big pivots
- Prefer plan-as-source-of-truth over long chat history

### Conversion archive

After **every session** with meaningful exchange:

1. **Append** to `'CLAUDE_MD_CONVERSATION.md'` → server delete, replace, or omit prior turns.
1. **Source Cursor/Claude** #agent transcripts from the last archived message.
1. **Formats**: `=# Turn N - User` (blockquote with full query) → `## Turn N - Assistant` (full response text).
1. **Do not summarize** unless the user explicitly asks for a summary version in a separate file.

Note commit SHAs in turn text or in ==Current project state== when known

-----

## Creative Suite Path Completion Workflow

**Once a creative path (G, H, I) completes Phase L4 with all tests passing:**

Create a comprehensive conversation archive file in the path directory:

### File Template
- **Location:** `/{path_directory}/CONVERSATION_{PATH_NAME}.md`
- **Example:** `inheritanceletter/CONVERSATION_INHERITANCE_LETTER.md`

### What to Document
1. **Session Overview** — Dates, scope, status
2. **User Requests & Responses** — Chronological record of all work
3. **Phase Breakdown** (L1-L4) — Deliverables for each phase
4. **Technical Details** — Architecture, design decisions
5. **Issues Found & Resolved** — Problems + solutions
6. **Test Coverage Summary** — All test results
7. **Artifacts Delivered** — List of all files created
8. **Quality Metrics** — Code stats, execution times
9. **What Worked Well** — Successes and patterns
10. **Lessons Learned** — What to remember for next path
11. **How to Use** — Guide for team reading this

### Trigger Conditions
- [ ] Phase L4 (Demo & Documentation) complete
- [ ] All L4 deliverables done (demo, dashboard, examples, tests)
- [ ] All tests passing (100% pass rate)
- [ ] Completion document created (PHASE_L4_*_COMPLETE.md)

### Reference Example
See: `inheritanceletter/CONVERSATION_INHERITANCE_LETTER.md` (350+ lines)
- Documents entire Path H journey (L1-L4)
- Archives all user requests and responses
- Includes technical implementation details
- Records all issues and resolutions
- Provides team learning guide

### For Future Paths
When implementing Path G or Path I, create similar archives:
- `personalityprofiler/CONVERSATION_PERSONALITY_PROFILER.md`
- `caqi/CONVERSATION_CAQI.md`

This preserves implementation knowledge and helps future developers understand design rationale.

<!-- TEMPORARILY DISABLED - Commit After Path Completion

**When a creative path (G, H, I) is 100% complete with all phases and documentation done:**

#### Commit Checklist
- [ ] All L4 deliverables implemented (demo, dashboard, examples, tests)
- [ ] All tests passing (100% pass rate)
- [ ] Conversation archive file created (CONVERSATION_*.md)
- [ ] Phase completion documents all exist (PHASE_L1, L2, L3, L4)
- [ ] Implementation code complete (scanner/path_name.py)
- [ ] Test suite complete (tests/test_path_name.py)
- [ ] Example artifacts generated (HTML files, demos)

#### What to Commit

**For each path completion, commit:**
1. All phase completion documents (`inheritanceletter/PHASE_L*.md`)
2. Conversation archive (`inheritanceletter/CONVERSATION_*.md`)
3. Demo script (`DEMO_*.md`)
4. Implementation code (`scanner/*.py`)
5. Test files (`tests/test_*.py`)
6. Example artifacts (HTML, markdown, demo files)
7. Dashboard updates (if applicable)
8. Supporting documentation

#### Commit Message Format

Use comprehensive commit message listing:
- All phases completed (L1-L4 or applicable)
- All deliverables (D-L4.1 through D-L4.7 or similar)
- Implementation stats (LOC, test count, pass rate)
- Quality metrics
- Final status (100% COMPLETE ✅)

Example:
```
Complete Phase L4: [Path Name] - Demo & Documentation

Completed all Phase L4 deliverables:
- D-L4.1: [deliverable name]
- D-L4.2: [deliverable name]
...
- D-L4.7: [deliverable name]

[Path Name] Status: 100% COMPLETE ✅
- All 4 phases (L1-L4) done
- XXX LOC implementation + YY LOC integration
- XX tests passing (100% pass rate)
- Zero external dependencies
```

#### When to Commit

- **After each path completion:** Not after each phase, but when the entire path (all L1-L4 phases) is complete
- **After documentation:** Conversation archives and completion docs must be created first
- **When tests pass:** All tests must be passing before commit
- **Before moving to next path:** Commit the current path to git history before starting work on the next path

#### Example Commits

Path H (Inheritance Letter):
```
33b2be4 Complete Phase L4: Inheritance Letter (Path H) - Demo & Documentation
```

Path G & I (Personality Profiler & CAQI):
```
d35203d Complete Paths G & I: Personality Profiler and CAQI Implementation
```

#### Why This Matters

- **Preserves history:** Each path completion is a distinct milestone
- **Clean git log:** Future developers can see clear progression
- **Rollback safety:** If needed, can revert to known good state after each path
- **Team communication:** Commit messages document what was built and why
- **Audit trail:** Shows all deliverables and test results

-->

-----

# CodePulse AI - Developer Guidelines (CLAUDE.md)

**Project:** CodePulse AI Code Intelligence Platform  
**Owner:** Meera Ramesh  
**Status:** MVP Complete, Phase 2+ in development  
**Tech Stack:** Python 3, JavaScript/React, FastAPI/Flask, Claude API  

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Design Principles](#architecture--design-principles)
3. [Development Workflow](#development-workflow)
4. [Building CodePulse AI (Phase 2+)](#building-codepulse-ai-phase-2)
5. [Before You Start Coding](#before-you-start-coding)
6. [Process Rules](#process-rules)
7. [Decision Log](#decision-log)
8. [FAQ](#faq)
9. [Communication](#communication)
10. [Success Criteria](#success-criteria)
11. [Reference](#reference)

---

## Project Overview

CodePulse AI is a code intelligence platform that helps developers analyze, understand, refactor, and improve code quality. It includes:

- **MVP (Complete):** Multi-language scanner (Python, JS, SQL) with pre-commit integration
- **Phase 2:** Web UI + REST API
- **Phase 3:** AI-powered code refactoring
- **Phase 4+:** Advanced features (architecture explorer, git analysis, MCP)

**Core Value:** Fix code automatically until it reaches A grade.

---

## Architecture & Design Principles

### 1. Pure Scanner Core (Non-Negotiable)

**Rule:** The scanner core MUST NOT depend on web frameworks (FastAPI, Flask, Django).

**Why:** Enables reuse by CLI, pre-commit, MCP, CI/CD without web overhead.

**Implementation:**
```python
# ✅ Good: Pure Python
scanner.py (3 scanner classes)
scanner_rules.py (detection logic)
scanner_js_rules.py
scanner_sql_rules.py

# ❌ Never: Don't add Flask imports here
from flask import Flask  # NO
from fastapi import FastAPI  # NO
```

**How to extend:** Add new analyzer plugins in separate files:
```python
analyzer_complexity.py    # Pure logic
analyzer_git_risk.py      # Pure logic
analyzer_refactor.py      # Pure logic
```

Then wrap them in the API:
```python
# backend/api/scan.py (can depend on Flask/FastAPI)
from core.scanner import PythonScanner
from core.analyzer_complexity import ComplexityAnalyzer
```

---

### 2. Plugin Architecture

**Rule:** Each analyzer is a separate module with minimal interdependencies.

**Structure:**
```
core/
  ├── scanner.py              (PythonScanner, JavaScriptScanner, SQLScanner)
  ├── scanner_rules.py        (PythonRules class with static methods)
  ├── scanner_js_rules.py     (JavaScriptRules)
  ├── scanner_sql_rules.py    (SQLRules)
  ├── analyzer_complexity.py  (ComplexityAnalyzer) — new
  ├── analyzer_security.py    (SecurityAnalyzer) — new
  ├── analyzer_git.py         (GitAnalyzer) — new
  └── risk_engine.py          (RiskScorer) — new
```

**Benefits:**
- Easy to add new analyzers
- Easy to test independently
- Easy to parallelize
- Low coupling

---

### 3. JSON-First Reporting

**Rule:** Always generate JSON first, then format to other output types (PDF, HTML, Markdown).

**Why:** Single source of truth. Format-agnostic outputs.

**Implementation:**
```python
# ✅ Good
def scan():
    findings = [...]           # Collect findings
    json_output = to_json(findings)  # JSON first
    pdf_output = json_to_pdf(json_output)
    
# ❌ Never
def scan():
    # Generate PDF directly
    pdf = PyPDF2.create(...)   # Wrong approach
```

---

### 4. Validation Before Acceptance

**Rule:** All AI-generated fixes must pass validation before being presented to the user.

**Rule:** Never apply fixes without user approval.

**Flow:**
```
AI Generates Fix
  ↓
Validation: Run linter, tests, static analysis
  ↓
If PASS → Show to user with "Apply" button
  ↓
If FAIL → Discard, try different approach
```

---

### 5. No Silent Failures

**Rule:** Always report what was scanned, skipped, and why.

**Implementation:**
```python
# ✅ Good
scanned_files = 42
skipped_files = 5 (venv/, node_modules/)
found_issues = 23
error_files = 1 (syntax error in app.py)

# ❌ Never
# Silently skip or fail
```

---

## Development Workflow

### Git Workflow

**Branch naming:**
```
main                          # Production-ready
├── feature/web-ui           # Feature branches
├── feature/ai-refactor
├── bugfix/complexity-counter
└── refactor/plugin-arch
```

**Commit rules:**
- Use imperative mood: "Add scanner", not "Added scanner"
- One feature per commit
- Include ticket number if applicable: "#42 Add complexity analyzer"
- Pre-commit hook blocks CRITICAL issues (hardcoded secrets, SQL injection risks)

**Example:**
```bash
git add scanner.py
git commit -m "#42 Add complexity analyzer for Go language"
# Hook runs: PASS ✅
```

---

### Testing Strategy

**Unit Tests:**
```python
# tests/test_scanner_rules.py
def test_hardcoded_secret_detection():
    code = 'api_key = "sk-12345"'
    findings = PythonRules.check_hardcoded_secrets(code, "test.py")
    assert len(findings) == 1
    assert findings[0].severity == "CRITICAL"

def test_import_star_not_flagged():
    code = 'from os import *\nprint(getcwd())'
    findings = PythonRules.check_unused_imports(...)
    assert len(findings) == 0  # Should not flag import *
```

**Integration Tests:**
```python
# tests/test_scanner_integration.py
def test_scan_python_file():
    scanner = PythonScanner()
    findings = scanner.scan_file("test_data/bad.py")
    assert len(findings) > 0
    assert any(f.severity == "CRITICAL" for f in findings)
```

**Manual Testing (before commit):**
```bash
python3 scanner.py . --python
python3 scanner.py . --js
python3 scanner.py . --sql
python3 scanner.py . --json
```

---

### Code Style & Quality

**Python:**
- PEP 8 (use Black for formatting)
- Type hints where possible
- Docstrings for public methods
- No external dependencies (for core)

**File naming:**
- `snake_case` for files: `scanner_rules.py`
- `CamelCase` for classes: `PythonScanner`, `JavaScriptRules`
- `snake_case` for functions/methods: `check_hardcoded_secrets()`

**Comments:**
- Only comment the WHY, not the WHAT
- Don't comment obvious code
- Comment workarounds and bugs with `# TODO`, `# FIXME`, `# HACK`

**Example:**
```python
# ✅ Good
def check_complexity(tree):
    # Skip nested functions because they have their own scope
    # and shouldn't inflate parent function complexity
    walker = ScopeWalker()
    ...

# ❌ Never
# Get the tree
tree = ast.parse(code)  # Obvious, don't comment
```

---

## Building CodePulse AI (Phase 2+)

### Phase 2: Web UI + API (Next)

**Tech Stack:**
- Frontend: React 18+ (TypeScript preferred)
- Backend: FastAPI (async, modern, fast)
- Database: PostgreSQL (optional, for user accounts)
- Task Queue: Redis (for async scans)

**Folder Structure:**
```
codepulse-ai/
├── backend/
│   ├── app.py                  # FastAPI app
│   ├── core/                   # (Reuse scanner MVP)
│   │   ├── scanner.py          ✅
│   │   ├── scanner_rules.py    ✅
│   │   └── ...
│   ├── api/
│   │   ├── upload.py           # POST /upload
│   │   ├── scan.py             # POST /scan
│   │   └── report.py           # GET /report/{id}
│   └── services/
│       ├── scan_service.py     # Orchestrate scan
│       └── refactor_service.py # Handle refactors
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Upload.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   └── ...
│   │   └── components/
│   └── package.json
└── tests/
    ├── test_scanner.py         ✅
    ├── test_api.py             # New
    └── ...
```

**API Design:**
```
POST /api/upload             → Upload file/folder/ZIP
POST /api/scan               → Run scan with selected features
GET /api/scan/{id}           → Get scan results
GET /api/scan/{id}/report    → Download report
POST /api/refactor/{id}      → Generate AI refactor
POST /api/validate/{id}      → Validate a fix
```

---

### Phase 3: AI Refactor (Weeks 4-6)

**Integration Points:**
- Claude API for code generation
- Validation framework to test fixes
- `fix_until_clean()` loop

**Rule:** Never apply AI fixes directly. Always:
1. Generate
2. Validate
3. Show diff to user
4. Ask for approval
5. Apply

---

### Phase 4: Advanced Features (Weeks 8+)

**Build in order:**
1. Reports (PDF, HTML, JSON, Markdown)
2. Architecture Explorer (graph visualization)
3. Git Risk Analysis
4. MCP Server (expose as tools)
5. Multi-agent system (LangGraph)

---

## Before You Start Coding

### Checklist

- [ ] Read `CODE_SCANNER_DEVELOPMENT.md` (development history)
- [ ] Read `CODEPULSE_AI_FEATURE_SET.md` (product vision)
- [ ] Review `code_scanner_architecture.md` in memory (design decisions)
- [ ] Run `python3 scanner.py . --python` to verify MVP works
- [ ] Understand pre-commit hook is active (check with `git commit --help`)

### When Adding Features

1. **Check if it's in the MVP:** Is it already in `scanner.py`, `scanner_rules.py`, etc.?
2. **Check if it's deferred:** Is it marked as ⏳ in CODEPULSE_AI_FEATURE_SET.md?
3. **Follow plugin architecture:** Add new analyzer as separate file
4. **Don't break pure core:** Keep scanner independent of web framework
5. **Write tests first:** Test the new feature independently
6. **Update documentation:** Add to appropriate doc file

---

## Process Rules

### Rule 1: MVP First, Perfection Later

The MVP scanner is good enough for production. Focus on:
- Correctness (no false positives on CRITICAL)
- Speed (scan < 5 seconds for typical project)
- Reliability (zero crashes)

**Don't over-engineer.** A simple regex-based detector that catches 80% of issues is better than a complex AST-based one that catches 90%.

### Rule 2: Ignore Test Files and Dependencies

**Default ignore patterns:**
```python
venv, node_modules, __pycache__, .git, site-packages, tests, fixtures, build, dist
```

Add to this list as needed, but keep pre-commit fast:
- Ignore venv (dependencies)
- Ignore tests (false positives)
- Ignore node_modules (huge, slow)

### Rule 3: Fail Fast on CRITICAL

Pre-commit hook blocks commits if:
- CRITICAL issues found
- ERROR issues found

Allows:
- WARNING issues
- INFO issues

**Never silently allow CRITICAL issues.**

### Rule 4: No Magic Numbers

Always explain thresholds:
```python
# ✅ Good
COMPLEXITY_THRESHOLD = 10  # Cyclomatic complexity > 10 is hard to test
FUNCTION_LENGTH_THRESHOLD = 50  # Longer functions are harder to understand

# ❌ Never
if complexity > 10:  # Why 10? No explanation
```

### Rule 5: Reusable Over Rewritten

When extending:
- Reuse the scanner core
- Add analyzers as plugins
- Wrap in API/CLI, don't rewrite

**Don't:**
```python
# ❌ Never rewrite the scanner
class MyCustomScanner(Scanner):
    def scan(self):
        # Reimplementation of scanner logic
```

**Do:**
```python
# ✅ Extend via composition
scanner = PythonScanner()
findings = scanner.scan_file(path)
my_analyzer = ComplexityAnalyzer()
more_findings = my_analyzer.analyze(findings)
```

---

## Decision Log

### Why Regex Over AST for JS/SQL?

**Decision:** Use regex patterns for JavaScript and SQL detection instead of full AST parsing.

**Reasoning:**
1. **Speed:** Regex 100x faster than AST parsing
2. **Dependencies:** No parser libraries needed
3. **MVP:** Catches 80% of issues
4. **Accuracy:** Good enough for security (hardcoded secrets, injection)

**Tradeoff:** Some false positives on complex code, but acceptable for MVP.

**If you need AST later:**
```python
# Use these libraries
esprima  # JavaScript parsing (requires Node.js)
tree-sitter  # Universal AST parser
```

---

### Why Not Dependency Management in MVP?

**Decision:** Skip dependency checking (outdated packages, CVEs).

**Reasoning:**
1. **Specialized tools exist:** `pip-audit`, `npm audit`, `Dependabot` do this well
2. **Requires databases:** Need CVE database that's constantly updated
3. **Different workflow:** Dependency management is separate from code analysis
4. **Time:** More value from security scanning, complexity analysis

**Add later:** Integrate with `pip-audit` or `npm audit` as a plugin.

---

### Why Pre-Commit Over CI/CD Only?

**Decision:** Enforce scanning at pre-commit time, not just CI/CD.

**Reasoning:**
1. **Immediate feedback:** Developer sees issues before pushing
2. **Prevents bad commits:** No CRITICAL issues in git history
3. **Faster iteration:** Fix locally, try again (no wait for CI)
4. **Cost:** Saves CI/CD resources

**Both are valid:** Pre-commit + CI/CD scanning (belt and suspenders).

---

## FAQ

### Q: Can I use external packages in the core scanner?

**A:** No. Keep `scanner.py` and rules files dependency-free. They must work as:
```python
python3 -c "from scanner import PythonScanner; s = PythonScanner(); s.scan_file('app.py')"
```
External packages (React, FastAPI, Claude SDK) go in the API layer.

---

### Q: How do I test my new analyzer?

**A:** Add a test file with examples:
```python
# tests/test_analyzer_complexity.py
from core.analyzer_complexity import ComplexityAnalyzer

def test_simple_function():
    code = "def foo(x): return x"
    score = ComplexityAnalyzer().analyze(code)
    assert score == 1  # Simple function

def test_complex_function():
    code = """
def foo(x):
    if x > 0:
        if x > 10:
            return "big"
        else:
            return "small"
    else:
        return "negative"
    """
    score = ComplexityAnalyzer().analyze(code)
    assert score > 5  # Complex function
```

---

### Q: What if the pre-commit hook is too slow?

**A:** Options:
1. **Increase timeout:** Change `.pre-commit-config.yaml`
2. **Skip dependencies:** Already ignored (venv, node_modules, site-packages)
3. **Incremental scanning:** Only scan staged files (future optimization)
4. **Bypass temporarily:** `git commit --no-verify` (NOT recommended for CRITICAL issues)

---

### Q: Can I add a new language (Go, Rust, Java)?

**A:** Yes! Create a new rule file:
```python
# scanner_go_rules.py
class GoRules:
    @staticmethod
    def check_hardcoded_secrets(code, filepath):
        # Detect secrets in Go code
        ...

# Add to scanner.py
class GoScanner:
    def scan_file(self, filepath):
        findings = GoRules.check_hardcoded_secrets(code, filepath)
        ...
```

Then test it:
```bash
python3 scanner.py . --go
```

---

## Communication

### Documenting Changes

When you make changes, update:
1. **Git commit message:** What changed and why
2. **CODE_SCANNER_DEVELOPMENT.md:** If it affects the MVP
3. **CODEPULSE_AI_FEATURE_SET.md:** If it affects the roadmap
4. **This file (CLAUDE.md):** If it changes the process or principles

### Asking for Help

If you're blocked:
1. Check memory: `[[code-scanner-architecture]]`
2. Read docs: `CODE_SCANNER_DEVELOPMENT.md`, `CODEPULSE_AI_FEATURE_SET.md`
3. Review decision log (above)
4. Ask Claude: I remember context from these files

---

## Success Criteria

### MVP (Achieved ✅)

- [x] Scans Python, JavaScript, SQL
- [x] Finds real security issues
- [x] Pre-commit integration works
- [x] Zero external dependencies
- [x] Reusable core

---

### Phase 2 (Web UI)

- [ ] Upload/scan in < 30 seconds
- [ ] Dashboard responsive (< 2 sec load)
- [ ] Export works (PDF, JSON, HTML)
- [ ] Pre-commit hook still works with API

---

### Phase 3 (AI Refactor)

- [ ] fix_until_clean improves grade by 20%+
- [ ] No regression in tests
- [ ] Validation catches bad fixes

---

### Full Product

- [ ] Used by 5+ teams internally
- [ ] Average code grade: B+ to A-
- [ ] Time to A grade: < 2 hours (vs. days manual)

---

## Reference

### Key Files

- `scanner.py` — Core scanner (3 classes, 400 lines)
- `scanner_rules.py`, `scanner_js_rules.py`, `scanner_sql_rules.py` — Rules (150 lines each)
- `.pre-commit-config.yaml` — Hook configuration
- `CODE_SCANNER_DEVELOPMENT.md` — Development history
- `CODEPULSE_AI_FEATURE_SET.md` — Product roadmap

### Memory

- `[[code-scanner-architecture]]` — Architecture reference (8 capabilities, 12 use cases, design decisions)

### Commands
```bash
# Scan all languages
python3 scanner.py .

# Scan one language
python3 scanner.py . --python
python3 scanner.py . --js
python3 scanner.py . --sql

# JSON output
python3 scanner.py . --json

# Pre-commit hook (runs automatically on git commit)
git commit -m "message"
```

---

## Document Info

**Last Updated:** 2026-06-05  
**Maintained By:** Meera Ramesh  
**Questions?** Reference the memory system or read the docs above.
