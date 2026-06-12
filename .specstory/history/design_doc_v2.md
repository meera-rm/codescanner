# Code Scanner — Design Document V2

**Based on:** Hackathon_Training_Guide.md Core Requirements  
**Status:** Design complete — Phases 1-4 defined; align with "Hackathon_Part_II_guide.md"  
**Approach:** PDLC (Design → Plan → Implement)

## What You're Building

A code scanner that:

- Reads and analyzes source code files
- Extracts meaningful metrics (line count, complexity, patterns)
- Generates human-readable reports
- Focuses on correctness and testability, not polish

**Scope:** Keep it small. Get core features working reliably. Save advanced visualizations for bonus rounds.

## Core Requirements (From Hackathon Guide)

### Analysis Capability

Extract metrics from code files:

- **File characteristics:** line count, complexity metrics, patterns
- **Function analysis:** identify functions/methods and their properties
- **Code patterns:** detect specific coding patterns (error handling, logging, etc.)

### Output Format

- Generate human-readable reports
- Structured analysis that's easy to parse
- Clear presentation of findings

### Code Quality Standards

- Write clear, maintainable code
- Follow consistent patterns
- Use meaningful naming conventions

## Analysis Features (Select 3+ for Phase 1-2)

| Feature | Phase | Input | Output |
|---------|-------|-------|--------|
| Line Counting | 1 | File content | `{ lines_total, lines_code, lines_blank, lines_comment }` |
| Complexity Analysis | 2 | Content search | `{ try_catch_count, raise_count }` |
| Error Handling Detection | 2 | Content search | `{ error_handling_count, try_except_count, raise_count }` |
| Logging Detection | 2 | Pattern matching | `{ logging_call_count, log_statements }` |

**Phase 1 Minimum:** Line counting + function identification  
**Phase 1 expansion:** Complexity + error handling + logging  
**Phase 3:** Human-readable reports (Markdown + optional CSV)  
**Phase 4:** Encode learnings into ground rules (CLAUDE.md)

## Project Phases

### Phase 1: Bootstrap Test Scanner (3-4 hours)

**Goal:** Get a working scanner that reads files and extracts basic metrics.

**Deliverables:**
- ✅ Scanner reads code files and analyzes them
- ✅ Basic metrics extraction working (at least 2 features)
- ✅ Test harness demonstrating functionality
- ✅ Code is readable and documented

**What to build:**
- File reader that handles I/O errors
- Language detection by file extension (Python, JavaScript)
- Line counting (total, code, blank, comments)
- Function/class detection (count only, no AST yet)
- Basic test cases with sample code files
- Output as structured dict or simple JSON

**Avoids:**
- Don't over-engineer (get something working quickly)
- Don't build reports yet (Phase 3)
- Don't support every language (start 1-2)
- Don't aim for perfect edge case handling

**Definition of Done (Phase 1):**
- Scanner can read a file and extract line metrics
- Test cases pass (at least 3 tests)
- Results vary meaningfully across different test files
- Code is readable and documented
- Committed to git

### Phase 2: Add Analysis Features (~45 min)

**Goal:** Expand metrics beyond basic counting. Implement complexity and pattern detection. Generate reports.

**Deliverables:**
- ✅ Advanced metrics extraction (3 features: complexity, error handling, logging)
- ✅ Function/class analysis (AST-based where applicable)
- ✅ Extended test coverage (one test per feature)

**What to build:**
- Cyclomatic complexity per function (Python AST)
- Error handling pattern detection (try/except/raise)
- Logging pattern detection (print, logging., logger.)
- Tests for each new feature
- Composable Metrics Pipeline: File → [Line Counter] → [Complexity] → [Patterns] → JSON

**Alignment check:** Before each feature, ask "Tell me what you're going to build."

**Avoids:**
- Don't merge features — keep each testable in isolation
- Don't refactor Phase 1 unless necessary
- Don't build full reports yet (Phase 3)

**Reflect before moving on:**
- Which features integrated smoothly vs. required iteration?
- Corrections repeated more than once? Write them down — that's encoding.

**Definition of Done (Phase 2):**
- 3 analysis features implemented
- Each feature has tests
- Metrics appear in JSON output
- No obvious bugs in main features
- Committed to git

### Phase 3: Generate Reports (~30 min)

**Goal:** Add human-readable output on top of JSON metrics.

**Deliverables:**
- ✅ Markdown summary report (tables + summary sections)
- ✅ Optional: CSV export (one row per file — bonus-friendly)
- ✅ CLI flags: `--output report.json`, `--report-md report.md`
- ✅ [Optional stretch]: HTML dashboard with charts

**What to build:**
- `generate_markdown_report()` → summary, per-file metrics, pattern counts
- Show per-file table (lines, functions, complexity, patterns)
- Top complex functions / files (if applicable)

