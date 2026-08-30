# CodePulse AI — Technical Implementation Guide (MVP)

## Project Structure (Recommended)

```
codepulse-ai/
├── backend/
│   ├── app.py                          # FastAPI entry point
│   ├── requirements.txt
│   ├── .env.example
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                   # API endpoints
│   │   ├── schemas.py                  # Pydantic models
│   │   └── dependencies.py             # Database, config, etc.
│   ├── core/
│   │   ├── __init__.py
│   │   ├── analyzer.py                 # Base analyzer class
│   │   ├── orchestrator.py             # ScanOrchestrator
│   │   └── models.py                   # Database models
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── complexity.py               # ComplexityAnalyzer ✓
│   │   ├── security.py                 # SecurityAnalyzer ✓
│   │   ├── documentation.py            # DocumentationAnalyzer ✓
│   │   ├── dependency.py               # DependencyAnalyzer (partial)
│   │   ├── codesmells.py               # CodeSmellAnalyzer (partial)
│   │   └── registry.py                 # Analyzer registration
│   ├── skills/
│   │   ├── __init__.py
│   │   ├── refactor.py                 # RefactorSkill (TODO)
│   │   ├── validation.py               # ValidationSkill (TODO)
│   │   └── reporting.py                # ReportGenerator
│   ├── services/
│   │   ├── __init__.py
│   │   ├── file_handler.py             # Upload, extract ZIP
│   │   ├── language_detector.py        # Language detection
│   │   ├── scoring.py                  # Grade calculation
│   │   └── storage.py                  # Results persistence
│   └── tests/
│       ├── __init__.py
│       ├── test_analyzers.py           # Unit tests
│       └── test_orchestrator.py        # Integration tests
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx           # Main page
│   │   │   └── Results.jsx             # Results view
│   │   ├── components/
│   │   │   ├── Upload.jsx              # Upload widget
│   │   │   ├── FeatureSelector.jsx     # Checkboxes
│   │   │   ├── OverviewTab.jsx         # Dashboard view
│   │   │   ├── FindingsTable.jsx       # Issues table
│   │   │   └── ReportDownload.jsx      # Download buttons
│   │   ├── api/
│   │   │   └── client.js               # API calls (fetch)
│   │   └── hooks/
│   │       └── useScan.js              # React hook for scan logic
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   └── vite.config.js
│
├── cli/
│   ├── __init__.py
│   ├── main.py                         # CLI entry point (Click)
│   └── commands.py                     # Commands (scan, report)
│
├── .pre-commit-hooks.yaml              # Pre-commit configuration
├── README.md
├── CONTRIBUTING.md
└── ROADMAP.md
```

---

## Database Schema (SQLite MVP)

```sql
CREATE TABLE scans (
    id TEXT PRIMARY KEY,                -- UUID
    created_at TIMESTAMP NOT NULL,
    repo_path TEXT NOT NULL,
    repo_size_bytes INT,
    language_distribution JSON,         -- {"python": 60, "js": 40}
    enabled_features JSON,              -- ["complexity", "security", "docs"]
    status TEXT,                        -- "queued", "running", "completed", "failed"
    error_message TEXT,
    completion_time_seconds FLOAT
);

CREATE TABLE findings (
    id TEXT PRIMARY KEY,                -- UUID
    scan_id TEXT NOT NULL,
    analyzer TEXT NOT NULL,             -- "complexity", "security", etc.
    severity TEXT NOT NULL,             -- "critical", "high", "medium", "low", "info"
    file_path TEXT NOT NULL,
    line_number INT,
    column_number INT,
    issue_type TEXT,                    -- "long_function", "hardcoded_secret", etc.
    message TEXT,
    suggestion TEXT,
    code_context TEXT,                  -- 3-5 lines around the issue
    FOREIGN KEY (scan_id) REFERENCES scans(id)
);

CREATE TABLE scan_results (
    id TEXT PRIMARY KEY,
    scan_id TEXT NOT NULL UNIQUE,
    grade TEXT,                         -- "A", "B+", "C", etc.
    score INT,                          -- 0-100
    total_issues INT,
    critical_count INT,
    high_count INT,
    medium_count INT,
    low_count INT,
    info_count INT,
    result_json JSON,                   -- Full scan result (for export)
    FOREIGN KEY (scan_id) REFERENCES scans(id)
);

-- Indexes for quick lookup
CREATE INDEX idx_scans_created_at ON scans(created_at);
CREATE INDEX idx_findings_scan_id ON findings(scan_id);
CREATE INDEX idx_findings_severity ON findings(severity);
```

