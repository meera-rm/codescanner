# CAQI (Code Air Quality Index) — Complete Architecture Breakdown

## 1. CAQI Overview & Concept

**What It Is:**
- EPA-style health score for codebases (0-500 scale)
- Primary pollutant identification (worst category + source file)
- Headline metric for demos and stakeholder reports
- Not a long report—instant snapshot of code health

**Why This Design:**
- Single number (CAQI score) vs overwhelming spreadsheets
- EPA bands familiar to anyone who's seen air quality reports
- Primary pollutant tells you WHERE to focus (security, complexity, etc.)
- Works for quick decision-making (deploy? refactor? audit?)

**The 3 Paths (Same Data, Different Stories):**
- **Path G: Personality** — Who is this codebase? (Archetype card)
- **Path H: Inheritance Letter** — What must the next dev know? (First-person letter)
- **Path I: CAQI** — How bad is the air right now? (0-500 gauge)

---

## 2. The 6 Pollutants (Each Scored 0-100)

### Pollutant 1: Complexity
**Label:** Complexity Smog
**Driven By:** Average + max cyclomatic complexity
**Formula:** `min(avg_cyclomatic * 20 + max_fn_cyclomatic * 10, 100)`
**Meaning:** High complexity = harder to understand, test, maintain
**Example:** Function with avg 2.5, max 5 → min(2.5*20 + 5*10, 100) = min(75, 100) = 75

### Pollutant 2: Security
**Label:** Security Toxins
**Driven By:** High + medium severity findings
**Formula:** `min(high_vulns * 40 + medium_vulns * 20, 100)`
**Meaning:** Hardcoded secrets, SQL injection, missing error handling
**Example:** 2 high + 1 medium → min(2*40 + 1*20, 100) = min(100, 100) = 100

### Pollutant 3: Smells
**Label:** Smell Particulates
**Driven By:** Code smell count
**Formula:** `min(code_smell_count * 12.5, 100)` (8+ smells → 100)
**Meaning:** Long functions (>20 lines), deep nesting (>3 levels), too many params (>4)
**Example:** 5 smells → min(5*12.5, 100) = min(62.5, 100) = 62.5

### Pollutant 4: Documentation
**Label:** Documentation Haze
**Driven By:** Low coverage ratio (INVERTED)
**Formula:** `(1 - coverage_ratio) * 100`
**Meaning:** Missing docstrings = pollution. 0 coverage = 100 pollution. 100% coverage = 0 pollution
**Example:** 80% documented → (1 - 0.80) * 100 = 20

### Pollutant 5: Duplication
**Label:** Duplication Dust
**Driven By:** Duplicate percentage
**Formula:** `duplicate_percentage (capped at 100)`
**Meaning:** Duplicate code blocks (3+ lines) increase maintenance burden
**Example:** 25% duplicated → 25

### Pollutant 6: Coupling
**Label:** Coupling Ozone
**Driven By:** Import count + circular dependencies
**Formula:** `min(imports * 5, 100) + 50 if circular_deps else 0`
**Meaning:** Too many imports = tight coupling. Circular deps = architectural debt
**Example:** 8 imports, no circular → min(8*5, 100) + 0 = 40

---

## 3. Repo CAQI Calculation (The Roll-Up)

### The Formula

```
CAQI = round(max_pollutant * 3.5 + mean(top_3_pollutants) * 1.5)
Clamped to [0, 500]
primary_pollutant = argmax(pollutants)
```

### Why This Weighting?

**`max_pollutant * 3.5`** — Amplifies worst problem
- If security = 100, CAQI starts at 350
- One severe issue (e.g., hardcoded secrets at 100) dominates
- Security is the gatekeeper: blocks everything else

**`mean(top_3) * 1.5`** — Considers overall health
- Averages the next 3 worst issues
- Dampens single-issue bias
- E.g., if top_3 = [100, 60, 40], mean = 66.67, contribution = 100

### Example Calculation

