# Code Scanner - Complete Plan Audit Report
**Date:** 2026-06-06  
**Status:** All plans reviewed for correctness, errors, gaps, and strength  
**Scope:** Creative Suite GHI + Onboarding Profile v2 + Part II Creative Paths

---

## Executive Summary

**Overall Status:** 🟡 AMBER - Plans are well-structured but have gaps, duplications, and inconsistencies that should be resolved before implementation.

**Key Findings:**
- **Strengths:** Clear phase structures, good design rationale, realistic time estimates
- **Critical Issues:** 3 found (path naming conflicts, edge case handling missing, unclear acceptance criteria)
- **Medium Issues:** 8 found (duplications, vague deliverables, missing acceptance criteria)
- **Minor Issues:** 12 found (grammar, em-dash vs hyphen, missing examples)

**Recommendation:** Resolve critical and medium issues before starting any implementation.

---

# SECTION 1: CREATIVE SUITE GHI (PATHS G + H + I)

## Plan File: `plan-creative-suite-ghi.md`

### ✅ STRENGTHS

1. **Clear Architecture** — All 3 paths are interpretation layers (smart design avoids duplication)
2. **Good Meta-Plan** — Explains why GHI works together before diving into details
3. **Realistic Time Estimates** — 4-5 hours total is achievable
4. **Strong Demo Script** — 3-minute demo with clear flow (hook → run → output → before/after)
5. **Ground Rules** — Enforces evidence-based claims (no unsourced recommendations)
6. **File Structure** — Clear target structure for all 3 paths

### 🔴 CRITICAL ISSUES

**Issue #1: Path Naming Conflict in Part II Plan**
- **Location:** plan-creative-suite-ghi.md refers to Path G (Personality Profiler)
- **Conflict:** plan-part-ii-creative-paths.md ALSO uses Path G for "MCP Integration" (lines 414-468)
- **Impact:** Confusing when reading Part II; unclear which G is which
- **Fix:** Rename Part II's MCP integration to Path M or clearly separate "Creative Suite G/H/I" from "Part II Paths A-F"

**Issue #2: CLI Flags Have Inconsistent Dashes**
- **Location:** Lines 32-44 use em-dashes (—) instead of regular hyphens (-)
- **Problem:** Em-dashes won't work in CLI parsing; will cause command failures
- **Fix:** Replace all `—` with `--` in combined demo command (lines 32-44)
- **Affected Flags:**
  ```
  ❌ —output, —report-md, —security, —personality-html, —inheritance-letter, —cagi
  ✅ --output, --report-md, --security, --personality-html, --inheritance-letter, --cagi
  ```

**Issue #3: Missing Edge Case Handling**
- **Location:** Entire plan assumes all 3 paths will have valid data
- **Gap:** What if:
  - No security findings exist? (Inheritance Letter confessions section empty)
  - Codebase is tiny (< 5 files)? (CAGI may not be meaningful)
  - All traits are low (Quiet Newcomer fallback always triggered)?
- **Fix:** Add section "Edge Cases & Graceful Degradation" specifying behavior for each

### 🟡 MEDIUM ISSUES

**Issue #4: Demo Script Assumes Specific Example Files**
- **Location:** Lines 71, 81 reference `insecure.py`, `logging_heavy.py`, `realistic_app.py`
- **Problem:** If these files don't exist or have different issues, demo fails
- **Fix:** Either:
  - Create fixture files with guaranteed issues, OR
  - Make demo flexible: "Open whichever HTML shows highest CAGI score"
- **Acceptance Criteria:** Demo must work with ANY codebase, not just `examples/`

**Issue #5: MVP Sign-Off Incomplete**
- **Location:** Lines 174-184
- **Gap:** Missing acceptance criteria for:
  - Combined command must work without errors
  - All 3 HTML outputs must be self-contained (no external deps)
  - Before/after beat (specific metrics expected to change by how much?)
- **Fix:** Add concrete acceptance criteria:
  ```
  - [ ] Combined command runs < 5 seconds on examples/
  - [ ] CAGI drops ≥ 50 points after insecure.py fix
  - [ ] Personality tone shifts from Reckless to Cautious
  - [ ] Inheritance letter secrets section shrinks by ≥ 50%
  ```

**Issue #6: No Integration Testing Plan**
- **Location:** Entire plan
- **Gap:** How do we verify all 3 paths work together?
  - Do they share the same scan output?
  - Do they interfere with each other's flags?
  - Can they run sequentially or only together?
- **Fix:** Add Phase 0 (Integration):
  ```
  Phase 0: Integration Testing (~30 min)
  - [ ] Verify all 3 flags work in single command
  - [ ] Check for flag conflicts (e.g., --personality and --personality-html)
  - [ ] Ensure shared JSON output compatible with all 3 modules
  - [ ] Test with clean examples/, then with insecure.py fix
  ```

**Issue #7: Unclear About Shared Metrics**
- **Location:** Lines 119-138 (Shared Architecture section)
- **Problem:** References optional `scan_summary.py` refactor but doesn't specify:
  - When should this be done? Before, during, or after I/G/H?
  - What metrics should be shared? (complexity? security counts? quality score?)
  - How do existing modules use shared totals?
- **Fix:** Create explicit contract:
  ```python
  # scan_summary.py (optional, only if 2+ paths share logic)
  def aggregate_repo_metrics(metrics_list):
      """Returns shared totals for all paths"""
      return {
          "avg_complexity": float,
          "security_high_count": int,
          "security_medium_count": int,
          "avg_quality_score": float,
          "doc_coverage_ratio": float,
          "circular_dep_count": int,
          "total_functions": int,
      }
  ```

