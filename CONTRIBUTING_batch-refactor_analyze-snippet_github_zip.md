# CodeScanner Developer Guide

A hands-on guide for developers working on CodeScanner Phase 3.

---

## Getting Started

### 1. Clone & Setup (5 minutes)

```bash
# Clone repository
git clone <repo-url>
cd codescanner

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
cd frontend
npm install
cd ..

# Verify setup
python -m pytest tests/ -v 2>/dev/null | head -5
npm run build --prefix frontend 2>&1 | tail -3
```

### 2. Start Development Servers (2 terminals)

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
python -m uvicorn api.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Access at `http://localhost:3002`

---

## Architecture Quick Reference

### Frontend Structure

CodeScanner.tsx is the main component (~3500 lines) with:
- useUploadManager: file input + language detection
- useRefactorBatch: batch refactoring orchestration
- useLiveCodeAnalysis: snippet analysis + caching
- useRecentPaths: localStorage history

Components:
- DiffViewer: character-level diff visualization
- FunctionSelector: multi-select UI for batch refactoring
- LiveCodeEditor: code input with language selector
- LiveMetricsPanel: visual metrics with gauges

Tabs: Overview, Complexity, Files, Refactor, Live

### Backend Structure

FastAPI Routes under /api/v1/scan:
- POST /sync: local directory scan
- POST /batch-refactor: batch refactoring
- POST /analyze-snippet: live code analysis
- POST /scan-github: GitHub repo download + scan
- POST /scan-zip: ZIP file upload + scan

Services:
- ScannerService: main analyzer
- RefactoringService: AI-powered code fixes
- RemoteScannerService: GitHub/ZIP handling

Utilities:
- remote_handler.py: download, extract, cleanup

Scanners:
- PythonScanner, JavaScriptScanner, SQLScanner

---

## Common Development Tasks

### Add a Feature

1. Backend: Create service method in api/services/
2. Route: Add endpoint in api/routes/scanner.py
3. Frontend: Create hook/component in frontend/src/
4. Test: Write tests for both backend and frontend
5. Document: Update README_PHASE_3.md

### Fix a Bug

1. Reproduce: Write test that fails
2. Debug: Use pdb (Python) or browser DevTools (JS)
3. Fix: Make minimal changes to resolve issue
4. Test: Verify test now passes
5. Commit: Follow git workflow below

### Optimize Performance

Use profiling tools:
- Python: cProfile, memory_profiler
- JavaScript: Chrome DevTools, performance API

---

## Testing Guide

### Run Tests

```bash
pytest tests/ -v                          # All tests
pytest tests/test_batch_refactor.py -v   # Specific file
pytest tests/ --cov=api                   # With coverage
```

### Write a Test

```python
def test_my_feature():
    """Test description."""
    service = MyService()
    result = service.do_something()
    assert result is not None
```

---

## Code Style

### Python
- Follow PEP 8
- Type hints required
- Docstrings for functions
- Max 100 chars per line

### TypeScript/React
- Props typed with interfaces
- Functional components + hooks only
- Use useCallback for handlers
- ESLint + Prettier format

---

## Git Workflow

### Branch Names
```
feature/phase-3.4-batch-refactoring
bugfix/live-analysis-cache-issue
docs/api-documentation
```

### Commit Format
```
[Phase X.Y] Type: Brief description

Detailed explanation
- Change 1
- Change 2

Closes #123
```

### Push PR
```bash
git checkout -b feature/my-feature
git add .
git commit -m "[Phase 3.6] Feature: Add GitHub support"
git push origin feature/my-feature
gh pr create --title "..." --body "..."
```

---

## Debugging

### Backend
```python
import pdb; pdb.set_trace()  # Breakpoint
print(f"DEBUG: {variable}")  # Logging
```

### Frontend
```javascript
console.log('state:', state);  // Browser console
// React DevTools Chrome extension for component tree
// Network tab in DevTools for API calls
```

---

## Common Issues

**Port already in use:** 
```bash
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

**Module not found:**
```bash
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

**TypeScript errors:**
```bash
cd frontend && npx tsc --noEmit
npx prettier --write src/ && npx eslint src/ --fix
```

---

## Performance Targets

| Metric | Target |
|--------|--------|
| Scan (1000 LOC) | < 1s |
| Batch refactor (5 funcs) | < 3s |
| Live analysis | < 100ms |
| GitHub scan (small) | < 20s |
| Bundle size | < 100KB gzip |

---

## Resources

- README_PHASE_3.md - Full documentation
- API_ENDPOINTS.md - API reference
- FastAPI docs: https://fastapi.tiangolo.com/
- React docs: https://react.dev/

---

Happy coding! 🚀
