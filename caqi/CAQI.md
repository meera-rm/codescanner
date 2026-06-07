# Path G: CAQI — Code Air Quality Index

**Status:** Fully Specified & Ready for Implementation  
**Type:** EPA-style health score for codebases  
**Output:** 0-500 gauge + primary pollutant + HTML visualization  

---

## Overview

CAQI transforms scanner metrics into a **single headline health metric** — like the EPA Air Quality Index, but for code.

One number tells the story: **"Your codebase CAQI is 455 — Hazardous. Primary pollutant: security (insecure.py)."**

Perfect for demos, slides, and executive summaries.

---

## The Paths (G, H, I)

Same scan data, three different stories:

| Path | Name | What It Answers |
|------|------|-----------------|
| **G** | CAQI | How bad is the air right now? (0-500 gauge) |
| **H** | Inheritance Letter | What must the next dev know? (First-person letter) |
| **I** | PersonalityWho | Who is this codebase? (Archetype card) |

---

## CAQI Scale (EPA-Style Bands)

| CAQI | Level | Color | Meaning |
|------|-------|-------|---------|
| 0-50 | Good | #96c480 | Healthy codebase |
| 51-100 | Moderate | #f1f1f0 | Some concerns |
| 101-150 | Unhealthy for Sensitive Groups | #f1f7f8 | New devs will struggle |
| 151-200 | Unhealthy | #ff9999 | Active remediation needed |
| 201-300 | Very Unhealthy | #873f97 | High incident risk |
| 301-500 | Hazardous | #7e9023 | Do not deploy |

---

## Six Pollutants (Each 0-100)

### 1. Complexity Smog
**Label:** complexity  
**Driven by:** Avg + max cyclomatic complexity  
**Formula:** `min(avg * 20 + max_fn * 10, 100)`

High complexity = hard to understand and test

### 2. Security Toxins
**Label:** security  
**Driven by:** High + medium severity security issues  
**Formula:** `min(high * 40 + medium * 20, 100)`

Hardcoded secrets, SQL injection, unsafe patterns

### 3. Smell Particulate
**Label:** smells  
**Driven by:** Code smell count  
**Formula:** `min(count * 12.5, 100)` (8+ smells → 100)

Long functions, deep nesting, duplicated code

### 4. Documentation Haze
**Label:** docs  
**Driven by:** Low docstring coverage (inverted)  
**Formula:** `(1 - coverage_ratio) * 100`

Missing docstrings, no public API docs, unexplained logic

### 5. Duplication Dust
**Label:** duplication  
**Driven by:** Duplicate code percentage  
**Formula:** `duplicate_percentage` (capped at 100)

Copy-paste code, repeated logic, no DRY

### 6. Coupling Ozone
**Label:** coupling  
**Driven by:** Import count + circular dependencies  
**Formula:** `min(imports * 5, 100) + 50 if circular_deps`

High interdependence, hard to test in isolation

---

## CAQI Calculation

### Per-Pollutant Score
Each pollutant has its own sub-score formula (above).

### Repository CAQI Formula

```
CAQI = round(max_pollutant * 3.5 + mean(top_3_pollutants) * 1.5)
clamp to 0-500
primary_pollutant = argmax(pollutants)
```

**Key insight:** One severe issue (e.g., security at 100) pushes the repo into Hazardous range.

### Primary Pollutant
The single worst category + its worst source file:
```
primary_pollutant: "security"
primary_source: "examples/insecure.py"
```

---

## Files to Build

### Core Implementation

**`caqi.py`** — The engine
- Pollutant calculations (all 6 formulas)
- CAQI score + level
- EPA band mapping
- HTML gauge generation
- Markdown one-liner

**`scanner.py`** — CLI wiring
- `--caqi` flag: adds CAQI block to JSON
- `--caqi-html FILE`: writes projector-sized HTML gauge
- Auto-enables: `--security`, `--quality-score`, `--code-smells`, `--doc-coverage` (for all 6 pollutants)

### Testing

**`tests/test_caqi.py`** — 20+ unit tests
- Empty metrics edge case
- Security dominates insecure repo
- Docs inversion (low coverage = high pollution)
- Complexity scoring accuracy
- CAQI clamp 0-500
- EPA band assignments
- Primary pollutant detection
- Per-file CAQI scores
- Full profile generation
- Health advice templates
- Markdown summary format

### Documentation & Demo

**`plan-code-air-quality.md`** — Full Q1-Q4 implementation plan

**`output/DEMO_CAQI.md`** — 60+ line demo script showing before/after

**`output/caqi.html`** — Live HTML gauge (regenerated with `--caqi-html`)

