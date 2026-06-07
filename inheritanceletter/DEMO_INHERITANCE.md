# Inheritance Letter - Demo Script

Complete walkthroughs showing how the Inheritance Letter feature works with real code examples.

---

## 60-Second Quick Demo

**The Pitch:**
```
"Code scanners give you metrics. This one gives you a narrative.
The codebase confesses. It tells the truth about itself."
```

**Copy-Paste Commands:**

```bash
# Step 1: Generate letter from examples/
PYTHONPATH=./scanner python scanner/scanner.py examples/ \
  --inheritance-letter \
  --security --quality-score --code-smells --doc-coverage \
  --inheritance-html output/letter.html

# Step 2: Open in browser
open output/letter.html  # macOS
start output/letter.html  # Windows
xdg-open output/letter.html  # Linux

# Step 3: Read the confessions aloud
# "I left a hardcoded_secret in insecure.py (line 6). I'm sorry."
```

**What You See (Red-Themed Letter):**
- Header: "Inheritance Letter - Tone: Apologetic"
- What I'm proud of: error_handling.py, utils.py
- What I'm not proud of: insecure.py (30/100 quality)
- Secrets I've been keeping: 2 confessions (hardcoded_secret, sql_injection)
- Rooms you should avoid first: authenticate_user(), process_request()
- Where to start instead: sample.py, error_handling.py
- How to survive your first week: Security-focused tips
- Sign-off: "Yours apologetically, A codebase that knows too much about itself"

**Expected Output:**
```
✅ Inheritance letter written to: output/letter.html

Letter tone: Apologetic
Generated 6 sections with 2 secrets confessed.
```

---

## 3-Minute Detailed Walkthrough

### Part 1: Understand the Problem (30 sec)

**Context:**
```
Code scanners traditionally output metrics:
  - Quality score: 45/100
  - Security findings: 2 high
  - Code smells: 14
  - Complexity hotspots: authenticate_user (6)

These are facts, but facts don't resonate.
They're boring. Developers forget them in seconds.
```

**The Insight:**
```
What if the CODE told the story?
What if it confessed what it did wrong?
What if it warned about dangerous functions?
What if it guided where to start?

That's the Inheritance Letter.
Not a report. A confession.
```

---

### Part 2: Generate the Letter (30 sec)

**Full Command with Explanation:**

```bash
PYTHONPATH=./scanner python scanner/scanner.py examples/ \
  --inheritance-letter \
  --security \
  --quality-score \
  --code-smells \
  --doc-coverage \
  --inheritance-html output/letter.html
```

**What Each Flag Does:**
- `--inheritance-letter` — Enable letter generation
- `--security` — Scan for security findings (needed for confessions)
- `--quality-score` — Measure overall quality (for tone selection)
- `--code-smells` — Detect bad patterns (for "avoid" section)
- `--doc-coverage` — Track docs (for quality calculation)
- `--inheritance-html output/letter.html` — Write self-contained HTML

**What's Happening Behind the Scenes:**
1. Scanner analyzes all Python files
2. Aggregates metrics (quality, complexity, security, smells)
3. Tone selected based on code health: **Apologetic** (due to security issues)
4. Sections generated:
   - Top 3 files (proud) → best quality
   - Bottom 3 files (not proud) → worst issues
   - Security findings (secrets) → first-person confessions
   - Dangerous functions (avoid) → complexity hotspots
   - Safe entry points (start here) → low complexity + clean
   - Actionable tips (first week) → tone-specific advice
5. HTML rendered with tone-matched colors (red for apologetic)
6. File written to `output/letter.html`

---

### Part 3: View the Letter (45 sec)

**Open in Browser:**
```bash
open output/letter.html  # macOS
```

**Read What You See:**

**Header (Red-Themed):**
```
📬 Inheritance Letter
Tone: Apologetic
```

**Section 1: What I'm Proud Of**
```
✅ error_handling.py
   Quality: 82/100
   Reason: Well-structured error handling

✅ utils.py
   Quality: 75/100
   Reason: Clean utilities, good documentation
```

**Section 2: What I'm Not Proud Of**
```
⚠️ insecure.py
   Quality: 30/100
   Issues: Hardcoded secrets, SQL injection vulnerability

⚠️ realistic_app.py
   Quality: 52/100
   Issues: High complexity in authenticate_user (6)
```

**Section 3: Secrets I've Been Keeping** (Key Section)
```
"I left a hardcoded_secret in insecure.py (line 6). 
I should have used environment variables. I'm sorry."

"I left an SQL injection risk in insecure.py (line 12). 
User input isn't properly escaped. I'm sorry."
```