```
Pollutants: {
  complexity: 60,
  security: 100,      ← MAX
  smells: 40,
  docs: 30,
  duplication: 20,
  coupling: 10
}

max_pollutant = 100
top_3 = [100, 60, 40]
mean_top_3 = (100 + 60 + 40) / 3 = 66.67

CAQI = round(100 * 3.5 + 66.67 * 1.5)
     = round(350 + 100)
     = 450 (Hazardous)

primary_pollutant = "security"
```

---

## 4. EPA-Style Bands (0-500 Scale)

| CAQI Range | Level | Color | Meaning | Action |
|-----------|-------|-------|---------|--------|
| 0-50 | Good | #96c480 | Healthy codebase | Continue best practices |
| 51-100 | Moderate | #f1f1f0 | Some concerns | Monitor & plan improvements |
| 101-150 | Unhealthy for Sensitive Groups | #f1f7f8 | New devs will struggle | Refactor before onboarding |
| 151-200 | Unhealthy | #ff9999 | Active remediation needed | Schedule sprints to fix |
| 201-300 | Very Unhealthy | #873f97 | High incident risk | Immediate action plan |
| 301-500 | Hazardous | #7e9023 | Do not deploy | Emergency response |

**Why EPA Style?**
- Familiar metaphor (air quality = code quality)
- Visual clarity (color coding)
- Urgency signals (Green → Red)

---

## 5. Data Structure: JSON Output Shape

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
        "primary_pollutant": "security"
      },
      // ... top 10 worst files
    ],
    
    "health_advice": "Health warning of emergency conditions. Do not deploy."
  }
}
```

**Key Fields:**
- `score` — 0-500 CAQI
- `level` — Good/Moderate/Unhealthy/Very Unhealthy/Hazardous
- `color` — Hex color for UI
- `primary_pollutant` — Worst category (security, complexity, etc.)
- `primary_source` — File with the issue
- `pollutants` — All 6 scores
- `per_file` — CAQI for each file (for drill-down)
- `health_advice` — Human-readable guidance

---

## 6. Output Formats

### Markdown One-Liner (Top of Report)

```
CAQI: 455 — Hazardous / Primary pollutant: security (insecure.py)
```

**Purpose:** Headline for stakeholders, CI/CD logs, team Slack

### HTML Gauge (Projector-Sized)

**Tool:** Chart.js template
**Rendering:** Circular gauge with:
- Score (455)
- Level badge (Hazardous)
- Color coding (#7e9023)
- Primary pollutant callout
- Health advice text

**Use Case:** Presentation slides, dashboards, stakeholder meetings

### CLI Output

```bash
python -m scanner ./examples \
  --caqi \
  --caqi-html output/caqi.html \
  --security --quality-score --code-smells --doc-coverage \
  --output output/report.json
```

**Flags:**
- `--caqi` — Adds CAQI to JSON + markdown report
- `--caqi-html FILE` — Writes projector-sized HTML gauge

---

## 7. Calculation Flow (Phase-by-Phase)

### Phase Q1: Research & Design
- Define 6 pollutants
- Design EPA band scale
- Create roll-up formula
- Validate on examples/

### Phase Q2: Core Engine (caqi.py)
- Implement `calculate_pollutant(metrics)` for each of 6
- Implement `calculate_repo_caqi(pollutants_dict)`
- Handle edge cases: empty metrics, single pollutant dominance, clamping
- Write 20+ unit tests

### Phase Q3: HTML Gauge + Markdown
- Chart.js template for gauge rendering
- Markdown one-liner generation
- Integration with scanner.py CLI

### Phase Q4: Dashboard Hook
- Integrate CAQI into scanner_dashboard.html
- Add CAQI card to main overview
- Link to full gauge viewer

---

## 8. The Before/After Demo (Real Example)

### BEFORE: Scan with Hardcoded Secrets

```python
# insecure.py
API_KEY = "sk-abc123xyz789"
password = "SuperSecretPass123"
```

**Result:**
```
Pollutants:
  complexity: 10.0
  security: 100.0      ← BLOCKER
  smells: 0.0
  docs: 100.0
  duplication: 0.0
  coupling: 0

CAQI = round(100 * 3.5 + mean([100, 100, 10]) * 1.5)
     = round(350 + 70)
     = ~455 Hazardous

