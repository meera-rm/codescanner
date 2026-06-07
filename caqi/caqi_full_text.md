# CAQI - Code Air Quality Index (Full Text Extract)

## What it is

CAQI turns scanner metrics into one EPA-style health score (0-500) plus a primary pollutant (worst category + source file). It's the headline metric for demos and slides — not a long report.

## Path

| Path | Lens | Output |
|------|------|--------|
| G — Personality | Who is this codebase? | Archetype card |
| H — Inheritance Letter | What must the next dev know? | First-person letter |
| I — CAQI | How bad is the air right now? | 0-500 gauge |

Same scan data, three different stories. CAQI is the instant snapshot.

Demo hook: "Your codebase CAQI is 455 — Hazardous. Primary pollutant: security (insecure.py)."

## Scale (EPA-style bands)

| CAQI | Level | Color | Meaning |
|------|-------|-------|---------|
| 0-50 | Good | #96c480 | Healthy codebase |
| 51-100 | Moderate | #f1f1f0 | Some concerns |
| 101-150 | Unhealthy for Sensitive Groups | #f1f7f8 | New devs will struggle |
| 151-200 | Unhealthy | #ff9999 | Active remediation needed |
| 201-300 | Very Unhealthy | #873f97 | High incident risk |
| 301-500 | Hazardous | #7e9023 | Do not deploy |

## Six pollutants (each 0-100)

| Key | Label | Driven by |
|-----|-------|-----------|
| complexity | Complexity smog | Avg + max cyclomatic complexity |
| security | Security toxins | security_high_count, security_medium_count |
| smells | Smell particulates | code_smell_count |
| docs | Documentation haze | Low coverage_ratio (inverted) |
| duplication | Duplication dust | duplicate_percentage |
| coupling | Coupling ozone | import_count, circular deps |

## Sub-score formulas (in caqi.py)

- Complexity: min(avg * 20 + max_fn * 10, 100)
- Security: min(high * 40 + medium * 20, 100)
- Smells: min(count * 12.5, 100) (8+ smells → 100)
- Docs: (1 - coverage_ratio) * 100
- Duplication: duplicate_percentage (capped at 100)
- Coupling: min(imports * 5, 100) + 50 if circular deps

## Repo CAQI formula

```
CAQI = round(max_pollutant * 3.5 + mean(top_3_pollutants) * 1.5)
clamp to 0-500
primary_pollutant = argmax(pollutants)
```

One severe issue (e.g. secrets at 100) pushes the repo into Hazardous range.

## What you built (files)

| File | Role |
|------|------|
| caqi.py | Engine: pollutants, CAQI, levels, HTML gauge, markdown one-liner |
| scanner.py | CLI wiring: —caqi, —caqi-html; auto-enables security/quality-score/code-smells/doc-coverage |
| tests/test_caqi.py | 20+ unit tests (pollutants, bands, insecure repo, markdown, etc.) |
| plan-code-air-quality.md | Full Q1-Q4 implementation plan |
| output/DEMO_CAQI.md | 60+ 3min demo script |

## CLI

```bash
python -m scanner examples/ \
  --caqi \
  --caqi-html output/caqi.html \
  --security --quality-score --code-smells --doc-coverage \
  --output output/report.json \
  --report-md output/report.md
```

### Flag

| Flag | Effect |
|------|--------|
| --caqi | Adds caqi block to JSON; CAQI line in markdown report |
| --caqi-html FILE | Writes projector-sized HTML gauge |

Auto-enabled when --caqi or --caqi-html: —security, —quality-score, —code-smells, —doc-coverage (so all six pollutants have data).

## JSON output shape

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
    "per_file": [ /* top 10 worst files */ ],
    "health_advice": "Health warning of emergency conditions. Do not deploy."
  }
}
```

## Markdown one-liner (top of report, when --caqi + --report-md):

```
CAQI: 455 — Hazardous / Primary pollutant: security (insecure.py)
```

## Your repo today (live scan on examples/)

| Metric | Value |
|--------|-------|
| Repo CAQI | 455 — Hazardous |
| Primary pollutant | security → examples/insecure.py |
| Worst files | gate_demo/another_secret.py (420), gate_demo/new_secret.py (420), insecure.py (415) |
| Saved artifact | output/caqi.html shows 405 (older scan, before gate_demo/ was included) |
| Pollutant breakdown (current): security pegged at 100; docs also high (100) because many files lack docstrings when —doc-coverage verge runs. | |

## Before/after demo (from DEMO_CAQI.md)

1. Scan with secrets in insecure.py → CAQI ~500 Hazardous, primary = security
2. Remove hardcoded secrets + add error handling
3. Re-scan → CAQI ~287 Very Unhealthy (~213 points), primary shifts to complexity
4. Talking point: security was the blocker; what's left is architectural

## Implementation phases (completed)

| Phase | Deliverable | Status |
|-------|-------------|--------|
| Q1 | RESEARCH.md CAQI section | Done |
| Q2 | caqi.py + —caqi + tests | Done |
| Q3 | —caqi-html gauge + markdown line | Done |
| Q4 | DEMO_CAQI.md + dashboard hook in scanner_dashboard.html | Done |

## Tests (tests/test_caqi.py)

Covers: empty metrics, security dominates insecure repo, docs inversion, complexity scoring, CAQI clamp 0-500, EPA bands, primary pollutant, per-file CAQI, full profile, health advice templates, markdown summary format.

Run: pytest tests/test_caqi.py -v

## Creative suite (all three paths)

```bash
python -m scanner examples/ \
  --caqi --caqi-html output/caqi.html \
  --personality --personality-html output/personality.html \
  --inheritance-letter output/letter.md --inheritance-html output/letter.html \
  --security --quality-score --code-smells --doc-coverage \
  --output output/report.json --report-md output/report.md
```

See output/DEMO_COMBINED.md for the full before/after demo script.

## Also uses CAQI

Onboarding profile (Path J) — onboarding.py accepts caqi_profile for the health snapshot section when you run --onboard

Not in CAQI v1: historical trending, LLM advice (template strings only), pre-commit CAQI (too slow — security gate at commit time).

## Key docs to open

- Design: plan-code-air-quality.md, RESEARCH.md (Path I)
- Demo: output/DEMO_CAQI.md
- Live gauge: output/caqi.html or regenerate with --caqi-html output/caqi.html
- Skill reference: .claude/skills/code-scanner/SKILL.md → Creative suite section