**Issue #8: No Backwards Compatibility Strategy**
- **Location:** Entire plan
- **Gap:** What happens to existing JSON output when 3 new sections are added?
  - Old tools parsing the JSON might break
  - Need clear versioning strategy
- **Fix:** Add section:
  ```
  Backwards Compatibility:
  - Add "version": "2.0" to JSON root
  - Personality/inheritance/cagi sections are OPTIONAL (nested under top-level keys)
  - Old code can safely ignore: json.get("personality", {})
  - Update RESEARCH.md to document JSON schema v2.0
  ```

### 🔵 MINOR ISSUES

1. **Typo in table (line 100):** "Optional bonus flags" column header is unclear
2. **Missing dashboard link:** No mention of updating `scanner_dashboard.html` to link to all 3 outputs
3. **No error handling doc:** What if HTML generation fails partway through?
4. **CLI section (lines 27-45):** No indication which flags are optional vs required for demo

---

# SECTION 2: INHERITANCE LETTER (PATH H)

## Plan File: `plan-inheritance-letter.md`

### ✅ STRENGTHS

1. **Strong Design Rationale** — "Dear developer" angle is memorable and unique
2. **Clear Tone Selection** — Apologetic/Cautious/Confident mapping is explicit
3. **Letter Structure** — Well-thought-out sections (proud, not_proud, secrets, avoid, start_here, tips)
4. **Evidence Requirements** — Enforces citations (file, line, metric) — prevents generic advice
5. **Comprehensive Phases** — L1-L4 are clearly delineated with deliverables

### 🔴 CRITICAL ISSUES

**Issue #1: Phase L2 Is Duplicated**
- **Location:** Lines 178-299 (Phase L2 appears TWICE, nearly identical)
- **Impact:** Confusing to read, unclear if intentional or copy-paste error
- **Fix:** Remove one copy (probably lines 242-299, keep lines 178-240)

**Issue #2: Start_Here Selection Logic Is Vague**
- **Location:** Line 210 (Phase L2 section selection rules)
- **Problem:** Rule says "1-2 files: complexity = 1.5, no security; no error handling"
  - What does "complexity = 1.5" mean? Cyclomatic complexity can't be 1.5 (must be integer)
  - Does "no error handling" mean good files (we want them) or bad files (we avoid)?
- **Fix:** Clarify selection logic:
  ```
  'start_here': [
      Selection: 1-2 files where:
      - Cyclomatic complexity ≤ 3 (simple)
      - No security findings (safe)
      - Has try/except OR error handling present (good practices)
      - Good documentation (quality_score > 70)
      
      If no such files exist: 
      - Fall back to lowest complexity file
      - Add note: "There are no clean entry points; start with X anyway"
  ]
  ```

**Issue #3: Avoid Section Missing Edge Case**
- **Location:** Line 209
- **Problem:** "avoid" section selects "Top 3 functions by complexity_average"
  - What if codebase has < 3 functions?
  - What if all functions are simple?
- **Fix:** Add fallback rules:
  ```
  'avoid': [
      Default: Top 3 functions by complexity
      Fallback 1: If < 3 functions, use all
      Fallback 2: If no complex functions, use functions with most lines
      Fallback 3: If all functions are trivial, say "No dangerous functions found"
  ]
  ```

**Issue #4: Secrets Section May Be Empty**
- **Location:** Line 208
- **Problem:** Plan says "All security_findings with severity=high, first-person phrasing"
  - What if security_findings is empty?
  - Should the letter omit "Secrets" section or say "I have no secrets"?
- **Fix:** Clarify in L2:
  ```
  Omit sections gracefully:
  - No security findings → Skip confessions or say "I have no secrets I'm aware of"
  - No low-complexity files → Skip start_here or say "All entry points are complex"
  - No high-complexity functions → Skip avoid or say "I have no dangerous functions"
  ```

**Issue #5: Tone Selection Has Ambiguity**
- **Location:** Lines 88-99 (Tone Catalog table)
- **Problem:** Tone triggers overlap:
  - "avg quality < 55" is Apologetic
  - "avg quality 55-74" is Cautious
  - But what if avg_quality = 55 exactly? Both match.
- **Fix:** Use explicit ranges:
  ```
  | Tone | Trigger | Priority |
  | Apologetic | security_high ≥ 1 OR avg_quality < 55 | Check first |
  | Cautious | avg_quality 55-74 OR total_smells > 10 | Check second |
  | Confident | avg_quality ≥ 75 AND security_clean AND smells ≤ 5 | Check third |
  | Fallback | (any ambiguous case) | Cautious |
  ```

**Issue #6: First Week Tips Are Template-Based But Vague**
- **Location:** Line 211 (section selection rules)
- **Problem:** Says "Rule-based from tone + dominant issues (see templates below)" but templates are not shown
- **Gap:** No templates provided for what tips to suggest based on tone/metrics
- **Fix:** Add section after tone catalog with explicit templates:
  ```
  First Week Tips Templates:
  
  Apologetic tone → Tips focus on security fixes:
  1. "Add pre-commit security check to catch secrets before commit"
  2. "Review all hardcoded secrets in [files]; create config instead"
  3. "Schedule security audit with team lead"
  
  Cautious tone → Tips focus on quality improvements:
  1. "Read CLAUDE.md for project ground rules"
  2. "Refactor [function] to reduce complexity from X to <10"
  3. "Add docstrings to [files]; current coverage is X%"
  
  Confident tone → Tips focus on learning & contribution:
  1. "Set up pre-commit hooks locally (script in CLAUDE.md)"
  2. "Review [file] for architecture patterns"
  3. "Try adding tests for [function]; current coverage is X%"
  ```

