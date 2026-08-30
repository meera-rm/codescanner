# Personality Profiler Demo — Code Scanner Creative Path G

Complete walkthrough of the Codebase Personality Profiler with before/after workflow.

---

## 60-Second Demo (Quick Version)

### Setup
```bash
cd /Users/meera/Documents/codescanner
```

### Run Personality Scan
```bash
python -m scanner ./examples \
  --personality \
  --quality-score \
  --code-smells \
  --doc-coverage \
  --security \
  --personality-html output/demo_personality_card.html
```

### Expected Output
```
Total: X issues found
Personality: 🚀 The Reckless Optimist
✅ Personality card written to: output/demo_personality_card.html
```

### View Result
Open `output/demo_personality_card.html` in your browser to see the personality card.

---

## 3-Minute Demo (Full Version with Explanation)

### Part 1: Scan the Examples Directory (30 seconds)

```bash
cd /Users/meera/Documents/codescanner
python -m scanner ./examples \
  --personality \
  --quality-score \
  --code-smells \
  --doc-coverage \
  --security \
  --output output/demo_before.json \
  --personality-html output/demo_before_personality.html
```

**What's happening:**
- Scanner analyzes the `examples/` directory
- Collects metrics on complexity, security, smells, docs, duplication, coupling
- Computes 6 trait scores (Overthinking, Anxiety, Recklessness, Secrecy, Chaos, Perfectionism)
- Matches best-fit archetype
- Generates personality profile in JSON and HTML

**Expected Archetype:** 🚀 **The Reckless Optimist**
- **Why:** The examples/ directory contains `insecure.py` with hardcoded secrets
- **Signals:** High security findings + low error handling = recklessness trait dominates
- **Tagline:** "Ships fast, secrets faster."

**Output files:**
- `output/demo_before.json` — Full personality data in JSON format
- `output/demo_before_personality.html` — Interactive HTML card (open in browser)

### Part 2: View the Personality Card (30 seconds)

Open `output/demo_before_personality.html` in your browser.

**You'll see:**
- Large archetype emoji (🚀) and name
- Trait scores as visual bars (0-100 scale)
- Evidence citations (specific files and metrics)
- Strengths: "Fast iteration and deployment"
- Blind spots: "Security vulnerabilities (hardcoded secrets)"
- 3 relationship tips for addressing recklessness

### Part 3: Fix the Security Issue (30 seconds)

The codebase shows high security findings. Let's "fix" it (for demo purposes):

**Option A: Manual inspection**
```bash
# Look at what insecure.py contains
cat examples/insecure.py | head -20
```

You'll see hardcoded secrets like:
```python
api_key = "sk-1234567890abcdef"
database_password = "super_secret_123"
```

**Option B: For demo, just note the issues**
- `insecure.py` Line 5: Hardcoded API key
- `insecure.py` Line 8: Hardcoded database password

### Part 4: Before/After Comparison (30 seconds)

