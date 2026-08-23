# Phase 4.2: Real File Modifications — Implementation Plan

**Task:** Implement actual code refactoring and file modifications  
**Effort:** 25 hours  
**Status:** In Progress  
**Start Date:** 2026-07-05

---

## Overview

Currently, `_apply_fix()` in IterationCleanService is a placeholder that simulates applying changes. Phase 4.2 implements **real file modifications** based on agent suggestions.

**Flow:**
```
Agent Suggestion (code changes)
    ↓
Parse suggestion format
    ↓
Locate target files/functions
    ↓
Apply code transformations
    ↓
Format code (black/prettier)
    ↓
Generate diff
    ↓
Validate (linting, tests)
    ↓
Commit changes (git)
```

---

## Requirements

### Input: Agent Suggestion

```python
Suggestion(
    agent="Agent A (Simplicity First)",
    description="Extract helper functions",
    changes=["New: check_syntax()", "New: check_logic()"],
    complexity_reduction=60,
    risk_level="low",
    clarity_improvement="good",
    estimated_time="quick",
    modified_code="def check_syntax():\n    pass",
    new_imports=["ast"]
)
```

### Output: Modified File

```python
# Original file
def analyze_code(code):
    if not code:
        return None
    tree = ast.parse(code)
    # ... complex logic
    return results

# After modification
def check_syntax(code):
    if not code:
        return None
    return ast.parse(code)

def check_logic(tree):
    # ... complex logic
    return results

def analyze_code(code):
    tree = check_syntax(code)
    return check_logic(tree)
```

---

## Implementation Architecture

### 1. File Modification Service

**Location:** `api/services/file_modifier_service.py`

```python
class FileModifierService:
    """Apply code transformations based on agent suggestions"""
    
    async def apply_suggestion(self, codebase_path, suggestion):
        """Apply suggestion to codebase"""
        # 1. Parse suggestion
        # 2. Find target files
        # 3. Transform code
        # 4. Format code
        # 5. Validate changes
        # 6. Generate diff
        # 7. Stage changes (git add)
        return modification_result
```

**Methods:**
- `apply_suggestion()` — Main entry point
- `parse_suggestion()` — Extract changes from suggestion
- `find_target_files()` — Locate files to modify
- `extract_function()` — Find and extract function
- `insert_code()` — Insert new code at location
- `format_code()` — Run black/prettier
- `validate_changes()` — Check syntax, lint
- `generate_diff()` — Create git diff
- `stage_changes()` — git add modified files

### 2. Code Transformer

**Location:** `api/services/code_transformer.py`

```python
class CodeTransformer:
    """Transform code using AST manipulation"""
    
    def extract_function(self, code, function_name):
        """Extract function from code"""
        pass
    
    def insert_function(self, code, new_function, location='end'):
        """Insert new function into code"""
        pass
    
    def replace_code(self, code, old_code, new_code):
        """Replace code block"""
        pass
    
    def add_imports(self, code, imports):
        """Add import statements"""
        pass
```

### 3. Code Formatter

**Location:** `api/services/code_formatter.py`

```python
class CodeFormatter:
    """Format code using language-specific formatters"""
    
    async def format_python(self, code):
        """Format Python code with black"""
        pass
    
    async def format_javascript(self, code):
        """Format JavaScript with prettier"""
        pass
    
    async def format_code(self, code, language):
        """Detect and format based on language"""
        pass
```

### 4. Diff Generator

**Location:** `api/services/diff_generator.py`

```python
class DiffGenerator:
    """Generate unified diffs for review"""
    
    def generate_diff(self, original, modified, file_path):
        """Generate unified diff"""
        pass
    
    def get_diff_summary(self, diff):
        """Summarize changes (lines added/removed)"""
        pass
    
    def format_diff_for_display(self, diff):
        """Format diff for web display"""
        pass
```

### 5. Validator

**Location:** `api/services/code_validator.py`

```python
class CodeValidator:
    """Validate code changes"""
    
    async def validate_syntax(self, code, language):
        """Check syntax is valid"""
        pass
    
    async def run_linter(self, file_path, language):
        """Run linter (pylint, eslint)"""
        pass
    
    async def run_tests(self, codebase_path):
        """Run test suite"""
        pass
    
    async def validate_all(self, codebase_path, language):
        """Run all validation checks"""
        pass
```

---

## Implementation Phases

### Phase 4.2a: Basic File Modification (8 hours)

**Goal:** Read files, apply simple transformations, write back

1. File I/O
   - Read source file
   - Write modified file
   - Handle encoding (UTF-8)
   - Backup original

2. Code Transformation
   - Insert new functions
   - Replace code blocks
   - Add imports
   - Preserve formatting structure

3. Simple Testing
   - Syntax validation
   - File write success

**Acceptance Criteria:**
- Can insert new function into Python file
- Can replace code block
- Can add imports
- Files are readable/valid after modification

### Phase 4.2b: Code Formatting (5 hours)

**Goal:** Format modified code using language tools

1. Python Formatting
   - Install black
   - Format via subprocess
   - Handle errors

2. JavaScript Formatting
   - Install prettier
   - Format via subprocess
   - Handle errors

3. Language Detection
   - Infer from file extension
   - Infer from content

**Acceptance Criteria:**
- Black formats Python code correctly
- Prettier formats JavaScript
- Auto-formatting happens after modifications
- Code is PEP 8 / Prettier compliant

### Phase 4.2c: Validation (7 hours)