### 🟡 MEDIUM ISSUES

**Issue #7: Fixture Letters Not Defined**
- **Location:** Lines 227-232 (L2.3 Fixture letters)
- **Problem:** Says create fixtures but doesn't define what they should contain
- **Gap:** No schema for `apologetic_repo.json`, `cautious_repo.json`, `minimal_repo.json`
- **Fix:** Add fixture schemas:
  ```python
  # apologetic_repo.json
  {
    "files": [{
      "path": "insecure.py",
      "quality_score": 40,
      "complexity": 8,
      "security_findings": [
        {"type": "hardcoded_secret", "severity": "high", "line": 6}
      ]
    }],
    "avg_quality_score": 45,
    "security_high_count": 2
  }
  ```

**Issue #8: No Test Examples**
- **Location:** Entire L2-L3
- **Problem:** Says "tests pass" but doesn't show what tests should do
- **Gap:** No `test_tone_selection()`, `test_letter_generation()` examples
- **Fix:** Add test examples:
  ```python
  def test_tone_selection_apologetic():
      metrics = {"avg_quality_score": 40, "security_high_count": 1}
      tone = select_tone([metrics])
      assert tone == "apologetic"
  
  def test_letter_omits_empty_secrets():
      metrics = {"security_findings": []}
      letter = generate_letter([metrics])
      assert "I have no secrets" in letter["markdown"]
  ```

**Issue #9: HTML Output Lacks Accessibility Guidance**
- **Location:** Lines 348-356 (L3.2 HTML Letter Generator)
- **Problem:** Says "projector-friendly" but no WCAG guidelines
- **Gap:** No color contrast specs, no font size minimums
- **Fix:** Add accessibility checklist:
  ```
  - [ ] Minimum font: 18px for readability from 10 feet
  - [ ] Color contrast: 7:1 for tone colors (WCAG AAA)
  - [ ] No information conveyed by color alone (tone + text)
  - [ ] Semantic HTML (no divs as buttons)
  - [ ] Tested on 1920x1080 projector mockup
  ```

**Issue #10: No Rollback Plan**
- **Location:** Entire plan
- **Gap:** What if letter tone is wrong? How do we fix it?
  - Regenerate entire letter?
  - Just update tone section?
- **Fix:** Add to L4 Demo section:
  ```
  Rollback Strategy:
  - [x] If tone is wrong, update tone selection logic in inheritance.py
  - [x] Regenerate letter with --inheritance-letter flag
  - [x] No need to delete old letter; new one overwrites
  - [x] Git tracks both versions in history
  ```

**Issue #11: Missing Performance Targets**
- **Location:** All phases
- **Gap:** How long should letter generation take?
  - < 100ms? < 500ms? < 1s?
- **Fix:** Add performance targets:
  ```
  Phase L2 Performance Targets:
  - generate_letter() < 50ms
  - render_letter_markdown() < 10ms
  - render_letter_html() < 100ms
  - Combined: < 200ms for typical repo
  ```

### 🔵 MINOR ISSUES

1. **Line 9:** "PDLC" acronym not defined (assume PDLC = Plan → Design → Implement → Verify?)
2. **Line 83:** "Yours [apologies / cautiously / confidently]," — inconsistent pluralization
3. **Line 337:** Missing comma in "Markdown + HTML" (should be "Markdown + HTML generation")
4. **Lines 462-468:** Session management refers to `—inheritance-letter` (em-dash) instead of `--inheritance-letter`

---

# SECTION 3: ONBOARDING PROFILE V2

## Plan File: `plan-onboarding-profile-v2.md`

### ✅ STRENGTHS

1. **Clear Vision** — Professional assessment vs playful archetypes is well-motivated
2. **Good Design Decisions** — Explains why dimension mapping makes sense
3. **Realistic Scope** — 3 hours for 4 phases is achievable

### 🔴 CRITICAL ISSUES

**Issue #1: Dimension Mapping Completely Missing**
- **Location:** Lines 18-35 (Vision section)
- **Problem:** Plan says "Map archetype names → professional dimension names" but NEVER LISTS THE MAPPING
- **Impact:** Impossible to implement without knowing what the 6 dimensions should be
- **Fix:** Add explicit mapping table:
  ```markdown
  ## Archetype → Professional Dimension Mapping
  
  | Archetype | Professional Dimension | Score Interpretation |
  |-----------|----------------------|----------------------|
  | 🤔 Anxious Overthinker | Code Complexity | Low (simple) to High (tangled) |
  | 🚀 Reckless Optimist | Security Maturity | Low (risky) to High (hardened) |
  | 📋 Copy-Paste Artist | Code Duplication | Low (unique) to High (repetitive) |
  | 🔀 Chaotic Connector | Architecture Clarity | Low (coupled) to High (modular) |
  | ✅ Cautious Perfectionist | Code Quality | Low (issues) to High (polished) |
  | 🤐 Quiet Newcomer | Test Coverage | Low (untested) to High (covered) |
  
  **Professional Narrative:**
  Use neutral language: "Code Complexity: 75/100 (complex, refactor opportunities exist)"
  Instead of: "🤔 Anxious Overthinker (high anxiety)"
  ```

