---
created_at: 2026-06-12T18:16:43Z
title: Plan Fixes Checklist
source: claude-code
project: codescanner
---

# Plan Fixes Checklist — Implementation Ready
**Status:** Track progress as you apply fixes from PLAN_AUDIT_REPORT.md  
**Target:** All critical + medium fixes applied before Phase 1 starts

---

## CRITICAL FIXES (Apply First)

### 1. Fix Path G Naming Conflict ⚠️ BLOCKING

**What:** Path G is defined in TWO places with DIFFERENT meanings  
**Files Affected:**
- `plan-creative-suite-ghi.md` → Path G = Personality Profiler
- `plan-part-ii-creative-paths.md` (lines 414-468) → Path G = MCP Integration

**Action:** In `plan-part-ii-creative-paths.md`
- [ ] Find: "## Path G: MCP Integration" (line 414)
- [ ] Replace with: "## Path M: MCP Integration" (rename section header)
- [ ] Update ALL references in Path M section from `Path G` to `Path M`
- [ ] Update path index table (line 29) to show "M" instead of "G"
- [ ] Update recommended demo pairs (line 723+) if mentions Path G MCP

**Verify:** Run `grep -n "Path G" plan-part-ii-creative-paths.md` should show 0 results

---

### 2. Remove Duplicate Content ⚠️ BLOCKING

**What:** plan-part-ii-creative-paths.md contains entire file duplicated (lines 689-1370)  
**Files Affected:** `plan-part-ii-creative-paths.md`

**Action:**
- [ ] Open file in editor
- [ ] Delete lines 689-1370 (second copy of entire plan)
- [ ] Save file
- [ ] Verify line count goes from ~1370 to ~688 lines

**Verify:** File should be ~40K, not ~80K

---

### 3. Fix All Em-Dashes to Double-Hyphens 🔴 BLOCKING

**What:** All CLI flags use em-dashes (—) instead of double-hyphens (--)  
**Problem:** Em-dashes won't work in command-line parsing; commands will fail

**Files Affected:**
- `plan-creative-suite-ghi.md` (lines 32-44)
- `plan-inheritance-letter.md` (lines 462-468)
- `plan-personality-profiler.md` (multiple lines)
- `plan-onboarding-profile-v2.md` (multiple)
- `plan-part-ii-creative-paths.md` (multiple)

**Action:** Global replace in each file
```bash
# For each file:
sed -i 's/—/--/g' filename.md
```

**Verify:** `grep "—" *.md` should return 0 results

Files to check:
- [ ] plan-creative-suite-ghi.md
- [ ] plan-inheritance-letter.md
- [ ] plan-personality-profiler.md
- [ ] plan-onboarding-profile-v2.md
- [ ] plan-part-ii-creative-paths.md

---

### 4. Remove Duplicate Phase L2 in Inheritance Letter

**What:** Phase L2 appears twice in `plan-inheritance-letter.md`  
**Location:** Lines 178-240 (first copy) and 242-299 (second copy, nearly identical)

**Action:**
- [ ] Open `plan-inheritance-letter.md`
- [ ] Delete lines 242-299 (the second/duplicate Phase L2)
- [ ] Verify Phase L3 now immediately follows Phase L2
- [ ] Save file

**Verify:** Search for "## Phase L2" should appear exactly once

---

### 5. Add Dimension Mapping to Onboarding v2 🔴 BLOCKING

**What:** Plan says "map archetypes to professional names" but NEVER LISTS THE MAPPING  
**Files Affected:** `plan-onboarding-profile-v2.md`

**Action:** Add this section after "Design Decisions" (after line 45):