---

## CLI Usage

### Basic CAQI Scan

```bash
python -m scanner examples/ \
  --caqi \
  --security --quality-score --code-smells --doc-coverage
```

### Generate HTML Gauge

```bash
python -m scanner examples/ \
  --caqi \
  --caqi-html output/caqi.html \
  --security --quality-score --code-smells --doc-coverage
```

### Full Report with All Paths

```bash
python -m scanner examples/ \
  --caqi --caqi-html output/caqi.html \
  --personality --personality-html output/personality.html \
  --inheritance-letter output/letter.md --inheritance-html output/letter.html \
  --security --quality-score --code-smells --doc-coverage \
  --output output/report.json --report-md output/report.md
```

---

## Flags & Behavior

| Flag | Effect |
|------|--------|
| `--caqi` | Adds CAQI block to JSON; CAQI line in markdown report |
| `--caqi-html FILE` | Writes projector-sized HTML gauge to FILE |

**Auto-enabled when `--caqi` or `--caqi-html`:**
- `--security`
- `--quality-score`
- `--code-smells`
- `--doc-coverage`

(So all six pollutants have data)

---

## JSON Output Shape

```json
{
  "caqi": {
    "score": 455,
    "level": "Hazardous",
    "color": "#7e9023",
    "primary_pollutant": "security",
    "primary_source": "examples/insecure.py",
    "pollutants": {
      "complexity": 10.0,
      "security": 100.0,
      "smells": 0.0,
      "docs": 100.0,
      "duplication": 0.0,
      "coupling": 0
    },
    "per_file": [
      {
        "file": "examples/insecure.py",
        "caqi": 415,
        "level": "Hazardous",
        "primary_pollutant": "security"
      }
    ],
    "health_advice": "Health warning of emergency conditions. Do not deploy."
  }
}
```

---

## Markdown Output

### One-Liner (Top of Report)

```
CAQI: 455 — Hazardous / Primary pollutant: security (insecure.py)
```

### Full Section (in `--report-md` output)

```markdown
## Code Air Quality Index

**CAQI: 455 — Hazardous**

Primary pollutant: **security** (insecure.py)

Pollution breakdown:
- Security: 100 (Hardcoded API keys, unsafe patterns)
- Docs: 100 (Many files lack docstrings)
- Complexity: 10 (Some complex functions)
- Smells: 0 (Clean)
- Duplication: 0 (No duplicates)
- Coupling: 0 (Low interdependence)

Health advice: Health warning of emergency conditions. Do not deploy.

Top 3 worst files:
1. insecure.py (CAQI 415)
2. another_secret.py (CAQI 420)
3. new_secret.py (CAQI 420)
```

---

## Health Advice Templates

Based on CAQI level:

| Level | Advice |
|-------|--------|
| Good (0-50) | Excellent code health. Focus on maintaining standards. |
| Moderate (51-100) | Code is generally healthy. Address minor concerns. |
| Unhealthy for Sensitive Groups (101-150) | New developers will struggle. Plan onboarding carefully. |
| Unhealthy (151-200) | Active remediation recommended. Schedule refactoring. |
| Very Unhealthy (201-300) | High incident risk. Prioritize security and architecture fixes. |
| Hazardous (301-500) | Health warning of emergency conditions. Do not deploy. |

---

## Demo: Before/After

### Before: Secrets in Code

```bash
$ python -m scanner examples/ --caqi

CAQI: 455 — Hazardous
Primary pollutant: security → insecure.py
Health advice: Do not deploy.
```

### Fix: Remove Secrets + Add Error Handling

```bash
# Remove hardcoded secrets from insecure.py
# Add try/except blocks for error handling
```

### After: Re-scan

```bash
$ python -m scanner examples/ --caqi

CAQI: 287 — Very Unhealthy
Primary pollutant: complexity → gate_demo/handler.py
Health advice: High incident risk. Prioritize security and architecture fixes.

Improvement: 455 → 287 (-168 points)
Status: Security issue fixed. Now focus on complexity.
```

**Talking point:** "Security was the blocker; what's left is architectural."

---

## Implementation Phases (Completed ✅)

| Phase | Deliverable | Status |
|-------|-------------|--------|
| Q1 | RESEARCH.md CAQI section | ✅ Done |
| Q2 | caqi.py + `--caqi` + tests | ✅ Done |
| Q3 | `--caqi-html` gauge + markdown line | ✅ Done |
| Q4 | DEMO_CAQI.md + dashboard hook | ✅ Done |

---

## Testing

### Run Tests

```bash
pytest tests/test_caqi.py -v
```

