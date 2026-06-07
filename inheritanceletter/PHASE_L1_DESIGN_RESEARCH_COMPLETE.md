# Phase L1: Design & Research - COMPLETE ✅
**Date:** 2026-06-06  
**Status:** Production Ready  
**Documentation:** Locked and comprehensive

---

## Phase Overview

**Goal:** Lock letter structure, tone rules, and demo script before writing code.

**Duration:** ~30 min (per plan estimate)  
**Result:** Complete design specification in RESEARCH.md + demo script ready

---

## Deliverables

### D-L1.1: RESEARCH.md - Inheritance Letter Section ✅

**Location:** `/plan/RESEARCH.md` (lines 293-900+)

**Content Added to RESEARCH.md:**

#### 1. Problem Statement
- Onboarding docs are boring and overwhelming
- Code metrics don't become stories or confessions
- Security findings are lists, not warnings
- Complexity hotspots are tables, not guidance

#### 2. The Solution: First-Person Letter
```
The codebase writes a letter to its next owner.
Not a report - a "Dear developer, I owe you an honest conversation"
narrative that confesses mistakes, warns of dangers, and suggests
safe entry points.
```

#### 3. Why This Approach Works
- **Memorable:** Prose beats tables
  - Bad: "Complexity 3.1, 45 security findings, 62% test coverage"
  - Good: "There's a query in injection.sql (Line 15) that could be exploited. Please fix me."

- **Actionable:** Specific files + functions cited
  - Evidence grounded in real metrics
  - Developer knows exactly where to start

- **Emotional:** First-person voice creates accountability
  - Code confesses its mistakes
  - More human than a lint report

#### 4. Letter Structure (v1)

**Template Format:**

```
Dear Developer,

I'm the [directory] codebase. I've been scanned, and I owe you
an honest conversation.

### What I'm proud of
[2-3 best files with quality grade + reasoning]

### What I'm not proud of
[2-3 worst files - smells, low quality, high complexity]

### Secrets I've been keeping
[Security findings as first-person confessions]

### Rooms you should avoid first
[Top 3 complex functions - name, complexity, file]

### Where to start instead
[1-2 low-complexity, clean files for onboarding]

### How to survive your first week
[3 actionable tips derived from scan data]

Yours [apologetically / cautiously / confidently],
A codebase that knows too much about itself
```

**Section Rationale:**

| Section | Why | Source |
|---------|-----|--------|
| **Proud** | Highlight best practices to learn from | Quality scores |
| **Not Proud** | Acknowledge weak areas honestly | Quality, complexity, smells |
| **Secrets** | Confess security debt | Security findings |
| **Avoid** | Warn about dangerous code | Cyclomatic complexity |
| **Start Here** | Guide safe onboarding | Lowest complexity + clean files |
| **First Week** | Give immediate actionable steps | Tone + dominant issues |

---

### D-L1.2: Tone Catalog ✅

**3 Distinct Tones Based on Code Health**

#### Tone Selection Logic

**Priority-Based Matching:**
1. **Apologetic** - if `security_high_count ≥ 1` OR `avg_quality < 55`
   - Trigger: Security issues or poor quality
   - Signal: Code needs immediate help
   - Sign-off: "Yours apologetically,"

2. **Cautious** - if `avg_quality 55-74` OR `total_smells > 10`
   - Trigger: Moderate quality + moderate issues
   - Signal: Proceed with care, some work needed
   - Sign-off: "Yours cautiously,"

3. **Confident** - if `avg_quality ≥ 75` AND `security_clean` AND `smells ≤ 5`
   - Trigger: High quality + clean security
   - Signal: Good health, ready to use
   - Sign-off: "Yours confidently,"

**Fallback:** Cautious (for ambiguous cases)

#### Tone Characteristics

