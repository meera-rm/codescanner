# Phase 12: GitHub Integration & PR Scanning

**Status:** Planning
**Scope:** Add GitHub PR scanning with automated code review and quality gates
**Duration:** Estimated 2-3 weeks
**Team:** You + Claude

---

## 🎯 Goals

1. **Shift Left:** Catch code issues before merge (not after)
2. **Prevent Bad Commits:** Block PRs with CRITICAL/ERROR issues
3. **Developer Feedback:** Inline code review comments with fixes
4. **Increase Adoption:** Teams see immediate value on every PR

---

## 🏗️ Architecture

```
GitHub PR Created
    ↓
Webhook → CodePulse API
    ↓
Scan code changes
    ↓
Generate findings
    ↓
Post PR review comments
    ↓
Set status check (pass/fail)
    ↓
Block merge if CRITICAL
```

### Components

**1. GitHub App Registration**
- OAuth app for authentication
- Webhooks for PR events
- Permissions: read code, write PR comments, update checks

**2. New Backend Endpoints**
- `POST /api/v1/github/webhook` — Handle GitHub webhooks
- `POST /api/v1/github/authorize` — OAuth callback
- `GET /api/v1/github/installations` — List connected repos
- `POST /api/v1/github/settings/{repo_id}` — Configure repo

**3. New Services**
- `GitHubService` — GitHub API interactions (PyGithub)
- `PRScanService` — Scan changed files only
- `DiffAnalyzer` — Parse git diffs

**4. Database Updates**
- `GithubRepository` — Store repo metadata
- `PRScan` — Store PR scan results
- `GithubInstallation` — Store OAuth tokens

**5. Frontend**
- GitHub connection page
- Repository settings (enable/disable, thresholds)
- PR scan history & results

---

## 📋 Deliverables

### Phase 12.1: GitHub App Setup (Days 1-3)
- [ ] Create GitHub App in developer settings
- [ ] Setup OAuth flow
- [ ] Store installation tokens securely
- [ ] Test webhook delivery

### Phase 12.2: Backend Integration (Days 4-7)
- [ ] `GitHubService` class (API calls)
- [ ] `PRScanService` (diff parsing, scanning)
- [ ] Webhook endpoint (`POST /github/webhook`)
- [ ] Authorization endpoint
- [ ] Database models + migrations

### Phase 12.3: Review Comments (Days 8-10)
- [ ] Post comments on PR for each finding
- [ ] Link to dashboard with full details
- [ ] Suggest fixes for CRITICAL issues
- [ ] Show file/line of issue

### Phase 12.4: Status Checks (Days 11-12)
- [ ] Set PR status (pending → success/failure)
- [ ] Block merge if CRITICAL
- [ ] Show summary in PR

### Phase 12.5: Frontend + Settings (Days 13-15)
- [ ] GitHub connection page
- [ ] Repository settings
- [ ] Enable/disable scanning per repo
- [ ] Configure alert thresholds

### Phase 12.6: Testing & Docs (Days 16+)
- [ ] Integration tests
- [ ] E2E tests (real PR)
- [ ] Documentation
- [ ] User guide

---

## 🔧 Implementation Plan

### Step 1: GitHub App Registration
```bash
# Register app at: https://github.com/settings/apps
# Permissions needed:
#   - Read repository contents
#   - Read pull requests & issues
#   - Write pull request reviews
#   - Write checks
# Webhooks:
#   - pull_request (opened, synchronize)
#   - push
```

### Step 2: Create Database Models
```python
# api/db/models.py
class GitHubInstallation(Base):
    __tablename__ = "github_installations"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    installation_id = Column(Integer, unique=True)  # GitHub app installation ID
    token = Column(String)  # Encrypted access token
    repositories = relationship("GithubRepository", back_populates="installation")
    created_at = Column(DateTime, default=datetime.utcnow)

class GithubRepository(Base):
    __tablename__ = "github_repositories"
    
    id = Column(String, primary_key=True)
    installation_id = Column(String, ForeignKey("github_installations.id"))
    repo_name = Column(String)  # owner/repo
    repo_id = Column(Integer)  # GitHub repo ID
    enabled = Column(Boolean, default=True)
    fail_on_critical = Column(Boolean, default=True)
    fail_on_error = Column(Boolean, default=False)
    pr_scans = relationship("PRScan", back_populates="repository")
    created_at = Column(DateTime, default=datetime.utcnow)

class PRScan(Base):
    __tablename__ = "pr_scans"
    
    id = Column(String, primary_key=True)
    repository_id = Column(String, ForeignKey("github_repositories.id"))
    pr_number = Column(Integer)
    branch = Column(String)
    commit_sha = Column(String)
    findings = Column(JSON)  # Scan results
    comment_id = Column(String, nullable=True)  # GitHub comment ID
    status = Column(String, default="pending")  # pending, success, failure
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
```

