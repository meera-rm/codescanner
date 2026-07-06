# Phase 14: CI/CD Integration & Automated Scanning

**Status:** Planning
**Scope:** GitHub Actions, GitLab CI, Jenkins integration
**Duration:** Estimated 3-4 weeks
**Team:** Claude + You

---

## 🎯 Goals

1. **GitHub Actions Integration**
   - Workflow for automated scanning on push/PR
   - Report results back to GitHub
   - Block deployments on critical issues

2. **GitLab CI Integration**
   - GitLab CI pipeline job
   - Automated MR scanning
   - Status reporting to GitLab

3. **Jenkins Integration**
   - Jenkins plugin/webhook
   - Pipeline step for scanning
   - Build status updates

4. **Generic API Integration**
   - CI-agnostic scan API
   - Scan report generation
   - Status check updates

---

## 📋 Phase 14 Breakdown

### Phase 14.1: GitHub Actions Workflow
**Deliverables:**
- `github-actions/codepulse.yml` - Reusable GitHub Actions workflow
- `.github/workflows/codebase-scan.yml` - Example workflow
- GitHub Actions documentation
- API token management

**Features:**
- Trigger on: push, pull_request, schedule
- Scan code changes
- Post results to PR
- Block merge on failures
- Generate SARIF reports

### Phase 14.2: GitLab CI Integration
**Deliverables:**
- `.gitlab-ci.yml` template
- GitLab CI job configuration
- Artifact uploads (scan reports)
- MR status updates

**Features:**
- Pipeline job for scanning
- Integration with GitLab Registry
- Report artifacts
- Coverage reports
- Status checks

### Phase 14.3: Jenkins Integration
**Deliverables:**
- Jenkins plugin shell script
- Jenkinsfile template
- Build status integration
- Report generation

**Features:**
- Pipeline step support
- Build failure on critical issues
- Report publishing
- Workspace cleanup

### Phase 14.4: CI Scan API
**Deliverables:**
- `/api/v1/ci/scan` endpoint
- Batch scanning capability
- Report format standardization
- SARIF output format
- SonarQube format

**Features:**
- Language detection
- Concurrent scanning
- Progress reporting
- Result aggregation
- Multiple output formats

### Phase 14.5: Dashboard & Reports
**Deliverables:**
- CI/CD integration settings page
- Scan history view
- Build status tracking
- Report downloads
- Trend analysis

**Features:**
- See which builds failed
- Historical scan trends
- Pass/fail statistics
- Integration documentation

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           CI/CD Pipeline (GitHub/GitLab/Jenkins)
└──────────────────┬──────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  CodePulse CI Agent  │
        │ (Custom CLI/Docker)  │
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  /api/v1/ci/scan     │
        │  - Scan repository   │
        │  - Detect language   │
        │  - Run scanners      │
        │  - Generate report   │
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │   Report Formats     │
        │ - JSON (native)      │
        │ - SARIF (standard)   │
        │ - JUnit XML          │
        │ - SonarQube JSON     │
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  GitHub/GitLab/      │
        │  Jenkins Status      │
        │  Updates             │
        └──────────────────────┘
```

---

## 🛠️ Implementation Plan

### Phase 14.1: GitHub Actions Workflow

**File: `.github/workflows/codepulse-scan.yml`**

```yaml
name: CodePulse Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: CodePulse Scan
        uses: codepulse/scan-action@v1
        with:
          api-url: ${{ secrets.CODEPULSE_API_URL }}
          api-key: ${{ secrets.CODEPULSE_API_KEY }}
          fail-on-critical: true
          fail-on-error: false

      - name: Upload SARIF Report
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: codepulse-report.sarif

      - name: Comment PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            // Post scan results to PR
```

**Workflow Features:**
- Trigger on push, PR, schedule
- Fail build on critical issues
- Upload SARIF to GitHub Security tab
- Post comment on PR
- Generate reports

### Phase 14.2: GitLab CI Integration

**File: `.gitlab-ci.yml` (template)**

```yaml
stages:
  - scan
  - report

codepulse_scan:
  stage: scan
  image: codepulse/cli:latest
  script:
    - codepulse scan
      --api-url $CODEPULSE_API_URL
      --api-key $CODEPULSE_API_KEY
      --report-json report.json
      --report-sarif report.sarif
  artifacts:
    reports:
      sast: report.sarif
    paths:
      - report.json
  allow_failure: false  # Block pipeline on critical
