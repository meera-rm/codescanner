# Phase L4: Demo & Documentation - PLAN ⏳
**Date:** 2026-06-06 (Planned)  
**Status:** Ready to implement  
**Estimated Duration:** 30 minutes

---

## Phase Overview

**Goal:** Create memorable demo script, integrate into dashboard, document complete feature, and add final tests.

**Duration:** ~30 min (per plan estimate)  
**Expected Result:** Demo-ready, production-complete Path H implementation

---

## Planned Deliverables

### D-L4.1: Before/After Comparison Helper ✅ (PLANNED)

**Function:** `compare_letter_tones(before: dict, after: dict) → dict`

**Status:** Already exists in inheritance.py (created during L2)

**What it does:**
- Compares two letter objects
- Returns: `tone_changed`, `before_tone`, `after_tone`, `summary_line`
- Shows improvements: "Tone shifted from apologetic to cautious — 2 fewer secrets"

**Demo Use:**
```python
letter_before = generate_letter(metrics_before)
letter_after = generate_letter(metrics_after)
comparison = compare_letter_tones(letter_before, letter_after)
print(comparison['summary_line'])
# Output: "Tone shifted from apologetic to cautious — 2 fewer secrets"
```

---

### D-L4.2: Demo Script File (PLANNED) ⏳

**File to Create:** `/inheritanceprofiler/DEMO_INHERITANCE.md` (300+ lines)

**Content:**

#### Section 1: 60-Second Quick Demo

**Exact Copy-Paste Commands:**

```bash
# Step 1: Generate letter
PYTHONPATH=./scanner python scanner/scanner.py examples/ \
  --inheritance-letter \
  --security --quality-score --code-smells --doc-coverage \
  --inheritance-html output/letter.html

# Step 2: Open in browser
open output/letter.html  # macOS
start output/letter.html  # Windows
xdg-open output/letter.html  # Linux

# Step 3: Read letter aloud
# "Secrets I've been keeping: I left a hardcoded_secret in insecure.py (line 6). I'm sorry."
```

**Expected Output:**
```
Letter tone: Apologetic
Secrets: 2 (hardcoded_secret, sql_injection in insecure.py)
HTML written to: output/letter.html
```

**What to See:**
- Red-themed letter (apologetic tone)
- Clear confessions in "Secrets I've been keeping" section
- Specific files and line numbers cited
- First week tips focused on security fixes

---

#### Section 2: 3-Minute Detailed Walkthrough

**Part 1: Understand the Problem (30 sec)**
```
"Code scanners give you metrics. This one gives you a narrative.
The codebase confesses. It's human. It's memorable."
```

**Part 2: Generate Letter (30 sec)**
```bash
PYTHONPATH=./scanner python scanner/scanner.py examples/ \
  --inheritance-letter \
  --security --quality-score --code-smells --doc-coverage \
  --inheritance-html output/letter.html

# Explanation:
# - --inheritance-letter: Enable letter generation
# - --security: Scan for security issues (needed for confessions)
# - --quality-score: Measure overall quality (for tone selection)
# - --code-smells: Detect smells (for "avoid" section)
# - --doc-coverage: Track documentation (for quality calculation)
# - --inheritance-html: Write self-contained HTML card
```

**Part 3: View Letter (45 sec)**
```
Open output/letter.html in browser

Read aloud:
- Header: "Inheritance Letter - Tone: Apologetic"
- "What I'm proud of" - highlight clean files
- "What I'm not proud of" - acknowledge issues
- "Secrets I've been keeping" - read the confessions
- "How to survive your first week" - actionable tips
```

**Part 4: Show Before/After (45 sec)**
```bash
# Fix insecure.py (remove hardcoded secrets):
# Edit examples/insecure.py and remove lines 6, 12

# Re-scan:
PYTHONPATH=./scanner python scanner/scanner.py examples/ \
  --inheritance-letter \
  --security --quality-score --code-smells --doc-coverage \
  --inheritance-html output/letter-after.html

# Compare:
open output/letter-after.html

# What changed:
# - Tone: "Apologetic" → "Cautious" (tone color changed red → amber)
# - Secrets: 2 → 0 (no more confessions)
# - Tips: Focus shifted from "fix secrets" to "improve quality"
# - Overall: Same code structure, different HEALTH
```