**Issue #2: V1-V4 Phase Descriptions Are Vague**
- **Location:** Lines 88-151 (V1-V4 phases)
- **Problem:** Each phase has time estimate but NO deliverables
  - V1: "30 min" — for what? RESEARCH.md section? Dimension mapping? Both?
  - V2: "75 min" — create `onboarding.py` and tests, but what's the API?
- **Impact:** Impossible to start implementation without guessing
- **Fix:** Add explicit deliverables for each phase:
  ```
  V1 Design (30 min):
  Deliverables:
  - [ ] RESEARCH.md: Onboarding Profile section with dimension mapping
  - [ ] Dimension definitions (6 professional names, scoring rules)
  - [ ] Sample output for examples/ directory
  - [ ] First week checklist template
  
  V2 Core (75 min):
  Deliverables:
  - [ ] onboarding.py with:
    - generate_profile(metrics_list) → dict
    - select_dimensions(metrics_list) → dict[dimension_name -> score]
    - build_first_week_checklist(metrics_list, tone) → list[str]
  - [ ] --onboarding-profile flag in scanner.py
  - [ ] Markdown report generation
  - [ ] Tests: test_onboarding.py (8+ tests)
  ```

**Issue #3: First Week Actions Undefined**
- **Location:** Lines 36-41 (Vision section)
- **Problem:** Example shows:
  ```
  First week:
  1. Enable pre-commit gate (blocks secrets)
  2. Read CLAUDE.md for ground rules
  3. Review security findings
  ```
  But plan never defines what "first week actions" should be or how many
- **Impact:** Can't build the feature without knowing expected output
- **Fix:** Add explicit rules:
  ```
  First Week Checklist (auto-generated from metrics):
  
  Always include (top 3):
  1. Enable pre-commit security gate (copy command from output)
  2. Read CLAUDE.md for [team's] ground rules
  3. Run scanner: python -m scanner . --security (see current state)
  
  Conditional (based on metrics):
  If security issues exist:
    - Review and fix: [hardcoded secrets, SQL injection, unsafe patterns]
  If complexity high:
    - Refactor top 3 functions; target complexity < 10
  If documentation low:
    - Add docstrings to [N] functions (currently X% covered)
  If tests missing:
    - Write tests for [untested_hotspots]; current coverage X%
  ```

**Issue #4: Missing Onboarding Brief Structure**
- **Location:** Entire plan
- **Problem:** Never defines the actual HTML/Markdown structure of the onboarding profile
- **Gap:** What does the output look like?
- **Fix:** Add sample output section:
  ```markdown
  ## Sample Onboarding Profile Output
  
  ---
  # Welcome to [Repo Name]
  
  ## Codebase Assessment
  
  **Overall Grade:** B+ (Quality: 78/100)
  
  ### Dimensions
  - **Code Complexity:** 62/100 (Moderate — some refactoring needed)
  - **Security Maturity:** 85/100 (Good — few hardcoded secrets)
  - **Code Duplication:** 30/100 (Excellent — very unique)
  - **Architecture Clarity:** 72/100 (Good — mostly modular)
  - **Code Quality:** 78/100 (Good — readable, maintainable)
  - **Test Coverage:** 65/100 (Moderate — gaps in error handling)
  
  ### Your First Week
  
  - [ ] Enable pre-commit hook: `./scripts/install-hooks.sh`
  - [ ] Read `CLAUDE.md` (project ground rules — 10 min)
  - [ ] Review security findings in `output/report.json` (there are 2 issues)
  - [ ] Refactor `realistic_app.py:authenticate_user` (complexity 8 → 5)
  - [ ] Add docstrings to 5 undocumented functions
  
  ### Entry Points
  
  **Start here (simple, safe):**
  - `logging.py` (complexity 2, clean)
  - `utils.py` (complexity 3, well-documented)
  
  **Avoid first (complex):**
  - `realistic_app.py` (complexity 8)
  - `engine.py` (complexity 6)
  
  ### Inherited Debt
  
  - 2 hardcoded secrets (line 6, 12 in insecure.py)
  - 3 overly complex functions
  - 40% undocumented code
  
  **Next steps:** Address security debt first, then refactor complexity.
  ---
  ```

**Issue #5: Missing Professional Tone Specifications**
- **Location:** Lines 139-141 (V3 Polish)
- **Problem:** Says "Tone customization (Neutral/Brief/Detailed)" but never defines what each means
- **Gap:** When should a user pick "Brief" vs "Detailed"? What changes between them?
- **Fix:** Add tone specifications:
  ```
  Tone Options (--onboarding-tone):
  
  neutral (default):
    - 3-5 page PDF
    - Dimensions + first week checklist + entry points
    - No examples, no verbose explanations
    - For: New hires getting oriented
  
  brief:
    - 1-2 page summary
    - Top 3 dimensions only
    - 3-5 first week actions (critical only)
    - For: Executive summary, quick handoff
  
  detailed:
    - 5-10 page deep dive
    - All 6 dimensions with examples
    - Full inherited debt analysis
    - Refactor recommendations with complexity deltas
    - For: Technical leaders, architecture review
  ```