Primary pollutant: security (insecure.py:6)
```

**Message:** "Your codebase CAQI is 455 — Hazardous. Security blocker detected."

### AFTER: Secrets Removed + Error Handling Added

```python
# Fixed: Use environment variables
API_KEY = os.getenv("API_KEY")
password = os.getenv("PASSWORD")

# Added error handling
try:
    fetch_user_data(user_id)
except FileNotFoundError:
    logger.error("User data not found")
```

**Result:**
```
Pollutants:
  complexity: 60.0
  security: 0.0        ← FIXED
  smells: 40.0
  docs: 20.0
  duplication: 0.0
  coupling: 0

CAQI = round(60 * 3.5 + mean([60, 40, 20]) * 1.5)
     = round(210 + 45)
     = ~287 Very Unhealthy

Primary pollutant: complexity (realistic_app.py)
```

**Message:** "Security fixed (-168 points). Now complexity is the blocker."
**Talking Point:** "Security was the gatekeeper. With it gone, we see the real architectural debt."

---

## 9. Sub-Score Formulas (All 6 Pollutants)

### Complexity: min(avg * 20 + max_fn * 10, 100)
```python
def complexity_score(avg_cyclomatic, max_fn_cyclomatic):
    return min(avg_cyclomatic * 20 + max_fn_cyclomatic * 10, 100)

# Example
# avg=2.5, max=5 → min(50 + 50, 100) = 100
# avg=1.5, max=2 → min(30 + 20, 100) = 50
```

### Security: min(high * 40 + medium * 20, 100)
```python
def security_score(high_vulns, medium_vulns):
    return min(high_vulns * 40 + medium_vulns * 20, 100)

# Example
# 2 high, 1 medium → min(80 + 20, 100) = 100
# 1 high, 0 medium → min(40 + 0, 100) = 40
```

### Smells: min(count * 12.5, 100)
```python
def smells_score(code_smell_count):
    return min(code_smell_count * 12.5, 100)

# Example (8+ smells → 100)
# 5 smells → min(62.5, 100) = 62.5
# 8 smells → min(100, 100) = 100
```

### Docs: (1 - coverage_ratio) * 100
```python
def docs_score(coverage_ratio):
    return (1 - coverage_ratio) * 100

# Example (inverted: missing = pollution)
# 100% documented → (1 - 1.0) * 100 = 0 (good)
# 50% documented → (1 - 0.5) * 100 = 50
# 0% documented → (1 - 0.0) * 100 = 100 (bad)
```

### Duplication: duplicate_percentage (capped at 100)
```python
def duplication_score(duplicate_percentage):
    return min(duplicate_percentage, 100)

# Example
# 25% duplicated → 25
# 105% (overflow) → 100
```

### Coupling: min(imports * 5, 100) + (50 if circular else 0)
```python
def coupling_score(import_count, has_circular_deps):
    base = min(import_count * 5, 100)
    circular_penalty = 50 if has_circular_deps else 0
    return min(base + circular_penalty, 100)

# Example
# 8 imports, no circular → min(40, 100) + 0 = 40
# 8 imports, circular → min(40, 100) + 50 = 90
```

---

## 10. Key Design Insights

### Why max_pollutant * 3.5?
- Security (hardcoded secrets, SQL injection) blocks everything
- One severe issue should dominate CAQI
- Prevents "good average" masking critical problems

### Why mean(top_3) * 1.5?
- Balances single-issue bias
- Rewards teams fixing THE critical issue while ignoring others
- E.g., fix security from 100 → 0, CAQI drops significantly even if complexity stays high

### Why Invert Documentation?
- Missing docs = pollution (counterintuitive but powerful)
- 100% coverage = 0 pollution
- Forces teams to document to reduce CAQI
- Aligns with EPA metaphor (less pollution = cleaner code)

### Why Separate Pollutants?
- Diagnostics: "Which issue blocks us?" → primary_pollutant
- Roadmap: Team can say "Fix security first, then complexity"
- Metrics: Track progress on specific areas (security down 20%, complexity still high)

---

## 11. Limitations & Scope (v1)

### Not In CAQI v1:
- Historical trending (can add in v2)
- LLM advice (template strings only, not AI-generated)
- Pre-commit CAQI (too slow at commit time; security gate only)

### In Pre-Commit Gate (Separate System):
- Block hardcoded secrets
- Block SQL injection patterns
- Block unsafe error handling
- Separate from CAQI (real-time, not scored)

---

## 12. Integration Points

### CLI Integration
```bash
python -m scanner ./examples \
  --caqi \
  --caqi-html output/caqi.html \
  --security --quality-score --code-smells --doc-coverage \
  --output output/report.json