---

## API Routes (FastAPI)

### Authentication (MVP: None)
```python
# TODO: Add JWT auth in v1.1
# For now, all endpoints are open
```

### Core Endpoints

#### POST /api/scan/upload
Upload repo/file/ZIP
```python
@router.post("/scan/upload")
async def upload_repo(
    file: UploadFile = File(...),
    features: List[str] = Query(["complexity", "security", "documentation"])
):
    """
    Upload a ZIP file or folder for scanning.
    
    Response:
    {
        "scan_id": "uuid-string",
        "status": "queued",
        "uploaded_at": "2024-01-01T00:00:00Z"
    }
    """
    scan_id = str(uuid.uuid4())
    # Extract ZIP to /tmp/uploads/{scan_id}/
    # Save scan metadata to DB
    return {"scan_id": scan_id, "status": "queued"}
```

#### POST /api/scan/{scan_id}/run
Start scanning
```python
@router.post("/api/scan/{scan_id}/run")
async def run_scan(scan_id: str):
    """
    Start scanning the uploaded repo.
    
    Response:
    {
        "scan_id": "uuid",
        "status": "running",
        "message": "Scan started"
    }
    """
    # Load repo from disk
    # Initialize ScanOrchestrator with enabled features
    # Run analyzers (sync for MVP, async for v1.1)
    # Store results in DB
    # Return findings
```

#### GET /api/scan/{scan_id}/results
Get scan results (JSON)
```python
@router.get("/api/scan/{scan_id}/results")
async def get_results(scan_id: str):
    """
    Get scan results in JSON format.
    
    Response:
    {
        "scan_id": "uuid",
        "grade": "B+",
        "score": 78,
        "completed_at": "2024-01-01T00:05:00Z",
        "findings": [
            {
                "file": "src/main.py",
                "line": 45,
                "severity": "high",
                "type": "long_function",
                "message": "Function 'process_data' is 120 lines long"
            }
        ],
        "summary": {
            "total_issues": 14,
            "critical": 0,
            "high": 2,
            "medium": 8,
            "low": 4
        }
    }
    """
    # Fetch from DB, return JSON
```

#### GET /api/scan/{scan_id}/report
Download report (PDF/HTML/Markdown)
```python
@router.get("/api/scan/{scan_id}/report")
async def download_report(
    scan_id: str,
    format: str = Query("pdf")  # pdf, html, json, markdown
):
    """
    Download report in requested format.
    
    Returns binary file (PDF) or text (JSON/Markdown)
    """
    # Fetch scan results from DB
    # Render based on format
    # Return file for download
```

#### GET /api/analyzers
List available analyzers
```python
@router.get("/api/analyzers")
async def list_analyzers():
    """
    Response:
    {
        "analyzers": [
            {
                "id": "complexity",
                "name": "Complexity Analyzer",
                "description": "Measures cyclomatic and cognitive complexity"
            },
            ...
        ]
    }
    """
```

---

## Backend Implementation Details

### ScanOrchestrator (Core Component)