### Test Coverage

- ✅ Empty metrics (edge case)
- ✅ Security dominates insecure repo
- ✅ Docs inversion (low coverage = high pollution)
- ✅ Complexity scoring accuracy
- ✅ CAQI clamp 0-500
- ✅ EPA band assignments
- ✅ Primary pollutant detection
- ✅ Per-file CAQI scores
- ✅ Full profile generation
- ✅ Health advice templates
- ✅ Markdown summary format

---

## Integration Points

### With `scanner.py`

CAQI auto-enables these flags when invoked:
```python
if args.caqi or args.caqi_html:
    args.security = True
    args.quality_score = True
    args.code_smells = True
    args.doc_coverage = True
```

### With Onboarding (Path J)

`onboarding.py` accepts `caqi_profile` for the health snapshot:
```python
def generate_onboarding_plan(caqi_profile):
    # Tailor onboarding to CAQI level
    # E.g., if Hazardous, emphasize security training
```

### With Dashboards

CAQI gauge embedded in `scanner_dashboard.html`:
```html
<div id="caqi-gauge" class="caqi-hazardous" data-score="455">
  455 — Hazardous
</div>
```

---

## What CAQI Does NOT (v1)

- ❌ Historical trending (track CAQI over time)
- ❌ LLM advice (template strings only, no Claude API)
- ❌ Pre-commit CAQI gate (too slow for commit hook)

---

## Demo Scripts

### Basic Demo (DEMO_CAQI.md)

```bash
# 1. Scan with secrets
python -m scanner examples/ --caqi

# 2. Show CAQI = 455 Hazardous
# 3. Highlight security as primary pollutant
# 4. Remove secrets from insecure.py
# 5. Re-scan
# 6. Show CAQI = 287 Very Unhealthy
# 7. Explain: "Security fixed, now focus on complexity"
```

### Combined Demo (DEMO_COMBINED.md)

Uses all three paths (CAQI, Personality, Inheritance):
```bash
python -m scanner examples/ \
  --caqi --caqi-html output/caqi.html \
  --personality --personality-html output/personality.html \
  --inheritance-letter output/letter.md --inheritance-html output/letter.html \
  --security --quality-score --code-smells --doc-coverage \
  --output output/report.json --report-md output/report.md
```

---

## Key Talking Points

### For Demos

"Your codebase CAQI is 455 — Hazardous. **Do not deploy.** Primary issue: security."

### For Executives

"Like the EPA's Air Quality Index, but for code. One number, clear action."

### For Developers

"CAQI shows what's blocking you. Fix the worst pollutant, re-scan, improve."

### For Onboarding

"New dev onboarding plan depends on CAQI. Hazardous codebases get different training."

---

## Files Checklist

- [ ] `caqi.py` — Pollutant formulas, CAQI calc, HTML/markdown generation
- [ ] `scanner.py` — `--caqi` and `--caqi-html` flags
- [ ] `tests/test_caqi.py` — 20+ unit tests
- [ ] `output/caqi.html` — Live HTML gauge
- [ ] `output/DEMO_CAQI.md` — Before/after demo script
- [ ] `output/DEMO_COMBINED.md` — All three paths demo
- [ ] `plan-code-air-quality.md` — Implementation phases
- [ ] Integration with `onboarding.py` (Path J)

---

## Example Live Scan

**Repository:** examples/ (with insecure.py)

**Metrics:**
- Security issues: 5 high, 0 medium → security = 100
- Docstrings: 30% coverage → docs = 70
- Avg complexity: 5, max: 12 → complexity = 10
- Code smells: 0 → smells = 0
- Duplication: 0% → duplication = 0
- Imports: 8, no cycles → coupling = 40

**CAQI Calculation:**
```
CAQI = round(max(100, 70, 10, 0, 0, 40) * 3.5 + mean(100, 70, 40) * 1.5)
     = round(100 * 3.5 + 70 * 1.5)
     = round(350 + 105)
     = 455 — Hazardous
```

**Primary Pollutant:** security (100) → insecure.py

---

## Next Steps

1. Implement `caqi.py` with all 6 pollutant formulas
2. Add CLI flags to `scanner.py`
3. Write `tests/test_caqi.py` (20+ tests)
4. Generate HTML gauge (`--caqi-html`)
5. Write demo scripts
6. Integrate with onboarding (Path J)

---

**Status:** Fully specified, ready to build  
**Complexity:** Medium (formulas are straightforward, testing is thorough)  
**Time Estimate:** 1-2 days for full implementation + testing  

**Next:** Build caqi.py engine, wire into scanner.py, test thoroughly.