**Issue #6: Test Coverage Undefined**
- **Location:** V2 phase
- **Problem:** Says "5+ unit tests" but doesn't specify what they should test
- **Fix:** Add test list:
  ```
  test_onboarding.py:
  - [ ] test_dimensions_calculated_for_clean_repo
  - [ ] test_dimensions_calculated_for_complex_repo
  - [ ] test_first_week_checklist_includes_security_if_issues
  - [ ] test_first_week_checklist_skips_refactor_if_clean
  - [ ] test_tone_selection_neutral_vs_brief_vs_detailed
  - [ ] test_markdown_output_readable
  - [ ] test_html_output_self_contained
  - [ ] test_onboarding_profile_backwards_compatible_with_personality
  ```

### 🟡 MEDIUM ISSUES

**Issue #7: Acceptance Criteria for V2 Too Broad**
- **Location:** Lines 153-165 (V2 Acceptance Criteria)
- **Problem:** Says "All tests pass" but no specific pass/fail criteria
- **Gap:** No metrics for what "hiring-ready" means
- **Fix:** Add concrete criteria:
  ```
  Acceptance Criteria for V2:
  - [ ] Dimensions map to all 6 archetype traits
  - [ ] First week checklist has ≥3 actions, ≤7 actions
  - [ ] Grade (A-F) clearly shown in output
  - [ ] Professional language only (no emoji, no playful tone)
  - [ ] output correctly maps to new hire skill level (entry/mid/senior)
  - [ ] Backwards compatible: old personality.py tests still pass
  ```

**Issue #8: V3 Polish Acceptance Criteria Missing**
- **Location:** Lines 155-165 (V3 subsection)
- **Problem:** Says "Dashboard update" but no clear acceptance criteria
- **Fix:** Add:
  ```
  V3 Polish Acceptance Criteria:
  - [ ] HTML outputs in < 100ms
  - [ ] Dimension chart renders correctly (bar chart or radar)
  - [ ] Color contrast ≥ 7:1 (WCAG AAA)
  - [ ] Responsive design (mobile to desktop)
  - [ ] Tone selector works in CLI and HTML
  ```

**Issue #9: V4 Demo Missing Specific Commands**
- **Location:** Lines 183-187 (V4 Demo & Docs)
- **Problem:** Says "Commands are copy-paste ready" but doesn't show them
- **Fix:** Add explicit commands:
  ```
  V4 Deliverables:
  - [ ] DEMO_ONBOARDING.md with exact commands:
    - Markdown: python -m scanner examples/ --onboarding-profile onboarding.md
    - HTML neutral: python -m scanner examples/ --onboarding-html onboard.html --tone neutral
    - HTML brief: python -m scanner examples/ --onboarding-html onboard.html --tone brief
  - [ ] DEMO_ONBOARDING.md shows expected output for examples/
  - [ ] Screenshots or mockups of HTML output
  ```

**Issue #10: No Migration Path from Personality to Onboarding**
- **Location:** Entire plan
- **Gap:** If user has existing personality profiles, how do they migrate to onboarding profiles?
- **Problem:** Two different output formats for same data
- **Fix:** Add migration section:
  ```
  Migration from Personality Profiler to Onboarding Profile:
  
  Both use same trait calculations but different output formats:
  - Personality: Memorable archetypes (hackathon demo)
  - Onboarding: Professional dimensions (hiring/onboarding)
  
  Strategy:
  - Both flags can coexist: --personality AND --onboarding-profile
  - Users choose which to use for different audiences
  - No breaking changes; old personality.py code unaffected
  - Shared metrics: use same trait calculation engine
  ```

**Issue #11: No Backwards Compatibility Plan**
- **Location:** V1-V4
- **Gap:** What if existing code depends on personality archetypes?
- **Fix:** Add note:
  ```
  Backwards Compatibility:
  - Old --personality flag still works (generates emoji archetypes)
  - New --onboarding-profile flag adds professional output
  - Both can run in same command: python -m scanner . --personality --onboarding-profile
  - No breaking changes to personality.py or scanner.py API
  ```

### 🔵 MINOR ISSUES

1. **Line 29:** "Cautious Perfectionist" image missing — show what professional name would be
2. **Line 36-41:** Sample output uses different format than described elsewhere
3. **Lines 153-165:** "V2" spelled as "✅ V2" but consistency in other sections
4. **Missing:** How to handle repos with no metrics (empty directory)?

---

# SECTION 4: PART II CREATIVE PATHS (A-F, G-L)

## Plan File: `plan-part-ii-creative-paths.md`

### ✅ STRENGTHS

1. **Comprehensive Overview** — All 12 paths described with pitch and demo hooks
2. **Realistic Estimates** — 2-4 hours per path is reasonable
3. **Shared Foundation Checklist** — Good reminder of what's needed before building
4. **Recommended Demo Pairs** — Smart guidance on which paths to combine
5. **Ground Rules** — Enforces evidence and no LLM calls

### 🔴 CRITICAL ISSUES

**Issue #1: PATH NAMING CONFLICT - Path G Defined Twice**
- **Location 1:** plan-part-ii-creative-paths.md, lines 414-468 = "Path G: MCP Integration"
- **Location 2:** plan-creative-suite-ghi.md, lines 1-244 = "Path G: Personality Profiler"
- **Impact:** Catastrophic confusion when reading Part II; unclear which G to implement
- **Fix:** IMMEDIATELY clarify:
  ```
  OPTION A (RECOMMENDED): Rename Part II's MCP to Path M
  - Keep "Creative Suite G/H/I" for Personality/Inheritance/CAQI
  - Rename MCP Integration to Path M (to maintain Part I/II separation)
  
  OPTION B: Separate "Creative Suite G/H/I" from "Part II Paths"
  - Explicitly state: "Creative Suite is standalone; Part II paths are separate"
  - Add note: "Path G in Creative Suite ≠ Path G in Part II"
  
  Chosen Solution: OPTION A (rename MCP to Path M)
  This prevents future confusion and keeps naming clean.
  ```