```python
# core/orchestrator.py

class ScanOrchestrator:
    """Main orchestration engine for scanning."""
    
    def __init__(self, repo_path: str, enabled_features: List[str]):
        self.repo_path = repo_path
        self.enabled_features = enabled_features
        self.analyzer_registry = AnalyzerRegistry()
        self.findings: List[Finding] = []
    
    def scan(self) -> ScanResult:
        """Execute full scan pipeline."""
        
        # Step 1: Language detection
        languages = self.detect_languages()
        
        # Step 2: File traversal
        files = self.traverse_files()
        
        # Step 3: Run enabled analyzers
        for analyzer_name in self.enabled_features:
            analyzer = self.analyzer_registry.get(analyzer_name)
            findings = analyzer.analyze(self.repo_path, files)
            self.findings.extend(findings)
        
        # Step 4: Score & grade
        score, grade = self.calculate_score()
        
        # Step 5: Return results
        return ScanResult(
            score=score,
            grade=grade,
            findings=self.findings,
            languages=languages,
            files_scanned=len(files)
        )
    
    def detect_languages(self) -> Dict[str, int]:
        """Detect programming languages in repo."""
        # Count files by extension
        # Return {"python": 60, "javascript": 40, ...}
    
    def traverse_files(self) -> List[FilePath]:
        """Walk repo tree, skip .git, node_modules, etc."""
        skip_dirs = {".git", "node_modules", "venv", "__pycache__", "dist", "build"}
        files = []
        for root, dirs, filenames in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for file in filenames:
                files.append(os.path.join(root, file))
        return files
    
    def calculate_score(self) -> Tuple[int, str]:
        """Convert findings to 0-100 score + grade."""
        total_issues = len(self.findings)
        critical = sum(1 for f in self.findings if f.severity == "critical")
        high = sum(1 for f in self.findings if f.severity == "high")
        
        # Simple scoring formula
        penalty = (critical * 10) + (high * 3) + (medium * 1)
        score = max(0, 100 - penalty)
        
        # Grade mapping
        grades = {
            (90, 100): "A",
            (80, 89): "B",
            (70, 79): "C",
            (60, 69): "D",
            (0, 59): "F"
        }
        grade = next(g for (min_s, max_s), g in grades.items() if min_s <= score <= max_s)
        
        return score, grade
```

### Base Analyzer Class

```python
# core/analyzer.py

from abc import ABC, abstractmethod

class BaseAnalyzer(ABC):
    """Base class for all code analyzers."""
    
    name: str = "BaseAnalyzer"
    description: str = "Base analyzer"
    
    @abstractmethod
    def analyze(self, repo_path: str, files: List[str]) -> List[Finding]:
        """
        Analyze repo and return findings.
        
        Args:
            repo_path: Path to repo root
            files: List of file paths to analyze
        
        Returns:
            List of Finding objects
        """
        pass
    
    def parse_file(self, file_path: str) -> Optional[AST]:
        """Parse Python/JS file using appropriate parser."""
        try:
            if file_path.endswith(".py"):
                return ast.parse(open(file_path).read())
            elif file_path.endswith(".js") or file_path.endswith(".jsx"):
                # Use esprima or similar JS parser
                pass
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
            return None
```

### Analyzer Registry (Plugin Architecture)

```python
# analyzers/registry.py

class AnalyzerRegistry:
    """Plugin registry for all analyzers."""
    
    _registry = {}
    
    @classmethod
    def register(cls, analyzer: Type[BaseAnalyzer]):
        """Register analyzer."""
        cls._registry[analyzer.name.lower()] = analyzer
    
    @classmethod
    def get(cls, name: str) -> BaseAnalyzer:
        """Get analyzer instance by name."""
        analyzer_class = cls._registry.get(name.lower())
        if not analyzer_class:
            raise ValueError(f"Analyzer '{name}' not found")
        return analyzer_class()
    
    @classmethod
    def list_all(cls) -> List[str]:
        """List all registered analyzers."""
        return list(cls._registry.keys())

# Auto-register analyzers
register_analyzers = [
    ComplexityAnalyzer,
    SecurityAnalyzer,
    DocumentationAnalyzer,
    DependencyAnalyzer,
    CodeSmellAnalyzer
]

for analyzer in register_analyzers:
    AnalyzerRegistry.register(analyzer)
```

---

## Frontend Implementation Details

### React Project Setup

```bash
npm create vite@latest codepulse-frontend -- --template react
cd codepulse-frontend
npm install axios react-query lucide-react tailwindcss
```

### Main App Component

```jsx
// src/App.jsx
import { useState } from 'react'
import Upload from './components/Upload'
import FeatureSelector from './components/FeatureSelector'
import Dashboard from './pages/Dashboard'
import './App.css'

export default function App() {
    const [scanId, setScanId] = useState(null)
    const [isScanning, setIsScanning] = useState(false)
    const [results, setResults] = useState(null)
    
    const handleUpload = async (file, selectedFeatures) => {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('features', selectedFeatures)
        
        const response = await fetch('/api/scan/upload', {
            method: 'POST',
            body: formData
        })
        
        const data = await response.json()
        setScanId(data.scan_id)
        return data.scan_id
    }
    
    const handleRunScan = async (id) => {
        setIsScanning(true)
        const response = await fetch(`/api/scan/${id}/run`, { method: 'POST' })
        const data = await response.json()
        setResults(data)
        setIsScanning(false)
    }
    
    return (
        <div className="App">
            {!scanId ? (
                <Upload onUpload={handleUpload} />
            ) : !results ? (
                <FeatureSelector 
                    scanId={scanId}
                    onRun={handleRunScan}
                    isLoading={isScanning}
                />
            ) : (
                <Dashboard results={results} />
            )}
        </div>
    )
}
```