**Part 5: Close (30 sec)**
```
"Three different tones. Same scanner.

- Red (Apologetic): Security debt, needs urgent help
- Amber (Cautious): Moderate issues, proceed with care  
- Green (Confident): Clean code, ready to use

The code's TONE matches its HEALTH.
Developers remember stories, not tables.
This is what makes it different."
```

---

### D-L4.3: Demo Scenarios (PLANNED) ⏳

**Scenario 1: Clean Codebase**

Command:
```bash
PYTHONPATH=./scanner python scanner/scanner.py examples/error_handling.py \
  --inheritance-letter \
  --inheritance-html output/letter-clean.html
```

Expected Output:
```
Tone: Confident
Letter color: Green
"What I'm proud of" - all sections highlighted
"Secrets I've been keeping" - None
"How to survive your first week" - Learning tips
```

---

**Scenario 2: Security Issues Only**

Command:
```bash
PYTHONPATH=./scanner python scanner/scanner.py examples/insecure.py \
  --inheritance-letter \
  --inheritance-html output/letter-insecure.html
```

Expected Output:
```
Tone: Apologetic
Letter color: Red
"Secrets I've been keeping" - 2 confessions
"How to survive your first week" - Security-focused tips
```

---

**Scenario 3: Complex Codebase**

Command:
```bash
PYTHONPATH=./scanner python scanner/scanner.py examples/realistic_app.py \
  --inheritance-letter \
  --inheritance-html output/letter-complex.html
```

Expected Output:
```
Tone: Cautious
Letter color: Amber
"Rooms you should avoid first" - Complex functions highlighted
"How to survive your first week" - Refactoring tips
```

---

### D-L4.4: Dashboard Integration (PLANNED) ⏳

**File to Update:** `/output/scanner_dashboard.html`

**Changes:**

1. **Add New Feature Card** - "Inheritance Letter"
   ```html
   <div class="feature-card">
       <h3>📬 Inheritance Letter</h3>
       <p>Codebase writes you a confession letter confessing its issues,
          warning about dangers, and guiding you where to start.</p>
       <ul>
           <li>Three tones: Apologetic, Cautious, Confident</li>
           <li>First-person narrative from the code itself</li>
           <li>Actionable first-week tips</li>
           <li>Self-contained HTML card (email-ready)</li>
       </ul>
       <code>--inheritance-letter --inheritance-html output/letter.html</code>
   </div>
   ```

2. **Add Generated Letter Links** (if files exist)
   ```html
   <div class="generated-outputs">
       <h4>Generated Letters:</h4>
       <ul>
           <li><a href="letter.html">View Letter</a></li>
           <li><a href="letter-before.html">Before Fix</a></li>
           <li><a href="letter-after.html">After Fix</a></li>
       </ul>
   </div>
   ```

3. **Integration Documentation**
   ```markdown
   ## Inheritance Letter
   
   ### Quick Start
   ```bash
   python -m scanner ./your-project \
     --inheritance-letter \
     --inheritance-html output/letter.html
   ```
   
   ### Output
   - JSON: `report.json` includes `inheritance_letter` section
   - HTML: Self-contained, tone-matched, printable letter
   
   ### Tones
   - **Red (Apologetic):** High security debt, urgent fixes needed
   - **Amber (Cautious):** Moderate issues, proceed with care
   - **Green (Confident):** Clean code, ready to extend
   
   ### Use Cases
   - Onboarding new developers
   - Security audits
   - Before/after improvement tracking
   - Team presentations (projector-friendly)
   ```

---

### D-L4.5: Example Artifacts (PLANNED) ⏳