```markdown
## Archetype → Professional Dimension Mapping

| Archetype | Professional Dimension | Score Interpretation |
|-----------|----------------------|----------------------|
| 🤔 Anxious Overthinker | Code Complexity | Low (simple) → High (tangled) |
| 🚀 Reckless Optimist | Security Maturity | Low (risky) → High (hardened) |
| 📋 Copy-Paste Artist | Code Duplication | Low (unique) → High (repetitive) |
| 🔀 Chaotic Connector | Architecture Clarity | Low (coupled) → High (modular) |
| ✅ Cautious Perfectionist | Code Quality | Low (issues) → High (polished) |
| 🤐 Quiet Newcomer | Test Coverage | Low (untested) → High (covered) |

**Output Format Change:**
- Old (Personality): "Meet the Reckless Optimist — ships fast, secrets faster"
- New (Onboarding): "Security Maturity: 40/100 (risky, needs hardening)"

**Professional Language Only:**
- No emoji (except in internal tables)
- No personality tone (neutral assessment language)
- No archetypes (use dimension names instead)
```

- [ ] Section added after "Design Decisions"
- [ ] Table contains all 6 dimensions with clear interpretations
- [ ] Verify against plan-personality-profiler.md that all 6 archetypes are mapped

---

### 6. Clarify start_here Selection Logic in Inheritance Letter

**What:** Plan says "1-2 files: complexity = 1.5" which is impossible (complexity must be integer)  
**Files Affected:** `plan-inheritance-letter.md` (line 210)

**Action:** Replace line 210 with:

```markdown
| `'start_here'` | 1-2 files where: cyclomatic complexity ≤ 3, no security findings, has error handling, quality > 70 | If no clean files exist, flag it: "No safe entry points; start with [file] anyway" |
```

- [ ] Line 210 updated with clear thresholds (complexity ≤ 3 instead of = 1.5)
- [ ] Fallback rule added (what if no clean files exist)
- [ ] Verify thresholds are achievable with examples/ directory

---

## MEDIUM FIXES (Apply Next)

### 7. Add Edge Case Handling to Inheritance Letter

**What:** Plan doesn't handle when sections are empty (no secrets, no avoid, no start_here)  
**Files Affected:** `plan-inheritance-letter.md`

**Action:** Add section after Letter Structure (after line 83):

```markdown
## Handling Empty Sections (Graceful Degradation)

**Secrets Section:**
- If no security findings: Say "I have no secrets I'm aware of" (tone-appropriate)
- If only low-severity: Skip section entirely

**Avoid Section:**
- If all functions are simple: Say "I have no dangerous functions found"
- If only 1-2 functions: Show those instead of "top 3"

**Start Here Section:**
- If no clean entry points: Flag it and recommend "start with [lowest-complexity file]"
- If all files are complex: Show complexity ranges so developer knows what to expect

**First Week Tips:**
- If codebase is already clean: Show "maintenance tips" instead of "fix tips"
- If only 1 issue type: Focus all 3 tips on that (don't force unrelated advice)
```

- [ ] Section added after Letter Structure
- [ ] Cover: secrets, avoid, start_here, tips sections
- [ ] For each: define empty case + fallback behavior

---

### 8. Add First Week Tips Templates to Inheritance Letter

**What:** Plan references templates that don't exist  
**Location:** plan-inheritance-letter.md (line 211)

**Action:** Add section after Tone Catalog (after line 99):

```markdown
## First Week Tips Templates (Tone-Based)

### Apologetic Tone Tips (high security or low quality)
1. "Run pre-commit hooks locally: `./scripts/install-hooks.sh` (blocks secrets)"
2. "Review and fix all hardcoded secrets: [list of files with line numbers]"
3. "Schedule security audit with team; expect 2-3 hours initial review"

### Cautious Tone Tips (moderate quality, some smells)
1. "Read CLAUDE.md for project ground rules; most questions answered there"
2. "Refactor [function name] in [file] to reduce complexity from X to <10"
3. "Add docstrings to undocumented functions; current coverage: X%"

### Confident Tone Tips (high quality, clean)
1. "Set up IDE pre-commit hook to run gate automatically: [command]"
2. "Review [file] for architecture patterns; consider it a reference model"
3. "Contribute by: choosing untested function, writing tests, submitting PR"
```

- [ ] Templates added after Tone Catalog section
- [ ] Each tone has 3 template tips
- [ ] Templates use placeholder syntax: [function name], [file], X%, etc.

---

### 9. Add Detailed Phase Deliverables to Onboarding v2