### Step 3: Create GitHub Service
```python
# api/services/github_service.py
from github import Github, GithubIntegration
import jwt
from datetime import datetime, timedelta

class GitHubService:
    def __init__(self, private_key: str, app_id: int):
        self.app_id = app_id
        self.private_key = private_key
    
    def get_installation_access_token(self, installation_id: int) -> str:
        """Get temporary access token for installation."""
        payload = {
            'iat': int(datetime.utcnow().timestamp()),
            'exp': int((datetime.utcnow() + timedelta(minutes=10)).timestamp()),
            'iss': self.app_id,
        }
        token = jwt.encode(payload, self.private_key, algorithm='RS256')
        integration = GithubIntegration(self.app_id, self.private_key)
        return integration.get_access_token(installation_id).token
    
    def post_pr_comment(self, token: str, repo: str, pr_number: int, comment: str):
        """Post comment on PR."""
        g = Github(token)
        repository = g.get_repo(repo)
        pull = repository.get_pull(pr_number)
        pull.create_issue_comment(comment)
    
    def post_pr_review(self, token: str, repo: str, pr_number: int, comments: list):
        """Post review with inline comments."""
        g = Github(token)
        repository = g.get_repo(repo)
        pull = repository.get_pull(pr_number)
        # Post review with comments
```

### Step 4: Create PR Scan Service
```python
# api/services/pr_scan_service.py
from git import Repo
from api.scanner import PythonScanner, JavaScriptScanner

class PRScanService:
    def scan_pr_changes(self, repo_path: str, base_branch: str, pr_branch: str) -> dict:
        """
        Scan only changed files in PR.
        
        Returns:
            {
                'added_files': [...],
                'modified_files': [...],
                'deleted_files': [...],
                'findings': [...],
                'summary': {...}
            }
        """
        repo = Repo(repo_path)
        
        # Get diff between base and PR branch
        diffs = repo.git.diff(f'{base_branch}...{pr_branch}', name_only=True).split('\n')
        
        # Scan only changed files
        findings = []
        for file in diffs:
            if file.endswith('.py'):
                scanner = PythonScanner()
                findings.extend(scanner.scan_file(file))
            elif file.endswith('.js'):
                scanner = JavaScriptScanner()
                findings.extend(scanner.scan_file(file))
        
        return {
            'changed_files': diffs,
            'findings': findings,
            'critical_count': len([f for f in findings if f.severity == 'CRITICAL']),
            'error_count': len([f for f in findings if f.severity == 'ERROR']),
        }
```

### Step 5: Create Webhook Endpoint
```python
# api/routes/github.py
from fastapi import APIRouter, Request, HTTPException
import hmac
import hashlib

router = APIRouter(prefix="/api/v1/github", tags=["github"])

@router.post("/webhook")
async def github_webhook(request: Request):
    """Handle GitHub webhook events."""
    # Verify webhook signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_webhook_signature(await request.body(), signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    payload = await request.json()
    event = request.headers.get('X-GitHub-Event')
    
    if event == 'pull_request' and payload['action'] in ['opened', 'synchronize']:
        # Trigger PR scan
        pr_number = payload['pull_request']['number']
        repo_name = payload['repository']['full_name']
        commit_sha = payload['pull_request']['head']['sha']
        
        # Queue async scan job
        await scan_pr(repo_name, pr_number, commit_sha)
        
        return {'status': 'scanning'}
    
    return {'status': 'acknowledged'}
```

---

## 🎮 User Flow

### Admin Setup (One-time)
1. Go to http://localhost:3000/github-connect
2. Click "Authorize GitHub App"
3. Redirected to GitHub to grant permissions
4. Select repositories to scan
5. Configure thresholds (CRITICAL blocks? ERROR blocks?)
6. Save settings

### Developer Experience
1. Push code to GitHub
2. Create PR
3. CodePulse automatically scans changes
4. 30-60 seconds: Comments appear with issues
5. PR status shows: ✅ Pass or ❌ Fail
6. If CRITICAL: PR blocked from merging
7. Developer clicks link → Dashboard with full details
8. Developer uses "Fix" button → AI generates fix
9. Developer applies fix → Re-scans → Merge

---

## ✅ Success Criteria

- [ ] GitHub App installed & working
- [ ] PR scans triggered automatically
- [ ] Comments posted on PRs with findings
- [ ] PR blocked if CRITICAL issues
- [ ] Frontend shows connected repos
- [ ] Settings page works
- [ ] 10+ repos can be scanned
- [ ] Average scan time < 60 seconds
- [ ] Zero false positives on test repos

---

## 🚀 Launch Checklist

- [ ] GitHub App created & configured
- [ ] Backend endpoints tested
- [ ] Frontend UI complete
- [ ] Database migrations run
- [ ] Webhook signature verification working
- [ ] Error handling for API failures
- [ ] Rate limiting applied
- [ ] Logging & monitoring setup
- [ ] Documentation written
- [ ] Team trained on new feature

---

## 📊 Phase 12 Roadmap

```
Week 1: GitHub App + Backend Service
Week 2: PR Scanning + Comments
Week 3: Frontend + Settings + Polish
```

---

## 💡 Future Enhancements (Phase 13+)

- GitLab integration
- Custom quality gates per team
- AI-powered auto-fixes applied to PRs
- Scheduled scans (daily/weekly)
- Slack notifications
- Performance comparison (vs team average)
- Code ownership tracking
- Auto-merge low-risk PRs

---

**Ready to build Phase 12?**