**Section 4: Rooms You Should Avoid First**
```
🚫 authenticate_user in realistic_app.py
   Complexity: 6 (too high)

🚫 process_request in insecure.py
   Complexity: 5 (refactor needed)

🚫 validate_query in realistic_app.py
   Complexity: 4 (difficult to understand)
```

**Section 5: Where to Start Instead**
```
✅ sample.py
   Complexity: 1 (simple, safe entry point)

✅ error_handling.py
   Complexity: 2 (well-structured, good patterns)
```

**Section 6: How to Survive Your First Week**
```
1. Enable pre-commit security gate to catch secrets before commit
2. Review and fix all hardcoded secrets and injection risks first
3. Schedule security audit with team

Yours apologetically,
A codebase that knows too much about itself
```

**The Magic:**
- Not a table. A story.
- Not metrics. A confession.
- The developer REMEMBERS this letter.
- Not "quality 30" — "I left a secret. I'm sorry."

---

### Part 4: Show Before/After (45 sec)

**Scenario: We Fix the Security Issues**

Step 1: Edit `examples/insecure.py`
```python
# BEFORE (line 6):
SECRET_API_KEY = "sk-abc123def456"  # ❌ Hardcoded

# AFTER:
SECRET_API_KEY = os.getenv("API_KEY")  # ✅ Environment variable

# BEFORE (line 12):
query = f"SELECT * FROM users WHERE id = {user_id}"  # ❌ SQL injection

# AFTER:
query = "SELECT * FROM users WHERE id = ?"  # ✅ Parameterized
```

Step 2: Re-scan the code
```bash
PYTHONPATH=./scanner python scanner/scanner.py examples/ \
  --inheritance-letter \
  --security --quality-score --code-smells --doc-coverage \
  --inheritance-html output/letter-after.html
```

Step 3: Compare the Letters

**BEFORE (output/letter.html):**
```
Tone: Apologetic (🔴 Red Header)
Quality: 45/100
Secrets: 2 confessions
First Week Tips: Focus on security fixes
Sign-off: "Yours apologetically..."
```

**AFTER (output/letter-after.html):**
```
Tone: Cautious (🟡 Amber Header)
Quality: 58/100
Secrets: 0 confessions
First Week Tips: Focus on quality improvements
Sign-off: "Yours cautiously..."
```

**What Changed:**
- Header color shifted: Red → Amber
- Confessions disappeared: "No secrets to keep"
- Tips changed focus: Security → Code quality refactoring
- Overall tone: Urgent → Measured improvement
- Same code structure. Different health. Different TONE.

**The Point:**
```
Developers see and FEEL the difference.

Red letter = "Help, we're broken"
Amber letter = "We're okay, but let's improve"
Green letter = "We're solid, ready to use"

One scanner. Three voices. Same code.
That's what makes it stick.
```

---

### Part 5: Close (30 sec)

**Key Takeaway:**

```
This isn't just another code quality tool.
It's a conversation between the code and its next maintainer.

The code tells the truth:
  "Here's what I'm good at."
  "Here's what I messed up."
  "Here's where it's dangerous."
  "Here's where to start safely."

Not in tables. In confessions.
Not in metrics. In narrative.

Because developers remember stories.
Not spreadsheets.

That's the Inheritance Letter.
```

---

## Three Demo Scenarios

### Scenario 1: Clean Codebase (Confident Tone)

**Command:**
```bash
PYTHONPATH=./scanner python scanner/scanner.py examples/error_handling.py \
  --inheritance-letter \
  --security --quality-score --code-smells --doc-coverage \
  --inheritance-html output/letter-clean.html
```

**Expected Output:**
```
✅ Inheritance letter written to: output/letter-clean.html

Letter tone: Confident
Quality: 82/100
Secrets: None
```

**Letter Characteristics:**
```
Tone: Confident (🟢 Green Header)
What I'm Proud Of: error_handling.py (82/100)
What I'm Not Proud Of: None
Secrets: None (no security issues)
Rooms to Avoid: None (all functions reasonable)
Where to Start: error_handling.py itself
Tips Focus: Learning and contribution
Sign-off: "Yours confidently..."
```

---

### Scenario 2: Security Issues Only (Apologetic Tone)

**Command:**
```bash
PYTHONPATH=./scanner python scanner/scanner.py examples/insecure.py \
  --inheritance-letter \
  --security --quality-score --code-smells --doc-coverage \
  --inheritance-html output/letter-insecure.html
```