```

### Dashboard Hook
```html
<div class="caqi-card">
  <h3>CAQI: 455 — Hazardous</h3>
  <p>Primary pollutant: security (insecure.py)</p>
  <a href="caqi.html">View Gauge →</a>
</div>
```

### GitHub Actions Example
```yaml
- name: Scan with CAQI
  run: python -m scanner . --caqi --caqi-html caqi.html

- name: Check CAQI
  run: |
    CAQI=$(grep "\"score\":" report.json | grep -o "[0-9]*")
    if [ $CAQI -gt 300 ]; then
      echo "CAQI Hazardous ($CAQI). Fix before merging."
      exit 1
    fi
```

---

## 13. Test Coverage for CAQI

### Unit Tests (20+ tests)

```python
# Test each pollutant formula
test_complexity_score_calculation()
test_complexity_score_clamping()
test_security_score_high_and_medium()
test_smells_score_threshold()
test_docs_score_inverted()
test_duplication_score_capping()
test_coupling_score_circular_penalty()

# Test CAQI roll-up
test_caqi_formula_basic()
test_caqi_formula_max_dominance()
test_caqi_clamping_0_to_500()
test_primary_pollutant_identification()

# Test EPA bands
test_band_good_0_50()
test_band_moderate_51_100()
test_band_unhealthy_151_200()
test_band_hazardous_301_500()

# Test output formats
test_caqi_json_shape()
test_caqi_markdown_oneliner()
test_caqi_html_gauge_rendering()
test_caqi_per_file_calculation()

# Test edge cases
test_empty_metrics()
test_all_pollutants_zero()
test_security_blocker_dominates()
```

---

## 14. File Structure

```
caqi.py
├── calculate_complexity_score(avg, max_fn)
├── calculate_security_score(high, medium)
├── calculate_smells_score(count)
├── calculate_docs_score(coverage_ratio)
├── calculate_duplication_score(percent)
├── calculate_coupling_score(imports, circular)
├── calculate_repo_caqi(pollutants_dict)
├── get_caqi_band(score)
├── generate_caqi_json(score, primary, pollutants, per_file)
├── generate_caqi_markdown_line(score, primary, source)
└── render_caqi_gauge_html(score, level, color, advice)

scanner.py (integration)
├── --caqi flag
├── --caqi-html FILE
└── Calls caqi.calculate_repo_caqi() with metrics

tests/test_caqi.py
└── 20+ test cases
```

---

## 15. Real-World Example: The Dashboard Snapshot

```
CAQI Dashboard for examples/

┌─────────────────────────┐
│   CAQI: 280 MODERATE    │
│                         │
│  Primary: complexity    │
│  Source: realistic_app. │
│          py             │
│                         │
│  Pollutants:            │
│  ├─ Complexity: 60      │
│  ├─ Security: 0 ✓       │
│  ├─ Smells: 40          │
│  ├─ Docs: 30            │
│  ├─ Duplication: 0      │
│  └─ Coupling: 0         │
│                         │
│  Status: Fair           │
│  Action: Refactor high- │
│          complexity     │
│          functions      │
└─────────────────────────┘
```

---

## 16. Roadmap (Future Versions)

**v1 (Complete):**
- 6 pollutants
- EPA bands
- Primary pollutant ID
- HTML gauge
- Markdown one-liner
- JSON output

**v2 (Planned):**
- Historical trending (CAQI over time)
- Per-phase CAQI (Bronze vs Silver vs Gold in DLT)
- LLM advice (detailed guidance, not just template)
- Custom thresholds (team-configurable bands)

**v3 (Future):**
- Pre-commit CAQI (fast gate)
- Multi-repo dashboards
- Team score aggregation
- Regression detection (CAQI going UP)