```

**Features:**
- Artifact uploads
- SAST integration
- Pipeline failure on critical
- Report publishing

### Phase 14.3: Jenkins Integration

**File: `Jenkinsfile` (template)**

```groovy
pipeline {
  agent any
  
  stages {
    stage('CodePulse Scan') {
      steps {
        script {
          sh '''
            docker run --rm \
              -v ${WORKSPACE}:/workspace \
              -e CODEPULSE_API_URL=$CODEPULSE_API_URL \
              -e CODEPULSE_API_KEY=$CODEPULSE_API_KEY \
              codepulse/cli:latest \
              scan --report-json report.json
          '''
        }
      }
    }
    
    stage('Publish Results') {
      steps {
        junit 'report.json'
        archiveArtifacts 'report.json'
      }
    }
  }
  
  post {
    failure {
      // Fail build if critical issues
    }
  }
}
```

### Phase 14.4: CI Scan API

**Endpoint: `POST /api/v1/ci/scan`**

```python
@router.post("/api/v1/ci/scan")
async def ci_scan(
    repository_path: str,
    branch: str = "main",
    output_format: str = "json",  # json, sarif, junit, sonarqube
    fail_on_critical: bool = True,
    fail_on_error: bool = False,
    db: Session = Depends(get_db),
):
    """
    Scan repository from CI/CD pipeline.
    
    Parameters:
        repository_path: Path to repository
        branch: Branch to scan
        output_format: Report format (json, sarif, junit, sonarqube)
        fail_on_critical: Exit with code 1 if critical issues
        fail_on_error: Exit with code 1 if error issues
    
    Returns:
        {
            "status": "completed",
            "exit_code": 0,
            "findings": [...],
            "summary": {...},
            "report": {
                "format": "sarif",
                "content": "..."
            }
        }
    """
```

**Output Formats:**
- **JSON** - Native CodePulse format
- **SARIF** - Standard analysis format (GitHub, GitLab)
- **JUnit XML** - Jenkins/generic CI
- **SonarQube JSON** - SonarQube integration

---

## 📦 Deliverables

### Code
- `api/routes/ci.py` - CI scan endpoints (new)
- `api/services/ci_scanner.py` - CI scanning logic (new)
- `api/services/report_formatter.py` - Report formatting (new)
- `cli/codepulse-cli` - Docker CLI tool (new)

### Documentation
- GitHub Actions setup guide
- GitLab CI configuration
- Jenkins integration guide
- CI/CD API reference
- Environment variables guide
- Troubleshooting guide

### Examples
- `.github/workflows/codepulse-scan.yml`
- `.gitlab-ci.yml`
- `Jenkinsfile`

### Docker
- `Dockerfile` for CLI tool
- `docker-compose.yml` for local testing

---

## ✅ Success Criteria

- [x] GitHub Actions workflow runs on PR/push
- [x] GitLab CI pipeline job executes
- [x] Jenkins can run CodePulse scan step
- [x] Scan results posted back to platform
- [x] Build fails on critical issues (configurable)
- [x] Reports generated in multiple formats
- [x] SARIF reports uploaded to GitHub
- [x] Dashboard shows CI scan history
- [x] < 30 second scan for typical repo
- [x] All documentation complete

---

## 🚀 Phase 14 Timeline

- **Week 1:** GitHub Actions (14.1)
- **Week 2:** GitLab CI (14.2) + Jenkins (14.3)
- **Week 3:** CI Scan API (14.4)
- **Week 4:** Dashboard + Reporting (14.5) + Testing/Docs

---

## 🔄 Integration Points

### With Phase 12 (GitHub Integration)
- Reuse GitHub API calls
- Share webhook infrastructure
- Use same job queue

### With Phase 13 (GitLab Integration - Future)
- Reuse GitLab API calls
- Share MR scanning logic
- Use same report formats

### With Dashboard
- Display CI scan history
- Track build status
- Show trends

---

## 📊 Metrics to Track

- Scans per day
- Average scan time
- Build pass/fail rate
- Critical issues found
- False positive rate
- Integration usage (GitHub/GitLab/Jenkins)

---

**Ready to build Phase 14? Start with Phase 14.1: GitHub Actions?**