### Upload Component

```jsx
// src/components/Upload.jsx
import { useState } from 'react'

export default function Upload({ onUpload }) {
    const [isDragging, setIsDragging] = useState(false)
    
    const handleDrop = (e) => {
        e.preventDefault()
        const files = e.dataTransfer.files
        if (files.length > 0) {
            handleFile(files[0])
        }
    }
    
    const handleFile = async (file) => {
        if (!file.name.endsWith('.zip')) {
            alert('Please upload a .zip file')
            return
        }
        await onUpload(file, ["complexity", "security", "documentation"])
    }
    
    return (
        <div className="upload-container">
            <div
                className={`drop-zone ${isDragging ? 'active' : ''}`}
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
            >
                <p>Drag & drop your repository ZIP here</p>
                <input 
                    type="file" 
                    accept=".zip"
                    onChange={(e) => handleFile(e.target.files[0])}
                />
            </div>
        </div>
    )
}
```

### Dashboard Component

```jsx
// src/pages/Dashboard.jsx
export default function Dashboard({ results }) {
    const { grade, score, findings, summary } = results
    
    return (
        <div className="dashboard">
            {/* Grade Card */}
            <div className="grade-card">
                <span className={`grade grade-${grade}`}>{grade}</span>
                <p>Code Quality Score</p>
                <span className="score">{score}/100</span>
            </div>
            
            {/* Summary Stats */}
            <div className="summary-grid">
                <StatCard label="Total Issues" value={summary.total_issues} />
                <StatCard label="Critical" value={summary.critical} severity="critical" />
                <StatCard label="High" value={summary.high} severity="high" />
                <StatCard label="Medium" value={summary.medium} severity="medium" />
            </div>
            
            {/* Findings Table */}
            <FindingsTable findings={findings} />
            
            {/* Download Buttons */}
            <div className="download-section">
                <button onClick={() => downloadReport('pdf')}>📄 PDF</button>
                <button onClick={() => downloadReport('json')}>📊 JSON</button>
                <button onClick={() => downloadReport('markdown')}>📝 Markdown</button>
            </div>
        </div>
    )
}

async function downloadReport(format) {
    const response = await fetch(`/api/scan/${scanId}/report?format=${format}`)
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report.${format}`
    a.click()
}
```

---

## CLI Tool (codepulse command)

```python
# cli/main.py
import click
from pathlib import Path

@click.group()
def cli():
    """CodePulse AI – Code Quality Scanner"""
    pass

@cli.command()
@click.argument('path', default='.')
@click.option('--features', multiple=True, default=['complexity', 'security', 'documentation'])
@click.option('--output', type=click.Choice(['json', 'table', 'summary']), default='table')
@click.option('--fail-on', type=click.Choice(['critical', 'high', 'medium']), default='critical')
def scan(path, features, output, fail_on):
    """Scan a repository for code quality issues."""
    
    from backend.core.orchestrator import ScanOrchestrator
    
    orchestrator = ScanOrchestrator(path, list(features))
    result = orchestrator.scan()
    
    if output == 'json':
        click.echo(result.to_json())
    elif output == 'table':
        print_table(result)
    else:
        print_summary(result)
    
    # Fail if threshold exceeded
    if should_fail(result, fail_on):
        raise SystemExit(1)

if __name__ == '__main__':
    cli()
```

---

## Pre-Commit Hook Configuration

```yaml
# .pre-commit-hooks.yaml
- id: codepulse-scan
  name: CodePulse AI Security Scan
  entry: codepulse scan --staged --mode quick --fail-on high
  language: system
  pass_filenames: false
  stages: [commit]
  types: [python, javascript, typescript]
```

User setup:
```bash
# Add to .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: codepulse-scan
        name: CodePulse AI
        entry: codepulse scan --staged --fail-on high
        language: system
        pass_filenames: false