**What:** Phases V1-V4 have time estimates but no explicit deliverables  
**Files Affected:** `plan-onboarding-profile-v2.md`

**Action:** Replace the brief phase descriptions with detailed ones:

**V1 Design (30 min):**
```markdown
Deliverables:
- [ ] RESEARCH.md section: "Onboarding Profile v2"
  - [ ] 6 professional dimensions with definitions
  - [ ] Sample output for examples/ directory
  - [ ] Scoring rules (0-100 for each dimension)
  - [ ] Acceptance criteria for "hiring-ready" output
```

**V2 Core (75 min):**
```markdown
Deliverables:
- [ ] onboarding.py module with functions:
  - [ ] generate_profile(metrics_list) → dict
  - [ ] select_dimensions(metrics_list) → dict[name -> score]
  - [ ] build_first_week_checklist(metrics, tone) → list[str]
  - [ ] generate_grade(metrics) → letter (A-F)
- [ ] Integration with scanner.py:
  - [ ] --onboarding-profile flag
  - [ ] --onboarding-tone option (neutral/brief/detailed)
- [ ] test_onboarding.py (8+ tests)
```

**V3 Polish (45 min):**
```markdown
Deliverables:
- [ ] HTML output with dimension chart
- [ ] Tone customization working in HTML
- [ ] Dashboard update with onboarding section
- [ ] Performance targets met (< 100ms generation)
```

**V4 Demo (30 min):**
```markdown
Deliverables:
- [ ] DEMO_ONBOARDING.md with exact copy-paste commands
- [ ] Sample outputs shown in README
- [ ] Dashboard links to onboarding HTML
```

- [ ] V1-V4 sections completely rewritten with explicit deliverables
- [ ] Each section includes acceptance criteria
- [ ] Cross-reference to test expectations

---

### 10. Add Test Strategy to All Plans

**What:** All plans mention "tests pass" but don't specify what tests  
**Files Affected:** All .md files in plan/

**Action:** Add section "Testing Strategy" to each plan (before MVP Sign-Off):

**For Inheritance Letter (add after Line 362):**
```markdown
## Testing Strategy

**Unit Tests (test_inheritance.py):**
- [ ] test_tone_selection_apologetic (security issues → apologetic)
- [ ] test_tone_selection_cautious (moderate quality → cautious)
- [ ] test_tone_selection_confident (clean code → confident)
- [ ] test_letter_omits_empty_secrets (no security → skip confessions)
- [ ] test_letter_omits_empty_avoid (all simple → skip avoid section)
- [ ] test_first_week_checklist_has_security_tips_if_issues
- [ ] test_markdown_output_valid
- [ ] test_html_output_self_contained

**Integration Tests:**
- [ ] Run on real examples/ directory
- [ ] Verify HTML opens in browser without errors
- [ ] Test all tones (apologies, cautious, confident)

**Performance Tests:**
- [ ] generate_letter() < 50ms
- [ ] render_letter_html() < 100ms
- [ ] Total < 200ms for repo with 100+ files

**Manual Tests:**
- [ ] Open HTML on 1920x1080 projector
- [ ] Read letter aloud; verify tone matches
- [ ] Before/after (add secrets) — verify tone shifts
```

Repeat similar structure for:
- [ ] plan-creative-suite-ghi.md
- [ ] plan-onboarding-profile-v2.md
- [ ] plan-personality-profiler.md
- [ ] plan-code-air-quality.md

---

### 11. Add Edge Case Section to All Plans

**What:** No plan handles empty/minimal codebases  
**Action:** Add section "Edge Cases & Fallbacks" to each plan:

```markdown
## Edge Cases & Fallbacks

**Empty Codebase (0 files):**
- Personality: Default to "Quiet Newcomer"
- Inheritance Letter: Say "No code to review"
- CAQI: Score = 0
- Onboarding: Grade = N/A

**Tiny Codebase (1-2 functions):**
- All metrics valid but may have unusual distributions
- Personality: May still trigger fallback
- Tips should reference actual files (not generic)

**All Metrics Disabled (no --security, --quality-score, etc.):**
- Modules should use sensible defaults or skip sections
- Don't crash; show "metric unavailable"

**Missing RESEARCH.md Sections:**
- Continue with defaults; don't block
```