**Avoid:**
- Don't rebuild metrics logic — reports consume existing JSON/dict structure
- Don't require HTML for Part I Done — Markdown or CSV is enough

**Report sections (Markdown):**
- Summary totals
- Per-file table (lines, functions, complexity, patterns)
- Top complex functions / files (if applicable)

**Example Markdown:**

```markdown
# Code Analysis Report

| File | Lines | Functions | Complexity | Patterns |
|------|-------|-----------|------------|----------|
| example.py | 50 | 3 | 4 |
| helper.py | 20 | 1 | 1 |

## Patterns Detected
- Error handling: 5
- Logging calls: 12
```

**Definition of Done (Phase 3):**
- JSON + at least one human-readable format (Markdown or CSV)
- Report runs on examples/ without errors
- Report is readable and shows all metrics
- Committed to git

### Phase 4: Encode What You've Learned (~remaining time)

**Goal:** Formalize ground rules so you never repeat the same corrections.

**Deliverables:**
- ✅ CLAUDE.md (or .cursor/rules/) updated with +2-3 meaningful, battle-tested rules

**Two approaches:**

1. **Your observations:** Corrections made more than once become rules. Examples:
   - "When this scanner on test fixtures after each metric change"
   - "Tests named after behavior, not function names (test_line_counting_ignores_blanks not test_count_lines())"
   - "Use recursive AST traversal for complexity — not ast.walk() — across nested functions"

2. **The retro move:** Ask the agent:
   - Review our conversation. What ground rules would have prevented our correction cycles? Suggest 2-3 rules I should add to CLAUDE.md.

**Part I Definition of Done (bonus):**
- CLAUDE.md has 2-3+ specific, actionable rules
- At least one bonus requirement attempted (tests, CSV, RESEARCH.md, etc.)
- Part I checkpoint passed (see Hackathon_Part_II_guide.md)
- Committed to git

## Design Decisions

### Language & Tech Stack

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary Languages | Python 3.10+ | AST support, fast CLI development |
| Analysis Languages | Python only (Phase 1-2) | AST available; extend to JS/others in bonus |
| Test Frameworks | pytest | Standard, good fixtures |
| Dependencies | Minimal (ast, json built-in) | Keep it simple |

### CLI Interface (Evolve as you build)

**Phase 1:**
```bash
python scanner.py path/to/file.py
# Output: dict or JSON to stdout
```

**Phase 2:**
```bash
python scanner.py path/to/dir --output report.json
# JSON only — metrics, no human report yet
```

**Phase 3:**
```bash
python scanner.py examples/ --output report.json --report-md report.md
python scanner.py examples/ --output report.json --report-csv report.csv
# Optional stretch: --report-html report.html
```

### Data Structures

Keep it simple — use dicts or dataclasses:

**Phase 1:**
```python
metrics = {
    'file': 'example.py',
    'lines_total': 50,
    'lines_code': 40,
    'lines_blank': 5,
    'lines_comment': 5,
    'function_count': 3
}
```

**Phase 2:**
```python
metrics = {
    'file': 'example.py',
    'lines_total': 50,
    'lines_code': 40,
    'lines_blank': 5,
    'lines_comment': 5,
    'function_count': 3,
    'functions': [
        {'name': 'foo', 'lines': 10, 'complexity': 2},
        {'name': 'bar', 'lines': 8, 'complexity': 1}
    ],
    'error_handling_count': 2,
    'logging_count': 3
}
```

### Parsing Strategy

| Analysis | Approach |
|----------|----------|
| Line Counting | Read lines, count blank/comment patterns |
| Function Detection | AST for Python; regex fallback for others |
| Complexity | AST branches (if/for/while/and/or) |
| Patterns | Regex or node searches |

**Why AST for Python:** Accurate, reliable, handles complex syntax.

### Report Format

**Phase 1:** No report needed (dict/JSON output is enough)

**Phase 2:** JSON only — full metrics structure

**Phase 3:** Human-readable output:
- Markdown tables: Summary + per-file breakdown (required — pick one format minimum)
- CSV: Per-file row export (bonus-friendly)
- HTML dashboard: Optional stretch (charts/graphs)

**Example Markdown:**

```markdown
# Code Analysis Report

| File | Lines | Functions | Complexity | Patterns |
|------|-------|-----------|------------|----------|
| example.py | 50 | 3 | 4 |
| helper.py | 20 | 1 | 1 |

## Patterns Detected
- Error handling: 5
- Logging calls: 12
```

### File Structure (Grow As Needed)

```
hackathon/
├── CLAUDE.md                         # Ground rules
├── design_doc.md                     # Original design
├── design_doc_v2.md                  # This file (hackathon-focused)
├── PLAN.md                           # Create via /plan
├── scanner.py                        # Single file for Phase 1 (OK to start here)
│   or
├── scanner/                          # Package when needed
│   ├── __init__.py
│   ├── analyzer.py
│   ├── metrics.py
│   └── report.py
├── tests/
│   ├── test_scanner.py               # Core tests
│   ├── fixtures/
│   │   ├── sample.py
│   │   └── errors.py
│   └── examples/                     # Real code to scan
```

