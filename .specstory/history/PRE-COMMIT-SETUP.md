---
created_at: 2026-06-12T18:16:43Z
title: Pre-Commit-Setup
source: claude-code
project: codescanner
---

# Pre-Commit Hook Setup

## Overview

The code scanner is now integrated as a pre-commit hook. It automatically runs on every commit to catch issues before code is committed.

## Installation & Setup

Pre-commit is already installed. To enable the hook in your repo:

```bash
# Install the pre-commit hooks (one-time setup)
pre-commit install

# That's it! The hook runs automatically on commit
```

## How It Works

When you run `git commit`, the scanner automatically:

1. **Scans all Python, JavaScript, SQL files** in the repo
2. **Reports findings** before the commit completes
3. **Blocks commit if CRITICAL issues found** (exit code 1)
4. **Allows commit if only WARNING/INFO** (exit code 0)

Example output:
```
Multi-Language Code Scanner..............................................Failed
CRITICAL:
  src/app.py:42 [hardcoded_secret] Hardcoded API key
  
ERROR:
  db/migrations.sql:15 [sql_injection_risk] Potential SQL injection detected
  
WARNING:
  src/utils.js:80 [deep_nesting] Code nesting depth 5 exceeds threshold
```

## Using the Hook

### Normal workflow:
```bash
git add myfile.py
git commit -m "Add feature"  # Hook runs automatically, may block if issues found
```

### Fix issues & retry:
```bash
# Edit file to remove hardcoded secret
git add myfile.py
git commit -m "Add feature"  # Should succeed this time
```

### Bypass hook (not recommended):
```bash
git commit -m "Quick fix" --no-verify  # Skip the scanner
```

## Configure Scanner Behavior

Edit `.pre-commit-config.yaml` to:

**Only scan specific languages:**
```yaml
repos:
  - repo: local
    hooks:
      - id: python-scanner
        name: Python Code Scanner
        entry: python3 scanner.py . --python
        language: system
        stages: [pre-commit]
        pass_filenames: false
```

**Exclude directories:**
Edit `scanner.py` and update `ignore_patterns` in the scanner classes:
```python
self.ignore_patterns = ["venv", "node_modules", "migrations/old"]
```

## Manual Scanning

Run the scanner manually without pre-commit:

```bash
# Scan all languages
python3 scanner.py .

# Scan specific language
python3 scanner.py . --python
python3 scanner.py . --js
python3 scanner.py . --sql

# JSON output for parsing
python3 scanner.py . --json
```

## Uninstall Hook

If you want to disable the hook:

```bash
pre-commit uninstall
```

Re-enable anytime with:
```bash
pre-commit install
```

## Troubleshooting

**Hook not running?**
```bash
pre-commit install  # Reinstall
```

**Getting false positives?**
- Check the rule in `scanner_rules.py`, `scanner_js_rules.py`, or `scanner_sql_rules.py`
- Add ignores to `ignore_patterns` in the scanner class
- Use `--no-verify` for legitimate cases, but fix the scanner

**Hook is too slow?**
- Configure it to scan only changed files (future enhancement)
- Or only run on `--python`, `--js`, or `--sql` separately

**Want different settings per developer?**
Create `.pre-commit-config.local.yaml` (git-ignored) with your local config.