# Then run:
pre-commit install
```

---

## Dependencies & Requirements

```txt
# backend/requirements.txt
fastapi==0.104.0
uvicorn==0.24.0
pydantic==2.4.0
sqlalchemy==2.0.0
python-multipart==0.0.6
aiofiles==23.2.0
click==8.1.7
gitpython==3.1.40
reportlab==4.0.4
jinja2==3.1.2

# Code analysis
radon==6.0.1      # Cyclomatic complexity
pylint==3.0.0     # Code smells
bandit==1.7.5     # Security

# Async
asyncio==3.4.3
aiohttp==3.9.0
```

```json
// frontend/package.json
{
  "dependencies": {
    "react": "^18.2.0",
    "axios": "^1.6.0",
    "react-query": "^3.39.0",
    "tailwindcss": "^3.3.0",
    "lucide-react": "^0.292.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0"
  }
}
```

---

## Environment Configuration (.env)

```bash
# .env.example

# Database
DATABASE_URL=sqlite:///./codepulse.db

# Storage
UPLOAD_DIR=/tmp/uploads
MAX_UPLOAD_SIZE_MB=500

# Scanning
MAX_SCAN_TIME_SECONDS=120
MAX_FILE_SIZE_MB=10
SKIP_FOLDERS=.git,node_modules,venv,__pycache__

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000

# Optional: Claude AI (for RefactorSkill in v1.1)
ANTHROPIC_API_KEY=

# Logging
LOG_LEVEL=INFO
```

---

## Testing Strategy

### Unit Tests
```python
# backend/tests/test_analyzers.py
import pytest
from analyzers import ComplexityAnalyzer

def test_complexity_analyzer():
    analyzer = ComplexityAnalyzer()
    findings = analyzer.analyze("./test_repo", ["test.py"])
    assert len(findings) > 0
    assert all(f.severity in ["critical", "high", "medium"]) for f in findings
```

### Integration Tests
```python
# backend/tests/test_orchestrator.py
def test_full_scan():
    orchestrator = ScanOrchestrator("./test_repo", ["complexity", "security"])
    result = orchestrator.scan()
    assert result.grade in ["A", "B", "C", "D", "F"]
    assert 0 <= result.score <= 100
```

### E2E Tests
```javascript
// frontend/tests/e2e.spec.js
describe("Upload to Dashboard Flow", () => {
    it("should complete full scan", () => {
        cy.visit("http://localhost:3000")
        cy.get(".drop-zone").selectFile("test.zip")
        cy.get(".run-button").click()
        cy.get(".dashboard").should("be.visible")
        cy.get(".grade-card").contains("B")
    })
})
```

---

## Performance Targets (MVP)

| Metric | Target | How to Achieve |
|--------|--------|----------------|
| Small repo scan (< 100 files) | < 5 sec | Synchronous, fast analyzers |
| Medium repo (500-1K files) | < 30 sec | Concurrent analyzers |
| Large repo (10K+ files) | < 120 sec | Streaming + chunking |
| Dashboard load | < 1 sec | Client-side caching |
| PDF generation | < 5 sec | Template rendering |

---

## Deployment Checklist (MVP)

### Local Development
- [ ] Backend runs on http://localhost:8000
- [ ] Frontend runs on http://localhost:3000
- [ ] API calls work end-to-end

### Testing
- [ ] All unit tests pass
- [ ] No console errors (frontend)
- [ ] No warnings (backend)

### Pre-Demo
- [ ] Sample repos scanned successfully
- [ ] Reports download correctly
- [ ] CLI tool works: `codepulse scan .`
- [ ] Pre-commit hook blocks bad commits

---

## Next Steps (Day 1 Morning)

```bash
# 1. Initialize projects
mkdir codepulse-ai && cd codepulse-ai
git init
git branch -M main

# 2. Backend setup
mkdir backend frontend cli
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install fastapi uvicorn pydantic sqlalchemy
touch app.py requirements.txt .env

# 3. Frontend setup
cd ../frontend
npm create vite@latest . -- --template react
npm install

# 4. Create directory structure
mkdir -p backend/api backend/core backend/analyzers backend/skills backend/services backend/tests
mkdir -p frontend/src/{components,pages,api,hooks}

# 5. Push to GitHub
git add .
git commit -m "Initial project setup"
git remote add origin https://github.com/your-org/codepulse-ai.git
git push -u origin main
```

This is your **complete technical blueprint** for the next 7 days. Start with Day 1 infrastructure and work through the timeline step-by-step.

Good luck! 🚀