**Start simple:** Single scanner.py file is fine for Phase 1.  
**Refactor when:** You have 3+ independent metric functions.

### Common Commands

**Phase 1:**
```bash
python scanner.py examples/sample.py
pytest tests/ -v
pytest tests/test_scanner.py::test_line_counting_ignores_blanks -v
```

**Phase 2 (metrics + JSON):**
```bash
python scanner.py examples/ --output report.json
pytest tests/ -v
```

**Phase 3 (imports):**
```bash
python scanner.py examples/ --output report.json --report-md report.md
python scanner.py examples/ --output report.json --report-csv report.csv
# Optional stretch: --report-html report.html
```

## Testing Strategy

### Phase 1 Tests

- Test line counting (total, code, blank, comment)
- Test function detection (count is correct)
- Test error handling (file not found, unreadable)
- Test with different file types (if supporting 2+ languages)

### Phase 2 Tests

- Add a test for each new feature (complexity, error handling, logging)
- Use fixtures (sample code files) for consistent test data
- Example test name: `test_complexity_counts_branching_correctly`

### Phase 3 Tests

- Markdown report contains summary section
- CSV has header row and one row per scanned file
- Reports handle edge cases (empty dir, special characters in paths)

### Test Fixtures (Sample Code)

Create simple .py files in `tests/fixtures/`:

```python
# test_simple.py - 5 lines, 1 function, no complexity
def hello():
    print("hi")

# test_complex.py - nested if/loops for complexity testing
def calculate(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                try:
                    log("even")
                except:
                    pass
```

## Ground Rules (Finalized in Phase 4)

Codify in CLAUDE.md after Phases 1-3:

- **Design before coding:** Complete this design doc before Phase 1. Check alignment after each feature (A, B, C).
- **Responsible features:** Each metric function is tested in isolation. No hidden dependencies.
- **Test naming:** Name tests after behavior, not function names (test_line_counting_ignores_blanks not test_count_lines()).
- **Error handling:** File I/O and parsing errors fail gracefully with clear messages.
- **Scope focus:** Core features first; HTML dashboards and extra menu features are bonus.
- **Run on real code:** After metric changes, scan examples/ and verify JSON output.

## Key Checkpoints

### Before Phase 1 Code

- Decide on language (Python?)
- Decide on initial metric features (at least 2)
- Understand test strategy (pytest + fixtures)
- Know what "done" looks like (what output format?)

### After Phase 1

- Scanner reads a file and extracts line metrics
- 3+ test cases passing
- Results vary meaningfully across different test files
- Code is readable
- Committed to git

### After Phase 2

- 3 analysis features implemented
- Each feature has tests
- Metrics appear in JSON output
- Committed to git

### After Phase 3

- Markdown and/or CSV report generated
- JSON + human report both work
- All Part I core output requirements met
- Committed to git

### After Phase 4 (Part I complete)

- CLAUDE.md has 2-3+ meaningful encoded rules
- At least one bonus requirement attempted (tests, CSV, RESEARCH.md, etc.)
- Part I checkpoint passed (see Hackathon_Part_II_guide.md)
- Committed to git

## Obstacles to Watch

| Obstacle | How to Spot | How to Fix |
|----------|------------|-----------|
| Over-engineering | Building abstractions before knowing what you need. | Start simple (single file OK). Refactor only when needed. |
| Scope creeping | "What if we also track security patterns?" | Finish Phase 1 first; Phase 2 locked to 3 features. |
| Context rot | Agent contradicts earlier decisions/clear between phases; plan is source of truth | |
| Tests failing | Red tests at end of phase | Debug in fresh session with only failing test |
| Report format unclear | "How should table look?" | Use design_doc_v2.md example; keep it simple |

## Bonus Ideas (after Part I / stretch)

Save these for after Phases 1-4 or Part II:

- Code duplication detection
- Security anti-patterns
- Documentation coverage (docstrings %)
- Import/dependency tracking
- HTML dashboard
- CSV export
- Multi-language support (JavaScript, TypeScript, Java)
- Performance hotspot detection
- Trend tracking over time

## Next Steps

1. Review this design. ✓
2. Create PLAN.md: `/plan` — use this design as input
3. Phase 1: bootstrap scanner with line counting and function detection
4. Phase 2: analysis features + tests
5. Phase 3: Markdown/CSV reports
6. Phase 4: encode rules in CLAUDE.md

## Resources

- Hackathon_Part_II_Guide.md — Part I exercise brief (Phases 1-4)
- CLAUDE.md — Agent ground rules (expand in Phase 4)
- PLAN.md — Implementation plan