- [ ] Added to plan-creative-suite-ghi.md
- [ ] Added to plan-inheritance-letter.md
- [ ] Added to plan-onboarding-profile-v2.md
- [ ] Added to plan-personality-profiler.md

---

### 12. Fix Phase A/B/C Descriptions (Part II)

**What:** Paths A, B, C only have sketches, not detailed plans  
**Files Affected:** `plan-part-ii-creative-paths.md`

**Action:** For each path, expand from ~2-3 pages to ~5-8 pages:

**Path A: Refactoring Assistant (expand lines 117-186)**
- Add acceptance criteria (complexity must drop ≥30% after refactor)
- Add example refactor walkthrough
- Add validation rules (refactored code must pass linter, tests)

**Path B: Code Explorer (expand lines 189-244)**
- Add 10 supported query templates (most_complex_files, security_findings, etc.)
- Add HTML mockup for explorer dashboard
- Add sample outputs

**Path C: Debt Radar (expand lines 247-303)**
- Justify weights (why 40% complexity, 30% churn, 20% security, 10% docs?)
- Add example risk score calculation
- Show git churn simulation for demo

- [ ] Path A expanded with examples and acceptance criteria
- [ ] Path B expanded with query templates and HTML mockup
- [ ] Path C expanded with weight justification and examples
- [ ] Each now ~5-8K words (consistent with Path H/I)

---

## NICE-TO-HAVE FIXES (If Time Allows)

- [ ] Add WCAG accessibility specs (font size, color contrast, semantic HTML)
- [ ] Add rollback/recovery procedures for each path
- [ ] Add demo script templates for each path
- [ ] Document shared metrics contract (scan_context.py API)
- [ ] Add performance benchmarks and thresholds
- [ ] Add JSON Schema v2.0 backwards compatibility guidance

---

## Progress Tracking

### Critical Fixes
- [ ] Path G renamed to Path M
- [ ] Duplicate content removed (lines 689-1370)
- [ ] All em-dashes fixed to double-hyphens
- [ ] Duplicate Phase L2 removed
- [ ] Dimension mapping added to Onboarding v2
- [ ] start_here selection logic clarified
- [ ] Secrets section empty case handled

**Status:** [0/7] Critical fixes complete

### Medium Fixes
- [ ] Edge case handling added (Inheritance Letter)
- [ ] First week tips templates added
- [ ] Detailed deliverables for Onboarding v2 phases
- [ ] Test strategy added (all plans)
- [ ] Edge case section added (all plans)
- [ ] Paths A/B/C descriptions expanded

**Status:** [0/6] Medium fixes complete

### Nice-to-Have Fixes
- [ ] WCAG accessibility specs
- [ ] Rollback procedures
- [ ] Demo script templates
- [ ] Shared metrics contract
- [ ] Performance benchmarks
- [ ] JSON Schema v2.0 guidance

**Status:** [0/6] Nice-to-have fixes complete

---

## Next Steps After Fixes

1. **Update RESEARCH.md** with new sections:
   - Personality Profiler (already done)
   - Inheritance Letter (new section)
   - CAQI (already done)
   - Onboarding Profile v2 (new section)

2. **Create Detailed Phase Plans** for Part II paths:
   - plan-refactoring-assistant-path-a.md (5-8K words)
   - plan-code-explorer-path-b.md (5-8K words)
   - plan-debt-radar-path-c.md (5-8K words)

3. **Update CLAUDE.md** with:
   - New CLI flags (--onboarding-profile, --inheritance-letter, --caqi, etc.)
   - JSON Schema v2.0
   - Backwards compatibility guidance

4. **Ready for Implementation:**
   - Phase 1: Creative Suite GHI (5-6 hours)
   - Phase 2: Onboarding Profile v2 (3-4 hours)
   - Phase 3: Part II paths (optional, if time allows)

---

**Last Updated:** 2026-06-06  
**Target Completion:** All critical fixes before Phase 1 starts  
**Responsibility:** Review each fix, apply, verify