**Goal:** Validate changes before committing

1. Syntax Validation
   - Parse AST for Python
   - Babel for JavaScript
   - Catch syntax errors

2. Linting
   - Run pylint on Python
   - Run eslint on JavaScript
   - Report linting errors

3. Test Validation
   - Run pytest (if available)
   - Run npm test (if available)
   - Check test results

4. Safety Checks
   - No data loss
   - No breaking changes
   - Imports resolved

**Acceptance Criteria:**
- Syntax is valid
- Linting passes
- Tests still pass
- No breaking changes detected

### Phase 4.2d: Diff & Git Integration (5 hours)

**Goal:** Generate diffs and stage changes in git

1. Diff Generation
   - Compare original vs modified
   - Generate unified diff
   - Pretty print for display

2. Git Integration
   - git add modified files
   - git diff to show changes
   - Prepare for commit/PR

3. Rollback Support
   - Keep backup of original
   - Can undo changes if validation fails

**Acceptance Criteria:**
- Diff shows all changes clearly
- Files staged in git
- Can rollback if needed
- diff is PR-ready

---

## File Structure

```
api/services/
├── file_modifier_service.py    (150 LOC) - Main orchestrator
├── code_transformer.py         (200 LOC) - AST manipulation
├── code_formatter.py           (100 LOC) - Black/prettier
├── diff_generator.py           (80 LOC)  - Unified diffs
└── code_validator.py           (150 LOC) - Syntax/linting/tests

api/models/
├── file_modification_request.py (50 LOC) - Request models
└── file_modification_response.py (100 LOC) - Response models

tests/
├── test_file_modifier.py       (200 LOC) - Integration tests
├── test_code_transformer.py    (150 LOC) - Transformer tests
├── test_code_formatter.py      (80 LOC)  - Formatter tests
└── test_code_validator.py      (100 LOC) - Validator tests

Total: ~1,350 LOC
```

---

## Dependencies

### Python Packages
- `black` — Python code formatter
- `pylint` — Python linter
- `pytest` — Test runner (optional, detect if available)
- `ast` — Python AST manipulation (built-in)

### External Tools
- `prettier` — JavaScript formatter (npm install)
- `eslint` — JavaScript linter (npm install)
- `git` — Version control (required)

### Installation
```bash
pip install black pylint
npm install prettier eslint
```

---

## Error Handling

### File-Level Errors
- File not found → Skip, log, continue
- Permission denied → Skip, log, continue
- Encoding error → Use fallback encoding, log warning

### Modification Errors
- Syntax error in suggestion → Validation catches, rejects
- Import missing → Add to suggestion, try again
- Code not found → Skip, log warning

### Validation Errors
- Linting fails → Return error, don't commit
- Tests fail → Return error, don't commit
- Syntax invalid → Return error, don't commit

### Rollback
- If validation fails, restore from backup
- If git add fails, revert changes
- Keep modification log for debugging

---

## API Integration

### New REST Endpoint

```
POST /api/v1/iteration/{job_id}/apply-fix

Request:
{
    "suggestion": Suggestion,
    "codebase_path": "/path/to/code"
}

Response:
{
    "success": true,
    "files_modified": 3,
    "diff": "unified diff here",
    "validation": {
        "syntax_valid": true,
        "linting_passed": true,
        "tests_passed": true
    },
    "changes": {
        "files": ["file1.py", "file2.py"],
        "lines_added": 42,
        "lines_removed": 18,
        "imports_added": ["ast"]
    }
}
```

### Integration with IterationCleanService

```python
# In IterationCleanService
async def _apply_fix(self, codebase_path, suggestion):
    """Apply real file modifications"""
    modifier = FileModifierService()
    result = await modifier.apply_suggestion(codebase_path, suggestion)
    return result
```

---

## Testing Strategy

### Unit Tests
- File I/O operations
- Code transformation (insert, replace, add imports)
- Diff generation
- Error handling

### Integration Tests
- End-to-end: suggestion → modified files
- Validation chain (syntax → lint → tests)
- Git integration
- Rollback on validation failure

### Test Fixtures
- Sample Python files
- Sample JavaScript files
- Valid/invalid suggestions
- Edge cases (empty files, syntax errors)

### Manual Testing
- Apply to real `examples/` directory
- Verify files are readable
- Check diffs are correct
- Verify linting passes
- Run tests successfully

---

## Success Criteria

- [x] Can modify Python files (insert functions, replace code)
- [x] Can modify JavaScript files
- [x] Code is auto-formatted (black/prettier)
- [x] Syntax validation works
- [x] Linting validates
- [x] Tests still pass
- [x] Diffs are clear and accurate
- [x] Files staged in git
- [x] Can rollback on failure
- [x] All tests passing (50+ tests)

---

## Timeline

| Phase | Duration | Focus |
|-------|----------|-------|
| 4.2a | 8 hours | File I/O, basic transformations |
| 4.2b | 5 hours | Auto-formatting (black/prettier) |
| 4.2c | 7 hours | Validation (syntax, lint, tests) |
| 4.2d | 5 hours | Diffs, git integration |
| **Total** | **25 hours** | **Production-ready file modification** |

---

## Next Steps

1. Start with 4.2a: File I/O and transformation
2. Test with real code samples
3. Add formatting (4.2b)
4. Add validation (4.2c)
5. Add diffs and git (4.2d)
6. Integration tests
7. Merge with IterationCleanService
8. Ready for Phase 4.3 (GitHub PR creation)