**Apologetic (Red #e63946):**
- Language: Regretful, urgent, action-oriented
- Audience: Teams with security debt
- First Week Tips focus on: Security fixes
- Example: "I left an API key in insecure.py. I'm sorry."

**Cautious (Amber #f77f00):**
- Language: Measured, balanced, improvement-focused
- Audience: Teams with moderate tech debt
- First Week Tips focus on: Quality improvements
- Example: "I'm fairly complex in places. Let's talk about refactoring."

**Confident (Green #06d6a0):**
- Language: Professional, clear, contribution-ready
- Audience: Well-maintained codebases
- First Week Tips focus on: Learning and contribution
- Example: "I'm well-documented and maintainable. Ready to contribute?"

---

### D-L1.3: Example Letter for `examples/` ✅

**Expected Results for Scanner's `examples/` Directory:**

```
Tone: Apologetic

(Due to security findings in insecure.py)

### What I'm proud of
- error_handling.py (quality: 82/100)
- utils.py (quality: 75/100)

### What I'm not proud of
- insecure.py (quality: 30/100, has hardcoded secrets)
- realistic_app.py (complexity: 3.5, authenticate_user is complex)

### Secrets I've been keeping
- I left a hardcoded_secret in insecure.py (line 6)
- I left a sql_injection risk in insecure.py (line 12)

### Rooms you should avoid first
- authenticate_user() in realistic_app.py (complexity: 6)
- process_request() in insecure.py (complexity: 5)
- validate_query() in realistic_app.py (complexity: 4)

### Where to start instead
- sample.py (complexity: 1.5, safe entry point)
- error_handling.py (complexity: 2.0, well-structured)

### How to survive your first week
1. Enable pre-commit security gate to catch secrets before commit
2. Review and fix all hardcoded secrets and injection risks first
3. Schedule security audit with team

Yours apologetically,
A codebase that knows too much about itself
```

---

### D-L1.4: Non-Goals (v1) ✅

**Explicitly NOT Including:**

| Feature | Why Not | When Later |
|---------|--------|-----------|
| **LLM Calls** | Adds complexity, external dependency | Phase 2+ if needed |
| **Per-Function Letters** | Too granular, overwhelming | Future enhancement |
| **Slack/Email Integration** | Out of scope for MVP | Phase 2+ |
| **Interactive CLI Wizard** | Too much UI, CLI-only is better | Future enhancement |
| **Email Delivery** | Out of scope for scanner | Future feature |
| **Slack Posting** | Out of scope for scanner | Future feature |

**What We ARE Building:**
- ✅ Rule-based generation (templates, no LLM)
- ✅ File output (JSON, Markdown, HTML)
- ✅ CLI flags for integration
- ✅ Professional formatting

---

## Demo Script

### D-L1.5: 3-Minute Demo Script (Ready) ✅

**HOOK (15 seconds):**
```
"Most scanners give you spreadsheets. This one writes you a letter.
From your code. About itself. Confessing. The codebase talks."
```

**RUN SCAN (20 seconds):**
```bash
PYTHONPATH=./scanner python scanner/scanner.py examples/ \
  --inheritance-letter \
  --security --quality-score --code-smells --doc-coverage \
  --output output/report.json \
  --inheritance-html output/letter.html
```

**LETTER DISPLAY (60 seconds):**
```
Open output/letter.html in browser

"Meet insecure.py. It wrote this letter to you. It's confessing.
'I left an API key on line 6. I'm sorry.'

That's not judgment. That's confession. From the code itself.

And look at the first week tips - they're not generic.
They're specific to THIS codebase's problems.

This is what happens when code admits the truth
instead of hiding behind metrics."
```

**BEFORE/AFTER BEAT (45 seconds):**
```
Fix insecure.py (remove hardcoded secrets):

python scanner/scanner.py examples/ \
  --inheritance-letter \
  --security --quality-score --code-smells --doc-coverage \
  --inheritance-html output/letter-after.html

"Watch the tone shift. Same code, healthier.

Tone changed from 'apologetic' to 'cautious'.
The letter sounds different. More confident.

Metrics changed by just removing a few secrets.
But the letter - the TONE of the confession - that's what matters to a developer."
```

**CLOSE (15 seconds):**
```
"Three lenses. One scanner. Every codebase gets a voice.

This is what I would build."
```

---

## Design Decisions Locked

### 1. First-Person Narrative (vs. Third-Person Report)
**Decision:** Use first-person ("I left a secret") not third-person ("the code has a secret")

**Rationale:**
- More human, less mechanical
- Creates accountability (code admits mistakes)
- More memorable for developers
- Stands out from standard linters

**Example:**
- ✅ "I left an API key in insecure.py (line 6). I'm sorry."
- ❌ "Hardcoded API key found at insecure.py:6"

### 2. Tone-Based Personality (vs. Neutral Reporting)
**Decision:** Change letter tone based on code health (apologetic/cautious/confident)

**Rationale:**
- Matches code actual health
- Different teams get different guidance
- Creates emotional resonance
- Actionable without being judgmental

### 3. Rule-Based Matching (vs. ML/LLM)
**Decision:** Use deterministic rules for tone selection and tips

**Rationale:**
- No external dependencies
- Reproducible results
- Fast execution
- Transparent logic

### 4. Template-Based Tips (vs. Generated)
**Decision:** Use pre-written tone-specific templates for first-week tips

**Rationale:**
- Consistent quality
- No LLM calls needed
- Easier to customize per org
- Proven effective copy

### 5. Graceful Section Omission (vs. Always Showing)
**Decision:** Omit sections when empty, show "None" message instead of fake data

**Rationale:**
- Honest reporting
- No manufactured concerns
- Clean output
- Builds trust

---

## Acceptance Criteria (L1)

All criteria for Phase L1 met:

- [x] RESEARCH.md section readable standalone in under 5 minutes
- [x] Example letter cites real files from `examples/`
- [x] Demo script provided (3-minute version)
- [x] Letter structure documented with sections
- [x] Tone selection rules explicit
- [x] Non-goals listed (no LLM, no email, etc.)
- [x] Design decisions locked before implementation
- [x] All decisions ready for L2 implementation

---

## What Was NOT Done (Intentionally)

- ❌ No code written (design-only phase)
- ❌ No tests created (will come in L2)
- ❌ No CLI integration (will come in L2)
- ❌ No HTML generation (will come in L3)

**Reason:** Locked design first, code follows.

---

## Transition to L2

With L1 complete, L2 is ready to start immediately:

**L2 Implementation Plan:**
1. Create `inheritance.py` with 10 functions
2. Wire into `scanner.py` with `--inheritance-letter` flag
3. Create test fixtures and 26 tests
4. Verify all tests pass (100%)
5. Generate test letter on real `examples/` directory

**All design decisions are locked - no changes to structure expected.**

---

## Files Reference

**Design locked in RESEARCH.md:**
- Lines 293-400: Problem statement + solution
- Lines 401-500: Letter structure
- Lines 501-650: Tone catalog with examples
- Lines 651-900: Demo script + non-goals

---

## Phase L1 Status

✅ **COMPLETE AND READY FOR IMPLEMENTATION**

All design questions answered.
All decisions locked.
Ready to code L2.

Next: Phase L2 - Letter Engine Implementation
