---
created_at: 2026-06-12T18:16:43Z
title: Readme 3 Batch-Refactor Analyze-Snippet Github Zip
source: claude-code
project: codescanner
---

# CodeScanner Phase 3 - Complete Documentation

**Version:** 3.6  
**Status:** Production Ready  
**Last Updated:** June 2026

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture](#architecture)
3. [Features](#features)
4. [API Documentation](#api-documentation)
5. [Installation & Setup](#installation--setup)
6. [Configuration](#configuration)
7. [Development Guide](#development-guide)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)

---

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### Installation

```bash
# Clone repository
git clone <repo-url>
cd codescanner

# Backend setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
npm run dev

# Start backend
cd ..
python -m uvicorn api.main:app --reload --port 8000

# Access at http://localhost:3002
```

### First Scan

1. Open http://localhost:3002
2. Click "Browse" and select a Python/JavaScript folder
3. Click "▶ Scan" button
4. View results in Overview, Complexity, Refactor tabs
5. Try "💻 Live" tab to analyze code snippets
6. Export results in JSON/HTML/Markdown/CSV/PDF

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ CodeScanner.tsx (Main Component ~3500 lines)         │   │
│  │  ├─ Recent Paths (Phase 3.1)                         │   │
│  │  ├─ Advanced Tabs (Phase 3.2)                        │   │
│  │  ├─ Batch Refactoring UI (Phase 3.4)                 │   │
│  │  ├─ Live Editor Tab (Phase 3.5)                      │   │
│  │  └─ Export Buttons (Phase 3.3)                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Components:                                                 │
│  ├─ DiffViewer (character-level diffs)                      │
│  ├─ FunctionSelector (multi-select UI)                      │
│  ├─ LiveCodeEditor (code input)                             │
│  └─ LiveMetricsPanel (visual gauges)                        │
│                                                              │
│  Hooks:                                                      │
│  ├─ useUploadManager (file upload + GitHub/ZIP detection)   │
│  ├─ useRefactorBatch (batch refactoring orchestration)      │
│  ├─ useLiveCodeAnalysis (debounce + cache)                  │
│  └─ useRecentPaths (localStorage persistence)               │
└─────────────────────────────────────────────────────────────┘
                           ↕ (HTTP)
┌─────────────────────────────────────────────────────────────┐
│                        Backend (FastAPI)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Router: /api/v1/scan                                 │   │
│  │  ├─ POST /sync (local directory scan)                │   │
│  │  ├─ POST /batch-refactor (batch refactoring)         │   │
│  │  ├─ GET /batch-refactor/{id}/status                  │   │
│  │  ├─ POST /analyze-snippet (live analysis)            │   │
│  │  ├─ POST /scan-github (GitHub repo)                  │   │
│  │  ├─ POST /scan-zip (ZIP file)                        │   │
│  │  └─ GET /github-info (pre-flight check)              │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Services:                                                   │
│  ├─ ScannerService (code analysis)                          │
│  ├─ RefactoringService (generate fixes)                     │
│  └─ RemoteScannerService (GitHub/ZIP handling)              │
│                                                              │
│  Utilities:                                                  │
│  └─ remote_handler.py (download, extract, cleanup)          │
│                                                              │
│  Scanners:                                                   │
│  ├─ PythonScanner (AST-based analysis)                      │
│  ├─ JavaScriptScanner (token-based analysis)                │
│  └─ SQLScanner (query analysis)                             │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Action
    ↓
Upload Manager (detect input type)
    ├─→ GitHub URL detected
    │    ├─ Parse owner/repo
    │    ├─ Validate URL
    │    └─ Call POST /scan-github
    │
    ├─→ ZIP file detected
    │    ├─ Validate file type
    │    └─ Call POST /scan-zip
    │
    └─→ Local folder selected
         └─ Call POST /sync
    ↓
Remote Handler (if GitHub/ZIP)
    ├─ Download from GitHub API
    ├─ Extract to temp directory
    └─ Pass to scanner
    ↓
Scanner Service
    ├─ Detect language
    ├─ Scan files
    ├─ Extract metrics
    └─ Return findings
    ↓
Results
    ├─→ Complexity Tab (display metrics)
    ├─→ Refactor Tab (enable refactoring)
    ├─→ Export (5 formats)
    └─→ Recent Paths (store in localStorage)
```

---

## Features

### Phase 3.1: Recent Paths UI

**What it does:** Stores and displays recently scanned projects for quick re-access.

**Location:** `frontend/src/hooks/useRecentPaths.ts`

**Features:**
- Stores up to 10 recent paths
- Time-ago formatting ("5m ago", "2h ago", "3d ago")
- Full path + relative path storage
- One-click rescan
- localStorage persistence
- Clear all button

**Usage:**
```typescript
const { recentPaths, addRecentPath } = useRecentPaths();

// Automatically added on every scan
addRecentPath({
  path: '/Users/meera/Documents/project',
  name: 'project',
  language: 'python',
  relative: 'Documents/project',
  timestamp: Date.now()
});

// Display in UI
recentPaths.map(path => (
  <div onClick={() => rescan(path.path)}>
    {path.name} • {getTimeAgo(path.timestamp)}
  </div>
))
```

---

### Phase 3.2: Advanced Tab Features

**What it does:** Provides detailed complexity metrics and function analysis.

**Features:**
- Summary cards (High/Medium/Low complexity counts)
- Function-level complexity metrics
- Severity indicators (🔴 High, 🟡 Medium, 🟢 Low)
- Sorted function list by complexity
- Visual complexity bars

**Display:**
```
High Complexity Functions: 3
Medium Complexity Functions: 5
Low Complexity Functions: 12

Functions:
1. complex_function() - Complexity: 15 (🔴 High)
2. process_data() - Complexity: 8 (🟡 Medium)
3. simple_function() - Complexity: 2 (🟢 Low)
```

---

### Phase 3.3: Export Functionality

**What it does:** Export scan results in multiple formats.

**Location:** `frontend/src/pages/CodeScanner.tsx` (lines 278-467)

**Supported Formats:**

1. **JSON** - Full structured data with all findings
   ```json
   {
     "scan_id": "scan_abc123",
     "status": "completed",
     "findings": [...],
     "metrics": {...},
     "timestamp": "2026-06-11T..."
   }
   ```

2. **HTML** - Professional report with styling
   - Gradient header (purple)
   - Metrics grid (6 cards)
   - Files table with sorting
   - Color-coded issues
   - Print-friendly

3. **Markdown** - GitHub-compatible format
   - Title and metadata
   - Metrics table
   - Files list
   - Issues breakdown

4. **CSV** - Spreadsheet-ready
   - Headers: File, Type, Severity, Line, Message
   - Proper escaping for quoted content
   - Excel/Google Sheets compatible

5. **PDF** - Print and archive
   - Same layout as HTML
   - Professional formatting

**Usage:**
```typescript
// Click export button (topbar)
// Select format (JSON, HTML, MD, CSV, PDF)
// File downloads automatically

// Behind the scenes:
handleExport('html') 
  → generateHTMLReport() 
  → fetch download
  → client.downloadFile(content, 'report.html')
```

---

### Phase 3.4: Batch Refactoring

**What it does:** Refactor multiple functions at once with AI suggestions.

**Components:**
- `DiffViewer.tsx` - Character-level diff with color highlighting
- `FunctionSelector.tsx` - Multi-select UI with category filters
- `useRefactorBatch.ts` - Batch orchestration hook

**Features:**
- Select 1-50+ functions at once
- Category filters (General, Complexity, Security, Style)
- Progress tracking (0-100%)
- View refactored suggestions before applying
- Reject individual functions
- Apply all at once
- Undo last changes with history tracking

**Workflow:**

```
1. Scan project → Complexity tab shows functions

2. Click "🔄 Batch" button → Enters batch mode

3. Select functions
   ☑ calculate_complexity() - Complexity: 10
   ☑ nested_conditions() - Complexity: 9
   ☐ simple_function() - Complexity: 1

4. Select category: "Complexity"

5. Click "🚀 Start Refactoring (2)"
   → API: POST /batch-refactor
   → Progress: 0% → 50% → 100%

6. Review results
   Original: def calculate_sum(numbers):
               result = 0
               for num in numbers:
                 result += num
   
   Refactored: def calculate_sum(numbers):
                return sum(numbers)

7. Click "✅ Apply All Changes"
   → Files updated with refactored code
   → "↩️ Undo (2)" button appears

8. If needed, click undo to revert
```

**API Endpoints:**

```
POST /api/v1/scan/batch-refactor
Request:
{
  "functions": [
    {
      "name": "calculate_sum()",
      "file": "/path/to/file.py",
      "line": 1,
      "code": "def calculate_sum(numbers): ...",
      "complexity": 6,
      "severity": "medium"
    }
  ],
  "category": "complexity"
}

Response:
{
  "batch_id": "batch_abc123",
  "status": "completed",
  "total_functions": 2,
  "processed": 2,
  "results": [
    {
      "function_name": "calculate_sum()",
      "status": "completed",
      "refactored_code": "return sum(numbers)",
      "explanation": "Simplified to built-in function",
      "risk_level": "low"
    }
  ]
}
```

---

### Phase 3.5: Real-time Live Analysis

**What it does:** Analyze code snippets in real-time as you type.

**Components:**
- `LiveCodeEditor.tsx` - Code input with language selector
- `LiveMetricsPanel.tsx` - Visual metrics with gauges
- `useLiveCodeAnalysis.ts` - Debounce + caching hook

**Features:**
- 300ms debounced analysis (no server spam)
- In-memory cache (50 max entries, 5-min TTL)
- Multi-language support (Python, JavaScript, SQL)
- Circular gauge metrics:
  - Quality Score (0-100)
  - Complexity (0-10)
  - Security Issues (count)
- Code length counter
- Issue list with line numbers
- Automatic analysis (no button click needed)

**Workflow:**

```
1. Open "💻 Live" tab

2. Select language: Python ↓

3. Paste code:
   def complex_fn(data):
       if len(data) > 0:
           for item in data:
               if isinstance(item, int):
                   if item > 0:
                       result += item

4. Wait 300ms → Analysis fires automatically

5. See results:
   ⭐ Quality: 72/100
   📈 Complexity: 5 issues
   🔒 Security: 1 issue
   
   Code Length: 142 chars
   Total Issues: 6
   
   Top Issues:
   • Line 3: High complexity - Too many nested conditions
   • Line 5: Medium complexity - Deep nesting detected

6. Change language → Re-analyzes instantly

7. Clear cache when needed → Dropdown option
```

**API Endpoint:**

```
POST /api/v1/scan/analyze-snippet
Request:
{
  "code": "def fn():\n    pass",
  "language": "python"
}

Response:
{
  "code_length": 17,
  "quality_score": 95,
  "complexity": {
    "high": 0,
    "medium": 0,
    "low": 0
  },
  "security_issues": 0,
  "total_issues": 0,
  "findings": []
}
```

---

### Phase 3.6: GitHub/ZIP Backend

**What it does:** Download GitHub repos and scan ZIP files.

**Components:**
- `api/utils/remote_handler.py` - Download/extract utilities
- `api/services/remote_scanner_service.py` - Orchestration
- New API endpoints (scan-github, scan-zip, github-info)

**Features:**
- GitHub repo download (via API zipball, no git CLI needed)
- ZIP file extraction
- Automatic temp file management
- Multi-format GitHub URL support
- Size limits (500MB default)
- Timeout protection (60s default)
- Pre-flight validation (check size before download)
- Comprehensive error handling

**Supported GitHub URL Formats:**

```
✓ https://github.com/owner/repo
✓ github.com/owner/repo
✓ https://github.com/owner/repo/tree/branch
✓ git@github.com:owner/repo.git
✓ https://github.com/owner/repo/tree/develop
```

**Workflow:**

```
GITHUB:
1. User pastes: https://github.com/django/django
2. Frontend calls: GET /github-info?github_url=...
3. Backend validates and returns size/language
4. User clicks scan
5. Frontend calls: POST /scan-github
6. Backend:
   - Downloads ZIP from GitHub API
   - Extracts to /tmp/codescanner_{job_id}/
   - Scans with existing scanner
   - Returns results
7. Temp files cleaned after 1 hour

ZIP:
1. User uploads: myproject.zip
2. Frontend validates (is_zipfile)
3. Frontend calls: POST /scan-zip (multipart/form-data)
4. Backend:
   - Saves uploaded file temporarily
   - Extracts to /tmp/codescanner_{job_id}/
   - Scans with existing scanner
   - Returns results
5. Temp files cleaned after 1 hour
```

**API Endpoints:**

```
# Get repo info (pre-flight check)
GET /api/v1/scan/github-info
Query: github_url, branch (optional)
Response:
{
  "repo": "django",
  "description": "The Web framework...",
  "size_mb": 273.9,
  "language": "Python",
  "stars": 87814,
  "branch": "main",
  "scannable": true
}

# Scan GitHub repo
POST /api/v1/scan/scan-github
Request:
{
  "github_url": "https://github.com/django/django",
  "branch": "main",
  "language": "python"
}
Response: ScanResponse (same format as /sync)

# Scan ZIP file
POST /api/v1/scan/scan-zip
Request: multipart/form-data
  file: <ZIP file>
  language: python (optional)
Response: ScanResponse (same format as /sync)

# Manual cleanup
DELETE /api/v1/scan/cleanup/{job_id}
Response: { "status": "success" }
```

---

## API Documentation

### Base URL
```
http://localhost:8000/api/v1/scan
```

### Authentication
None (add in Phase 4)

### Response Format

All endpoints return consistent format:

```json
{
  "job_id": "scan_abc123",
  "status": "completed|error|processing",
  "findings": [
    {
      "file": "/path/to/file.py",
      "line": 42,
      "column": 8,
      "type": "complexity_high",
      "message": "Function too complex",
      "severity": "high",
      "language": "python"
    }
  ],
  "metrics": {
    "quality_score": 75.5,
    "complexity": {
      "high_complexity_functions": 3,
      "total_issues": 8,
      "rating": "high"
    }
  },
  "scanned_files": [
    {
      "name": "main.py",
      "path": "/path/to/main.py",
      "language": "python",
      "loc": 245
    }
  ],
  "function_metrics": [
    {
      "name": "process_data()",
      "file": "/path/to/file.py",
      "line": 10,
      "complexity": 8,
      "severity": "medium"
    }
  ]
}
```

### Error Responses

```json
{
  "status": "error",
  "error": "Description of error",
  "details": "Optional detailed message"
}
```

**Common Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `413 Payload Too Large` - File/repo too large
- `422 Unprocessable Entity` - Processing error
- `504 Gateway Timeout` - Download/processing timeout
- `500 Internal Server Error` - Unexpected error

---

## Installation & Setup

### Prerequisites

**System Requirements:**
- Python 3.8 or higher
- Node.js 16 or higher
- 500MB free disk space (for temp files)
- 2GB RAM minimum

**Dependencies:**

Backend:
```
fastapi==0.104.0
uvicorn==0.24.0
python-multipart==0.0.6
requests==2.31.0
```

Frontend:
```
react==18.2.0
typescript==5.2.0
vite==5.0.0
```

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional)
export GITHUB_SIZE_LIMIT_MB=500
export ZIP_SIZE_LIMIT_MB=500
export GITHUB_TIMEOUT_SECONDS=60

# Run server
python -m uvicorn api.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### Verification

```bash
# Backend is running
curl http://localhost:8000/api/v1/scan/

# Frontend is running
curl http://localhost:3002
```

---

## Configuration

### Environment Variables

```bash
# Backend Configuration
GITHUB_SIZE_LIMIT_MB=500        # Max GitHub repo size (MB)
ZIP_SIZE_LIMIT_MB=500           # Max ZIP file size (MB)
GITHUB_TIMEOUT_SECONDS=60       # GitHub download timeout
TEMP_CLEANUP_HOURS=24           # Auto-cleanup interval

# Server Configuration
PYTHON_ENV=development          # development|production
DEBUG=true                       # Enable debug mode
LOG_LEVEL=INFO                   # Logging level
```

### Frontend Configuration

Edit `frontend/src/config.ts`:

```typescript
export const CONFIG = {
  API_BASE_URL: 'http://localhost:8000/api/v1',
  DEBOUNCE_DELAY_MS: 300,        // Live analysis debounce
  CACHE_TTL_MINUTES: 5,           // Cache time-to-live
  MAX_CACHE_ENTRIES: 50,          // Max in-memory cache
  THEME: 'light',                 // light|dark
  MAX_RECENT_PATHS: 10,           // Recent paths history size
};
```

---

## Development Guide

### Project Structure

```
codescanner/
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── CodeScanner.tsx (main ~3500 lines)
│   │   ├── components/
│   │   │   ├── DiffViewer.tsx (Phase 3.4)
│   │   │   ├── FunctionSelector.tsx (Phase 3.4)
│   │   │   ├── LiveCodeEditor.tsx (Phase 3.5)
│   │   │   └── LiveMetricsPanel.tsx (Phase 3.5)
│   │   ├── hooks/
│   │   │   ├── useUploadManager.ts
│   │   │   ├── useRefactorBatch.ts (Phase 3.4)
│   │   │   ├── useLiveCodeAnalysis.ts (Phase 3.5)
│   │   │   └── useRecentPaths.ts (Phase 3.1)
│   │   └── config.ts
│   └── package.json
│
├── api/
│   ├── main.py (FastAPI entry point)
│   ├── routes/
│   │   └── scanner.py (12 endpoints)
│   ├── services/
│   │   ├── scanner_service.py
│   │   ├── refactoring_service.py
│   │   └── remote_scanner_service.py (Phase 3.6)
│   ├── utils/
│   │   └── remote_handler.py (Phase 3.6)
│   └── scanner/
│       ├── python_scanner.py
│       ├── javascript_scanner.py
│       └── sql_scanner.py
│
├── tests/
│   ├── test_scanner.py
│   ├── test_refactor.py
│   ├── test_remote.py
│   └── test_live.py
│
└── README_PHASE_3.md (this file)
```

### Adding New Features

1. **Backend:**
   - Create service in `api/services/`
   - Add endpoints in `api/routes/scanner.py`
   - Add tests in `tests/`
   - Update API documentation

2. **Frontend:**
   - Create hook in `frontend/src/hooks/`
   - Create component in `frontend/src/components/`
   - Integrate in `CodeScanner.tsx`
   - Update type definitions

3. **Testing:**
   - Unit tests for logic
   - Integration tests for API
   - UI tests for components

### Code Style

**Python:**
- PEP 8 compliance
- Type hints required
- Docstrings for functions
- Max 100 characters per line

**TypeScript/React:**
- ESLint configuration
- Prettier formatting
- Functional components + hooks
- Props typed with interfaces

### Common Tasks

**Run tests:**
```bash
pytest tests/
```

**Format code:**
```bash
black api/
prettier --write frontend/src
```

**Type check:**
```bash
mypy api/
cd frontend && npx tsc --noEmit
```

**Build for production:**
```bash
cd frontend && npm run build
# Output in frontend/dist/
```

---

## Testing

### Test Coverage

- **Unit Tests:** Logic and utilities
- **Integration Tests:** API endpoints
- **Component Tests:** React components
- **E2E Tests:** Full workflows

### Running Tests

```bash
# Backend tests
pytest tests/ -v
pytest tests/test_phase_3_4.py -v  # Batch refactoring
pytest tests/test_phase_3_6.py -v  # GitHub/ZIP

# Frontend tests (if available)
cd frontend
npm test

# Type checking
mypy api/
cd frontend && npx tsc --noEmit
```

### Test Files

- `tests/test_scanner.py` - Scanner functionality
- `tests/test_export.py` - Export formats
- `tests/test_batch_refactor.py` - Batch refactoring
- `tests/test_live_analysis.py` - Live analysis
- `tests/test_github_zip.py` - GitHub/ZIP features

---

## Troubleshooting

### Common Issues

**Issue: "Address already in use" on port 8000**
```bash
# Kill existing process
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
# Or use different port
python -m uvicorn api.main:app --port 8001
```

**Issue: "Module not found" errors**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Issue: GitHub download timeout**
```bash
# Increase timeout in environment
export GITHUB_TIMEOUT_SECONDS=120
# Or configure in code
remote_scanner_service.download_timeout_seconds = 120
```

**Issue: ZIP extraction fails**
```bash
# Check file is valid ZIP
file myfile.zip  # Should output: Zip archive data

# Check disk space
df -h /tmp  # Need 1-2GB free
```

**Issue: Live analysis very slow**
```bash
# Check network latency
curl -w "%{time_total}\n" -o /dev/null http://localhost:8000/api/v1/scan/

# Monitor API response time
# Should be <100ms for analysis
```

### Logging

Enable debug logging:

```python
# In api/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

View logs:
```bash
# Terminal output (development)
python -m uvicorn api.main:app --reload

# File logging (production)
tail -f logs/scanner.log
```

---

## Contributing

### Pull Request Process

1. Create feature branch from `main`
2. Follow code style guidelines
3. Add tests for new features
4. Update documentation
5. Run full test suite
6. Submit PR with description

### Commit Messages

```
[Phase X.Y] Feature: Brief description

Detailed explanation of changes
- Change 1
- Change 2
- Change 3
```

Example:
```
[Phase 3.6] Feature: Add GitHub repository scanning

- Implement download_github_repo() utility
- Create scan-github API endpoint
- Add pre-flight validation endpoint
- Handle GitHub URL parsing for multiple formats
```

---

## Performance Tips

### Frontend Optimization

1. Use React DevTools Profiler
   ```bash
   npm run build:analyze
   ```

2. Lazy load components
   ```typescript
   const LiveEditor = React.lazy(() => import('./LiveCodeEditor'));
   ```

3. Memoize expensive computations
   ```typescript
   const results = useMemo(() => analyzeCode(code), [code]);
   ```

### Backend Optimization

1. Cache frequently accessed data
   ```python
   @functools.lru_cache(maxsize=128)
   def get_github_info(url):
       ...
   ```

2. Use async for I/O operations
   ```python
   async def download_github_repo(url):
       async with httpx.AsyncClient() as client:
           ...
   ```

3. Monitor memory usage
   ```bash
   python -m memory_profiler api/main.py
   ```

---

## Security Considerations

### Input Validation

- ✅ Validate GitHub URLs before download
- ✅ Check ZIP file format
- ✅ Enforce size limits
- ✅ Sanitize file paths

### File Handling

- ✅ Use temp directories (`tempfile.mkdtemp`)
- ✅ Clean up after processing
- ✅ Prevent path traversal attacks
- ✅ Set restrictive permissions

### API Security (Phase 4+)

- Add authentication (JWT tokens)
- Rate limiting
- CORS configuration
- Request signing

---

## Support & Resources

### Documentation
- Architecture overview: See [Architecture](#architecture)
- API reference: See [API Documentation](#api-documentation)
- Feature guides: See [Features](#features)

### Community
- GitHub Issues: Report bugs
- GitHub Discussions: Ask questions
- Pull Requests: Contribute code

### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Hooks Guide](https://react.dev/reference/react/hooks)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

---

## Version History

### Phase 3.6 (Current)
- ✅ GitHub repository scanning
- ✅ ZIP file extraction
- ✅ Temp file management

### Phase 3.5
- ✅ Real-time code analysis
- ✅ Live editor with metrics

### Phase 3.4
- ✅ Batch refactoring
- ✅ Diff viewer
- ✅ Edit history

### Phase 3.3
- ✅ Export functionality (5 formats)

### Phase 3.2
- ✅ Advanced complexity analysis

### Phase 3.1
- ✅ Recent paths history

---

## License

CodeScanner is provided as-is for educational and professional use.

---

**Last Updated:** June 2026  
**Maintainer:** CodeScanner Team  
**Status:** Production Ready ✅