**Issue #2: Duplicate Content in File**
- **Location:** Lines 1-688 then AGAIN lines 689-1370 (entire file duplicated!)
- **Impact:** Confusing; makes file twice as long as needed
- **Fix:** Delete lines 689-1370 (the duplicate section)

**Issue #3: Missing Implementation Plans for Paths A, B, C**
- **Location:** Lines 117-303 (Paths A, B, C sections)
- **Problem:** Only high-level sketches, not detailed phase plans like Path H/I
- **Impact:** Can't start implementation without more detail
- **Gap:**
  - Path A: No example refactor (which function to target?)
  - Path B: Query templates incomplete (how many queries supported?)
  - Path C: Risk formula weights not justified (why 40% complexity, 30% churn?)
- **Fix:** Create separate detailed plans:
  ```
  Create:
  - plan-refactoring-assistant-path-a.md (detailed phases A1-A4)
  - plan-code-explorer-path-b.md (detailed phases B1-B4)
  - plan-debt-radar-path-c.md (detailed phases C1-C4)
  
  Same rigor as plan-inheritance-letter.md (15-20K words each)
  ```

**Issue #4: Path D (Skill Creator) References Non-Existent Code**
- **Location:** Lines 992-1043 (Path D)
- **Problem:** Says "Author skill at `~cursor/skills/scanner-gate/SKILL.md`"
  - This path doesn't exist in the repo
  - Plan doesn't say HOW to create it
- **Fix:** Add step-by-step:
  ```
  D2 - Author Skill (60 min):
  
  Step 1: Create directory structure:
    mkdir -p ~/.claude/skills/code-scanner-gate/
  
  Step 2: Create SKILL.md with sections:
    - When to use (trigger phrases)
    - Ground rules from CLAUDE.md (top 4)
    - Anti-patterns ("don't scan without --security")
    - Verification checklist
    - Examples (show agent calls)
  
  Step 3: Reference template:
    Use ~/.claude/skills/graphify/SKILL.md as template
  ```

**Issue #5: Path F (Multi-Agent) Worktree Path Is Wrong**
- **Location:** Lines 1073-1077
- **Problem:** Says `git worktree add ../hackathon-agent1 -b feat/debt-radar`
  - This creates worktree at `../hackathon-agent1` (parent directory)
  - Probably should be within project or clearly specified
- **Fix:** Clarify:
  ```
  Worktree Setup:
  
  Option 1 (Recommended): Within project .git/
    git worktree add worktrees/agent1 -b feat/debt-radar
    git worktree add worktrees/agent2 -b feat/explorer
    git worktree add worktrees/agent3 -b feat/debt-tests
  
  Option 2: Outside project
    git worktree add ../codepulse-agent1 -b feat/debt-radar
    # But this breaks relative imports; not recommended
  ```

**Issue #6: Missing Shared Foundation Details**
- **Location:** Lines 733-766 (Shared Foundation section)
- **Problem:** Mentions `scan_context.py` but:
  - No actual function signatures
  - No example of how to use it
  - No clear acceptance criteria
- **Fix:** Add explicit API:
  ```python
  # scan_context.py (shared module, created after Path I/G/H work)
  
  def aggregate_repo_metrics(metrics_list: list[dict]) -> dict:
      """Combine all per-file metrics into repo-level totals.
      
      Args:
          metrics_list: List of file-level scan results
      
      Returns:
          {
              "total_files": int,
              "avg_complexity": float,
              "complexity_hotspots": list[dict],  # Top 5 complex functions
              "security_counts": {
                  "high": int,
                  "medium": int,
                  "low": int,
              },
              "avg_quality_score": float,
              "doc_coverage_ratio": float,
              "circular_dependencies": list[str],
              ...
          }
      """
  ```

### 🟡 MEDIUM ISSUES

**Issue #7: Paths J, K, L Are Too Brief**
- **Location:** Lines 1158-1301
- **Problem:** Only 4-5 phases each, very sparse detail
- **Gap:**
  - Path J: No test skeleton examples
  - Path K: No Mermaid diagram examples
  - Path L: No CI config parser details
- **Fix:** Expand each to 8-10K word plans (same detail as Path H)

**Issue #8: Recommended Demo Pairs Unclear**
- **Location:** Lines 1313-1320 (Recommended demo pairs)
- **Problem:** Says "A + re-scan" and "C + Risk" but:
  - Unclear how they chain together
  - No demo script provided
- **Fix:** Add section with full demo workflows:
  ```
  Demo Pair 1: Path A (Refactoring) + Re-scan
  1. Run initial scan: python -m scanner examples/ --output before.json
  2. View refactoring candidates: python -m scanner examples/ --refactor-candidates
  3. Show Agent refactoring authenticate_user (optional live)
  4. Run second scan: python -m scanner examples/ --output after.json
  5. Show deltas: python -m scanner compare-scans before.json after.json
  
  Demo Pair 2: Path C (Debt Radar) + CAQI
  1. Enable git: cd examples/ && git init && git add -A && git commit -m "initial"
  2. Simulate churn: Edit files multiple times, commit
  3. Run debt radar: python -m scanner examples/ --debt-radar
  4. Show risk score from CAQI
  5. Overlay: "High complexity + high churn = highest risk"
  ```