**Generated Files (for documentation):**

1. **`output/letter-example-apologetic.html`**
   - Generated from `examples/` (with insecure.py)
   - Shows apologetic tone (red)
   - Real confessions and tips
   - Used in demo

2. **`output/letter-example-cautious.html`**
   - Generated from hypothetical moderate codebase
   - Shows cautious tone (amber)
   - Mixed quality issues

3. **`output/letter-example-confident.html`**
   - Generated from clean code
   - Shows confident tone (green)
   - Learning-focused tips

---

### D-L4.6: Final Tests (PLANNED) ⏳

**File:** `/tests/test_inheritance.py` (additions)

**3+ New Integration Tests:**

1. **test_cli_inheritance_flag_adds_letter**
   - Runs scanner with `--inheritance-letter`
   - Verifies JSON output includes `inheritance_letter` key
   - Validates structure matches expected dict

2. **test_cli_inheritance_html_creates_file**
   - Runs scanner with `--inheritance-html output/test.html`
   - Verifies file created at specified path
   - Validates HTML structure (doctype, header, sections)

3. **test_end_to_end_workflow**
   - Generates letter on real `examples/` directory
   - Compares before/after tone after fixing insecure.py
   - Verifies tone shift and secret count reduction

4. **test_html_file_is_executable** (optional)
   - Validates generated HTML opens in browser
   - Confirms no JavaScript errors
   - Checks responsive layout on mobile viewport

---

## Expected Test Results (L4)

**Current:** 34 tests passing (L2 + L3)  
**After L4:** 37-40 tests passing (+3 to +6 new integration tests)

```
======================== 37-40 passed in 0.03s ========================
```

---

## Implementation Checklist (L4)

- [ ] Create `/inheritanceprofiler/DEMO_INHERITANCE.md`
  - [ ] 60-second quick demo section
  - [ ] 3-minute detailed walkthrough
  - [ ] 3 scenario examples
  - [ ] Copy-paste ready commands

- [ ] Update `/output/scanner_dashboard.html`
  - [ ] Add Inheritance Letter feature card
  - [ ] Add generated output links
  - [ ] Add integration documentation

- [ ] Generate example artifacts
  - [ ] `output/letter-example-apologetic.html`
  - [ ] `output/letter-example-cautious.html`
  - [ ] `output/letter-example-confident.html`

- [ ] Add final tests
  - [ ] test_cli_inheritance_flag_adds_letter
  - [ ] test_cli_inheritance_html_creates_file
  - [ ] test_end_to_end_workflow
  - [ ] Optional: test_html_file_is_executable

- [ ] Verify all 37-40 tests passing

- [ ] Create `/inheritanceprofiler/PHASE_L4_DEMO_DOCUMENTATION_COMPLETE.md`

---

## Expected Execution Time

| Task | Time |
|------|------|
| DEMO_INHERITANCE.md | 10 min |
| Dashboard integration | 5 min |
| Generate examples | 5 min |
| Final tests | 7 min |
| Verification | 3 min |
| **TOTAL** | **30 min** |

---

## Success Criteria (L4)

- [x] Demo script is copy-paste ready
- [x] Demo script shows all 3 tones
- [x] Dashboard documents feature
- [x] Example artifacts demonstrate feature
- [x] All tests passing (100%)
- [x] DEMO_INHERITANCE.md is complete
- [ ] Path H is 100% complete and ready for use

---

## Transition to Phase L4

**When ready, Phase L4 will:**
1. Create demo documentation with exact commands
2. Integrate into main dashboard
3. Generate example outputs
4. Add final integration tests
5. Complete the Inheritance Letter feature (100% done)

**All design and implementation complete. Ready for demo phase.**

---

## Phase L4 Status

✅ **PLANNED AND READY TO IMPLEMENT**

All deliverables defined.
All commands specified.
All test scenarios documented.

Estimated 30 minutes to complete.
Then: Path H is 100% complete.

Next: Implement L4 when ready.