**Expected Output:**
```
✅ Inheritance letter written to: output/letter-insecure.html

Letter tone: Apologetic
Quality: 30/100
Secrets: 2
```

**Letter Characteristics:**
```
Tone: Apologetic (🔴 Red Header)
What I'm Proud Of: (minimal, if anything)
What I'm Not Proud Of: insecure.py (multiple issues)
Secrets: 2 major confessions
Rooms to Avoid: process_request, sql_handler
Where to Start: Error handling in neighboring files
Tips Focus: Security-specific actions
Sign-off: "Yours apologetically..."
```

---

### Scenario 3: Complex Codebase (Cautious Tone)

**Command:**
```bash
PYTHONPATH=./scanner python scanner/scanner.py examples/realistic_app.py \
  --inheritance-letter \
  --security --quality-score --code-smells --doc-coverage \
  --inheritance-html output/letter-complex.html
```

**Expected Output:**
```
✅ Inheritance letter written to: output/letter-complex.html

Letter tone: Cautious
Quality: 52/100
Secrets: None but high complexity
```

**Letter Characteristics:**
```
Tone: Cautious (🟡 Amber Header)
What I'm Proud Of: (some good patterns)
What I'm Not Proud Of: Complex functions, moderate smells
Secrets: None (no security)
Rooms to Avoid: authenticate_user (6), process_request (5)
Where to Start: Simpler utilities
Tips Focus: Refactoring strategy
Sign-off: "Yours cautiously..."
```

---

## Integration with Scanner Pipeline

**Full Pipeline Command (All Three Paths):**

```bash
PYTHONPATH=./scanner python scanner/scanner.py examples/ \
  --personality \
  --personality-html output/personality.html \
  --inheritance-letter \
  --inheritance-html output/letter.html \
  --caqi \
  --caqi-html output/caqi.html \
  --security \
  --quality-score \
  --code-smells \
  --doc-coverage \
  --output output/report.json
```

**Output Files Generated:**
- `output/report.json` — JSON with all metrics
- `output/personality.html` — Personality Profiler card
- `output/letter.html` — Inheritance Letter (confessions)
- `output/caqi.html` — CAQI health index

**What This Shows:**
```
Three different lenses. One codebase.

Personality: What archetype is this code?
Inheritance Letter: What truth does it confess?
CAQI: What's the overall health?

Together: A complete picture of code character, health, and narrative.
```

---

## Expected Results Summary

| Scenario | Tone | Color | Quality | Secrets | Tips Focus |
|----------|------|-------|---------|---------|------------|
| insecure.py | Apologetic | 🔴 Red | 30/100 | 2 | Security fixes |
| realistic_app.py | Cautious | 🟡 Amber | 52/100 | 0 | Refactoring |
| error_handling.py | Confident | 🟢 Green | 82/100 | 0 | Learning |
| All examples/ | Apologetic | 🔴 Red | 45/100 | 2 | Security first |

---

## Testing the Demo Yourself

**Quick Test (60 sec):**
1. Run the command from "Part 2"
2. Open output/letter.html in browser
3. Verify it shows 6 sections with red theme

**Full Test (3 min):**
1. Run the command
2. Compare letter to examples/ metrics
3. Edit a file to remove a security issue
4. Re-run and compare tones

**Integration Test:**
1. Run full pipeline command (all three paths)
2. Verify all three HTML files generated
3. Open each one and see different perspectives

---

## Troubleshooting

**Command not found:**
```bash
# Make sure you're in the codescanner directory
cd /Users/meera/Documents/codescanner

# Make sure PYTHONPATH is set
export PYTHONPATH=./scanner
```

**No letter generated:**
```bash
# Verify --inheritance-letter flag is present
# Verify examples/ directory exists with .py files
# Check console output for error messages
```

**HTML file is empty:**
```bash
# Check output/ directory exists
mkdir -p output

# Verify --inheritance-html path is writable
# Check console for "written to" confirmation message
```

---

## What Makes This Different

**Traditional Code Scanners:**
```
ESLint: 45 warnings in 8 files
Sonarqube: Quality Gate FAILED (4.2)
Bandit: 12 security issues
```

**Inheritance Letter:**
```
"I left an API key in insecure.py (line 6). I'm sorry.
You should start with error_handling.py instead.
Yours apologetically,
A codebase that knows too much about itself."
```

The first one is a to-do list.
The second one is a conversation.

Developers remember conversations.

---

**End of Demo Script**

Ready to run? Start with the 60-second quick demo above, then explore the 3-minute detailed walkthrough.