**Issue #9: Unclear Implementation Order for Part II**
- **Location:** Lines 1324-1340
- **Problem:** Says "Pick 1-2 paths" but doesn't say IF Part II should even be done
  - Should user do I/G/H (Creative Suite) BEFORE Part II?
  - Or in parallel?
  - Or skip Part II entirely?
- **Fix:** Add decision framework:
  ```
  Decision Tree: Which Creative Paths to Build?
  
  Priority 1 - Essential (build these first):
  ✅ Path I (CAQI) - foundation for demo
  ✅ Path G (Personality) - most memorable
  ✅ Path H (Inheritance Letter) - best story
  
  Priority 2 - Strong Demo Add-ons (pick 1-2):
  🟡 Path A (Refactor Assistant) - shows metric improvement
  🟡 Path C (Debt Radar) - shows git risk  
  
  Priority 3 - Enhancement (only if time allows):
  🔵 Path D (Skill Creator) - meta-artifact
  🔵 Path F (Multi-Agent) - process demo
  🔵 Paths B, J, K, L - specialized use cases
  
  Recommendation: Do I/G/H first (3-4 hours), then pick 1-2 from Priority 2.
  ```

**Issue #10: Non-Goals Not Clear**
- **Location:** Lines 1306-1309
- **Problem:** Says "Not building scanner features" but unclear what counts
- **Fix:** Add examples:
  ```
  Non-Goals for Part II:
  - [ ] NOT adding new detection rules (that's scanner work)
  - [ ] NOT changing existing metrics (use what I/G/H define)
  - [ ] NOT building new analyzers (plugin that in Part III)
  - [ ] NOT modifying scanner.py core (wrap it instead)
  
  IS building (repackaging + visualization + orchestration):
  - [ ] Refactoring recommendations (ranking existing metrics)
  - [ ] Risk scoring (combining metrics with git data)
  - [ ] HTML dashboards (visualizing scan results)
  - [ ] CLI helpers (--ask, --refactor-candidates, --debt-radar)
  ```

### 🔵 MINOR ISSUES

1. **Typo (line 649):** "fastest packag" should be "fastest packaging"
2. **Lines 722-728:** Path index shows duplication (repeated)
3. **Line 804-814:** Path A header duplicated (lines 210-220 also)
4. **Missing:** No error handling guidance for when git commands fail (Path C/L)
5. **Line 1324-1340:** Session management prompt is incomplete

---

# SECTION 5: CROSS-PLAN ISSUES

### Issue 1: CRITICAL - Inconsistent CLI Flag Format Across All Plans

**Location:** All plans use mix of `--flag` and `—flag` (em-dashes)

**Affected Plans:**
- plan-creative-suite-ghi.md (lines 32-44)
- plan-inheritance-letter.md (lines 462-468)
- plan-personality-profiler.md (multiple)
- plan-onboarding-profile-v2.md (multiple)

**Fix:** Global search-and-replace:
```
Replace: —
With: --
(All flags must use double-hyphen, not em-dash)
```

### Issue 2: Inconsistent Phase Naming Convention

**Location:** Different plans use different naming:
- Creative Suite GHI: P1-P4 (personality), L1-L4 (letter), Q1-Q4 (CAQI)
- Onboarding: V1-V4
- Part II: A1-A4, B1-B4, etc.

**Problem:** Confusing when jumping between plans