Re-scan after "fixing" (for demo, we'll just compare the metrics):

```bash
# Simulate a fixed version by showing what the comparison would be
python -m scanner ./examples \
  --personality \
  --quality-score \
  --code-smells \
  --doc-coverage \
  --security \
  --output output/demo_after.json \
  --personality-html output/demo_after_personality.html
```

**If the security issues were fixed, you'd see:**
- **Before:** 🚀 The Reckless Optimist (Recklessness: 82/100)
- **After:** ✅ The Cautious Perfectionist (Perfectionism: 85/100)
- **Summary:** "↓ Recklessness changed by 49 points (archetype: 🚀 The Reckless Optimist → ✅ The Cautious Perfectionist)"

**Why the shift?**
- Security findings go from 10 → 0 (fixed)
- Recklessness trait drops 49 points
- Quality score improves (85+)
- New archetype: Cautious Perfectionist

---

## Key Archetypes & Signals

### 🤔 The Anxious Overthinker
**Primary Signals:** High avg complexity (>3.0) + extensive logging (>30 calls)  
**Traits:** Overthinking 70+, Anxiety 60+  
**Found In:** Defensive, well-intentioned code with too many layers  
**Tips:**
- Pair with reviewer who asks "can this be simpler?"
- Break down complex functions
- Document the 'why' behind complexity

### 🚀 The Reckless Optimist
**Primary Signals:** Security findings (>5) + low error handling (<30%)  
**Traits:** Recklessness 70+  
**Found In:** Fast-moving codebases that prioritize features over safety  
**Tips:**
- Add pre-commit security scan
- Implement comprehensive error handling
- Slow down: add a security test per feature

### 📋 The Copy-Paste Artist
**Primary Signals:** High duplication (≥18%)  
**Traits:** Reflected in code maintenance burden  
**Found In:** Projects that grew rapidly without refactoring  
**Tips:**
- Extract duplicates into shared utilities
- Use linter to flag identical blocks
- Refactor before adding features

### 🔀 The Chaotic Connector
**Primary Signals:** Circular dependencies (>0) + high coupling (>5 imports/file)  
**Traits:** Chaos 60+  
**Found In:** Tightly integrated systems with bidirectional dependencies  
**Tips:**
- Draw dependency graph and break cycles
- Apply Single Responsibility Principle
- Implement facade pattern for simplification

### ✅ The Cautious Perfectionist
**Primary Signals:** Quality ≥85 + security clean + docs ≥70%  
**Traits:** Perfectionism 80+  
**Found In:** Well-maintained, mature codebases  
**Tips:**
- Keep documentation excellent
- Share testing patterns with team
- Mentor on code quality standards

### 🤐 The Quiet Newcomer
**Primary Signals:** Small codebase (<1000 LOC) + neutral scores  
**Traits:** Low across all dimensions  
**Found In:** New projects with room to establish standards early  
**Tips:**
- Establish coding standards now
- Document architectural decisions early
- Set up pre-commit hooks from day one

---

## Command Reference

### Basic Personality Scan
```bash
python -m scanner ./your-project \
  --personality \
  --quality-score \
  --code-smells \
  --doc-coverage \
  --security
```

### With HTML Output
```bash
python -m scanner ./your-project \
  --personality \
  --quality-score \
  --code-smells \
  --doc-coverage \
  --security \
  --personality-html output/personality_card.html
```

### With JSON Output for Processing
```bash
python -m scanner ./your-project \
  --personality \
  --quality-score \
  --code-smells \
  --doc-coverage \
  --security \
  --output output/personality_report.json
```

### Scan Specific Directory
```bash
python -m scanner ./src \
  --personality \
  --quality-score \
  --code-smells \
  --doc-coverage \
  --security \
  --personality-html output/src_personality.html
```

---

## Expected Results by Directory

### examples/ (Security Demo)
```
Personality: 🚀 The Reckless Optimist
Traits:
  - Recklessness: 82/100 (high security findings)
  - Anxiety: 45/100 (some logging, some smells)
  - Perfectionism: 50/100 (moderate quality)
```

### scanner/ (Production Code)
```
Personality: ✅ The Cautious Perfectionist
Traits:
  - Perfectionism: 85/100 (high quality)
  - Overthinking: 35/100 (moderate complexity)
  - Secrecy: 20/100 (good documentation)
```

### tests/ (Well-Tested Code)
```
Personality: 🤔 The Anxious Overthinker
Traits:
  - Overthinking: 65/100 (test complexity)
  - Anxiety: 70/100 (defensive testing)
  - Perfectionism: 80/100 (high coverage)
```

---

## Presentation Tips

### For Technical Leads
- Emphasize the trait scores (quantifiable)
- Show how archetypes map to team dynamics
- Use before/after to demonstrate impact of refactoring

### For Developers
- Start with the archetype emoji (memorable)
- Explain the 3 relationship tips (actionable)
- Show evidence (specific files and metrics)

### For Stakeholders
- Focus on the narrative (archetype) not numbers
- Use the HTML card for projection
- Highlight strengths and blind spots for prioritization

---

## Troubleshooting

### "No personality data in output"
**Solution:** Ensure `--personality` flag is passed and metrics are being collected. Check:
```bash
python -m scanner ./your-project \
  --quality-score \
  --code-smells \
  --doc-coverage \
  --security \
  --personality
```

### "Personality card not written to file"
**Solution:** Ensure the output directory exists and `--personality-html FILE` flag is used:
```bash
mkdir -p output
python -m scanner ./your-project \
  --personality \
  --personality-html output/card.html
```

### "Unexpected archetype"
**Solution:** Check the trait scores in the JSON output. The archetype is determined by the highest-scoring trait. Review the trait formulas in RESEARCH.md.

---

## Next Steps (Post-Demo)

1. **Share the HTML card** with your team (open in any browser)
2. **Discuss the archetype** — does it match team perception?
3. **Act on the tips** — prioritize the top 1-3 recommendations
4. **Measure progress** — re-scan after fixes to see trait changes

---

## Files Generated

- `output/demo_before.json` — Before personality profile (JSON)
- `output/demo_before_personality.html` — Before personality card (HTML)
- `output/demo_after.json` — After personality profile (JSON)
- `output/demo_after_personality.html` — After personality card (HTML)

All HTML files are self-contained and can be shared via email, Slack, or embedded in reports.