**Recommendation:** Keep as-is (it's clear which plan each refers to), but add note in each plan:
```
Note: Phase naming varies by path:
- Personality: P1-P4
- Inheritance Letter: L1-L4
- CAQI: Q1-Q4
- Onboarding: V1-V4
This is intentional to avoid conflicts within each module.
```

### Issue 3: Missing Edge Case Documentation

**Location:** All plans assume "happy path" (data exists, metrics are valid)

**Missing:** What happens with:
- Empty codebase (0 files)
- Tiny codebase (1-2 files)
- All metrics disabled (--security, --quality-score, etc. not passed)
- Missing RESEARCH.md sections
- Files that can't be parsed

**Fix:** Add "Edge Cases" section to each plan:
```markdown
## Edge Cases & Error Handling

### Empty Codebase
- Input: directory with 0 Python files
- Expected: All modules should handle gracefully
- Personality: Default to "Quiet Newcomer" (fallback)
- Inheritance Letter: "No code found; starting from scratch"
- CAQI: Score = 0 (no pollution)

### Tiny Codebase (1-2 files)
- Input: directory with < 5 functions total
- Expected: Metrics still valid, just smaller scope
- Personality: May default to "Quiet Newcomer"
- Tips should reference actual files, not generic advice

### Missing Metrics
- Input: scanner run without --security, --quality-score flags
- Expected: Modules should use defaults or skip sections
- Error: Should NOT crash; should show "metric unavailable"
```

### Issue 4: Missing Test Strategy for All Plans

**Location:** All plans mention "tests pass" but don't specify:
- How many tests per module?
- What coverage % is required?
- Should integration tests run all 3 paths together?
- Test fixtures: real code or mocks?

**Recommendation:** Add to every plan:
```markdown
## Testing Strategy (for all phases)

Unit Tests:
- [ ] 10-15 unit tests per module
- [ ] Mock fixtures for edge cases
- [ ] 90%+ code coverage for core functions

Integration Tests:
- [ ] Run scanner on real examples/ directory
- [ ] Verify HTML output is valid
- [ ] Test all CLI flags together

Performance Tests:
- [ ] Metrics < 500ms per file
- [ ] HTML generation < 100ms
- [ ] Full demo < 5 seconds

Manual Tests:
- [ ] Open HTML in browser, verify styling
- [ ] Test on 1920x1080 projector mockup
- [ ] Re-run demo with different --tone options
```

### Issue 5: Backwards Compatibility Not Addressed

**Location:** All new features add to JSON output, but what about old tools parsing it?

**Problem:** If output.json gains new fields, old parsing code might break

**Fix:** Add to all plans:
```markdown
## Backwards Compatibility

JSON Output Format:
- Version: 2.0 (add to root of JSON)
- New sections are OPTIONAL (nested under top-level keys)
- Old parsers should use: json.get("personality", {})
- Document in RESEARCH.md: JSON Schema v2.0

Example:
{
  "version": "2.0",
  "scan_results": [...],
  "personality": { ... },              # Optional
  "inheritance_letter": { ... },       # Optional
  "caqi": { ... },                     # Optional
  "onboarding_profile": { ... }        # Optional
}

Old code can safely ignore new fields.
```

---

# FINAL RECOMMENDATIONS

## Priority 1: CRITICAL FIXES (Must Fix Before Starting Any Implementation)

- [ ] **Fix Path G naming conflict** — Rename Part II's MCP to Path M
- [ ] **Remove duplicate content** — Delete lines 689-1370 in plan-part-ii-creative-paths.md
- [ ] **Fix all em-dashes** — Replace `—` with `--` in ALL plans globally
- [ ] **Add dimension mapping to Onboarding v2** — Explicit 6-dimension table required
- [ ] **Clarify Inheritance Letter edge cases** — Define fallback behavior for empty sections
- [ ] **Fix Phase L2 duplication** — Remove duplicate section from inheritance-letter.md

## Priority 2: MEDIUM FIXES (Should Fix Before Implementation)

- [ ] **Add detailed test plans** to all plans (10-15 tests per module)
- [ ] **Add performance targets** (execution time limits)
- [ ] **Add edge case handling** to all plans
- [ ] **Create detailed Path A/B/C plans** (currently too brief)
- [ ] **Add acceptance criteria** to all phases
- [ ] **Document JSON Schema v2.0** for backwards compatibility

## Priority 3: NICE-TO-HAVE (Can Address During Implementation)

- [ ] Add WCAG accessibility guidelines to HTML outputs
- [ ] Add rollback/recovery procedures
- [ ] Create demo script templates for each path
- [ ] Add performance benchmarks (complexity = 1.5 clarification)
- [ ] Document shared metrics contract

## Recommended Implementation Sequence

**Phase 0: Fix All Plans (1-2 hours)**
1. Apply all Priority 1 & 2 fixes
2. Create comprehensive PLAN_AUDIT_CHECKLIST.md (tracked during build)

**Phase 1: Creative Suite GHI (5-6 hours)**
- Build in order: I (CAQI) → G (Personality) → H (Inheritance Letter)
- Each is independently testable
- Combined demo at end

**Phase 2: Onboarding Profile v2 (3-4 hours)**
- Depends on completed Creative Suite (reuses trait calculations)
- Professional dimension mapping
- First week checklist generation

**Phase 3: Select from Part II (2-4 hours)**
- If time allows, pick Path A (Refactoring) or Path C (Debt Radar)
- Skip Paths B, J, K, L unless specifically requested

---

# CHECKLIST: Before Implementation Starts

Use this to verify all fixes are applied:

- [ ] plan-creative-suite-ghi.md
  - [ ] Lines 32-44: All `—` replaced with `--`
  - [ ] Issue #3: Edge case handling section added
  - [ ] Issue #5: MVP sign-off criteria made concrete
  - [ ] Issue #6: Integration testing phase (Phase 0) added

- [ ] plan-inheritance-letter.md
  - [ ] Lines 178-299: Duplicate Phase L2 removed
  - [ ] Issue #2: start_here selection logic clarified (complexity thresholds)
  - [ ] Issue #3: avoid section fallback rules added
  - [ ] Issue #4: Secrets section empty case documented
  - [ ] Issue #6: First week tips templates added
  - [ ] Issue #7: Fixture schemas provided
  - [ ] Issue #8: Test examples added
  - [ ] Lines 462-468: All `—` replaced with `--`

- [ ] plan-onboarding-profile-v2.md
  - [ ] Issue #1: Dimension mapping table added (CRITICAL)
  - [ ] Issue #2: V1-V4 deliverables defined
  - [ ] Issue #3: First week actions explicitly listed
  - [ ] Issue #4: Sample onboarding profile output added
  - [ ] Issue #5: Tone specifications (neutral/brief/detailed) defined
  - [ ] Issue #6: Test list added

- [ ] plan-part-ii-creative-paths.md
  - [ ] Issue #1: Path G renamed to Path M (MCP Integration)
  - [ ] Issue #2: Lines 689-1370 (duplicate content) deleted
  - [ ] Issue #3: Create separate detailed plans for Paths A, B, C
  - [ ] Issue #5: Worktree path clarified
  - [ ] All `—` replaced with `--`

- [ ] All Plans
  - [ ] Edge case section added to each
  - [ ] Test strategy documented
  - [ ] JSON Schema v2.0 backwards compatibility added
  - [ ] Performance targets specified
  - [ ] Acceptance criteria concrete (not "tests pass")

---

**Report Created:** 2026-06-06  
**Status:** Ready for implementation after fixes applied  
**Next Step:** Apply fixes, then begin Phase 1 (Creative Suite GHI)
