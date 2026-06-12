---
created_at: 2026-06-12T18:16:43Z
title: Phase 4 Ai Refactoring With Pr Workflow Plan
source: claude-code
project: codescanner
---

# Phase 4: AI Refactoring with PR Workflow - Planning Document

**Project:** CODEPULSE AI Code Intelligence Platform  
**Phase:** 4 (Visual UI + GitHub Integration)  
**Status:** PLANNING (Ready for implementation after Phase 3.5 stabilizes)  
**Timeline:** 110-140 hours (2-3 weeks with 2 developers)  
**Priority:** HIGH (Final piece of core differentiator)

---

## Executive Summary

Phase 4 transforms Phase 3.5's backend iteration capability into a **production-grade developer experience** with:

1. **Visual Refactoring Interface** - Browse files, preview changes side-by-side
2. **GitHub PR Workflow** - One-click PR creation with auto-branch management
3. **Team Notifications** - GitHub, Slack, email alerts when PRs ready for review
4. **Real-time Dashboard** - Watch iteration progress with live metrics

**User Flow:**
```
Developer starts iteration
     ↓
Watches live progress in dashboard
     ↓
Sees refactored code in visual diff viewer
     ↓
Clicks "Create PR"
     ↓
System creates branch + commit + PR on GitHub
     ↓
Team gets notified
     ↓
Code review workflow begins
```

---

## What Gets Built

### Phase 4A: Backend Services (40-50 hours)

| Component | Purpose | Effort |
|-----------|---------|--------|
| RefactoringService (extended) | Add file diff generation | 10 hrs |
| GitHubService | PR creation workflow | 10 hrs |
| NotificationService | GitHub/Slack/email alerts | 10 hrs |
| DiffGenerator | Side-by-side diff logic | 10 hrs |
| MetricsTracker (extended) | Real-time metrics | 10 hrs |
| **Total** | | **50 hrs** |

### Phase 4B: Frontend Components (50-60 hours)

| Component | Purpose | Effort |
|-----------|---------|--------|
| RefactoringLounge | Main dashboard | 15 hrs |
| FileBrowser | File tree with severity badges | 10 hrs |
| DiffViewer | Side-by-side code viewer | 15 hrs |
| LineHighlighting | Red/green line markers | 10 hrs |
| ProgressTracker | Real-time iteration display | 10 hrs |
| **Total** | | **60 hrs** |

### Phase 4C: Integration (20-30 hours)

| Component | Purpose | Effort |
|-----------|---------|--------|
| Frontend-Backend API | WebSocket + REST integration | 10 hrs |
| GitHub OAuth | Authentication flow | 5 hrs |
| E2E Testing | Full workflow validation | 10 hrs |
| Documentation | API + UI guide | 5 hrs |
| **Total** | | **30 hrs** |

**TOTAL EFFORT: 110-140 hours (2-3 weeks)**

---

## Detailed Architecture

### Backend Services

#### 1. RefactoringService (Extended)

Current: Generates fixes with Claude API  
New: Also generates diffs and file lists

```python
class RefactoringService:
    # Existing methods
    async def generate_fix(self, issue: Issue) -> Fix: ...
    async def validate_fix(self, fix: Fix) -> bool: ...
    
    # NEW methods
    async def get_refactored_files(self, job_id: str) -> List[File]: 
        """Return list of files that need refactoring with severity."""
        # Scan at iteration start
        # Track changes across iterations
        # Return: [{path, severity, issues_count, lines_changed}, ...]
        
    async def generate_diff(self, file_path: str, original: str, 
                           refactored: str) -> Diff:
        """Generate side-by-side diff with line highlighting."""
        # Use difflib for character-level diffs
        # Highlight red/green lines
        # Track moved code segments
        # Return: {additions, deletions, modifications}
```

#### 2. GitHubService (New)

Manages GitHub integration for PR creation

```python
class GitHubService:
    def __init__(self, token: str, repo: str):
        self.token = token  # GitHub personal access token
        self.repo = repo    # owner/repo
        self.client = githubapi.GitHub(token)
    
    async def create_pr(self, 
                       branch_name: str,
                       title: str,
                       description: str,
                       files_changed: Dict[str, str]) -> PullRequest:
        """Create pull request with automatic branch creation."""
        
        # 1. Create branch from main
        branch = await self.client.create_branch(branch_name, "main")
        
        # 2. Commit changes
        for file_path, content in files_changed.items():
            await self.client.update_file(
                file_path,
                content,
                f"Refactor: {title}",
                branch=branch_name
            )
        
        # 3. Create PR
        pr = await self.client.create_pull_request(
            title=title,
            description=description,
            head=branch_name,
            base="main"
        )
        
        # 4. Assign reviewers, add labels, set milestone
        await self.client.assign_reviewers(pr.number, ["@user1", "@user2"])
        await self.client.add_labels(pr.number, ["refactor", "auto-generated"])
        
        return pr
    
    async def update_pr_status(self, pr_number: int, 
                              metrics: Dict) -> None:
        """Update PR with iteration metrics comment."""
        comment = f"""
        ## Refactoring Complete ✅
        
        - **Initial Grade:** C (72/100)
        - **Final Grade:** A (95/100)
        - **Improvement:** +23 points
        - **Iterations:** 4
        - **Complexity:** 28 → 8 (-71%)
        
        [View full metrics →](...)
        """
        await self.client.add_comment(pr_number, comment)
```

#### 3. NotificationService (New)

Sends alerts when PR is ready

```python
class NotificationService:
    async def notify_pr_created(self, 
                               pr: PullRequest,
                               metrics: Dict,
                               team: List[str]) -> None:
        """Send notifications when PR created."""
        
        # GitHub: Already notified via PR assignment
        
        # Slack: Post formatted message
        slack_message = {
            "text": "🚀 Code Refactoring PR Ready for Review",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{pr.title}*\n{metrics['description']}"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Review PR"},
                            "url": pr.html_url
                        }
                    ]
                }
            ]
        }
        await self.slack.post_message("#code-refactoring", slack_message)
        
        # Email: Send formatted email
        await self.email.send(
            to=team,
            subject=f"[CodePulse] PR Ready: {pr.title}",
            html=render_template("pr_notification.html", pr=pr, metrics=metrics)
        )
    
    async def notify_pr_status(self, 
                              pr_number: int,
                              status: str) -> None:
        """Notify team of PR status changes (merged, approved, etc)."""
        # Similar flow as notify_pr_created
        pass
```

#### 4. DiffGenerator (New)

Generates character-level diffs with highlighting

```python
class DiffGenerator:
    def generate_diff(self, original: str, refactored: str) -> Diff:
        """Generate side-by-side diff with line types."""
        
        differ = difflib.SequenceMatcher(None, original, refactored)
        
        diff_result = Diff(
            additions=[],    # New lines
            deletions=[],    # Removed lines
            modifications=[] # Changed lines
        )
        
        for tag, i1, i2, j1, j2 in differ.get_opcodes():
            if tag == 'insert':
                for line in refactored.split('\n')[j1:j2]:
                    diff_result.additions.append({
                        'line': line,
                        'line_number': j1 + 1,
                        'type': 'addition'
                    })
            elif tag == 'delete':
                for line in original.split('\n')[i1:i2]:
                    diff_result.deletions.append({
                        'line': line,
                        'line_number': i1 + 1,
                        'type': 'deletion'
                    })
            elif tag == 'replace':
                diff_result.modifications.append({
                    'original': original.split('\n')[i1:i2],
                    'refactored': refactored.split('\n')[j1:j2],
                    'type': 'modification'
                })
        
        return diff_result
```

---

### Frontend Components

#### 1. RefactoringLounge (Main Dashboard)

Central hub for refactoring workflow

```typescript
// pages/RefactoringLounge.tsx

interface RefactoringLoungeProps {
  jobId: string;
}

export function RefactoringLounge({ jobId }: RefactoringLoungeProps) {
  const [status, setStatus] = useState<JobStatus>(null);
  const [selectedFile, setSelectedFile] = useState<string>(null);
  
  useEffect(() => {
    // WebSocket subscription to real-time updates
    const ws = new WebSocket(`ws://localhost:8000/api/v1/iteration/${jobId}/ws`);
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      setStatus(update);
    };
  }, [jobId]);
  
  return (
    <div className="refactoring-lounge">
      <header>
        <h1>🔄 Refactoring in Progress</h1>
        <ProgressTracker status={status} />
      </header>
      
      <main>
        <aside>
          <FileBrowser 
            jobId={jobId}
            onSelectFile={setSelectedFile}
          />
        </aside>
        
        <section>
          {selectedFile && (
            <DiffViewer
              jobId={jobId}
              filePath={selectedFile}
            />
          )}
        </section>
        
        <aside>
          <IterationHistory status={status} />
          <MetricsPanel status={status} />
          <CreatePRButton jobId={jobId} status={status} />
        </aside>
      </main>
    </div>
  );
}
```

**Layout:**
```
┌──────────────────────────────────────────────────────┐
│ 🔄 Refactoring in Progress | Grade: B → A | 3/10    │
├─────────────┬──────────────────────┬─────────────────┤
│ Files (23)  │                      │                 │
│  ├─ scanner │   scanner.py         │ Iteration 1/3:  │
│  ├─ analysis                       │ ✅ Extract      │
│  ├─ utils   │ - def analyze():     │ methods         │
│             │   (complex...)       │                 │
│             │                      │ Issues: 23→18   │
│             │ + def analyze_x():   │                 │
│             │   (simple)           │ Grade: C→B-     │
│             │                      │                 │
│             │ + def analyze_y():   │ ___________     │
│             │   (simple)           │ [Create PR]     │
├─────────────┴──────────────────────┴─────────────────┤
│ Metrics: Complexity 28→8 | Coverage 65%→89%          │
└──────────────────────────────────────────────────────┘
```

#### 2. FileBrowser Component

Tree view of files with severity badges

```typescript
// components/FileBrowser.tsx

interface FileBrowserProps {
  jobId: string;
  onSelectFile: (path: string) => void;
}

interface FileNode {
  path: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  issuesCount: number;
  linesChanged: number;
}

export function FileBrowser({ jobId, onSelectFile }: FileBrowserProps) {
  const [files, setFiles] = useState<FileNode[]>([]);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  
  useEffect(() => {
    // Fetch files from /api/v1/iteration/{job_id}/files
    fetchFiles(jobId).then(setFiles);
  }, [jobId]);
  
  const handleFileClick = (path: string) => {
    onSelectFile(path);
  };
  
  return (
    <div className="file-browser">
      <h3>Files to Refactor ({files.length})</h3>
      
      {files.map(file => (
        <div 
          key={file.path}
          className={`file-item severity-${file.severity}`}
          onClick={() => handleFileClick(file.path)}
        >
          <span className="severity-badge">
            {file.severity.charAt(0).toUpperCase()}
          </span>
          <span className="path">{file.path}</span>
          <span className="meta">
            {file.issuesCount} issues | {file.linesChanged} lines
          </span>
        </div>
      ))}
    </div>
  );
}
```

**Styling:**
```css
.severity-critical { background: #fee; border-left: 4px solid #c33; }
.severity-high    { background: #ffe; border-left: 4px solid #fa0; }
.severity-medium  { background: #eef; border-left: 4px solid #06f; }
.severity-low     { background: #efe; border-left: 4px solid #0a0; }
```

#### 3. DiffViewer Component

Side-by-side code comparison with highlighting

```typescript
// components/DiffViewer.tsx

interface DiffViewerProps {
  jobId: string;
  filePath: string;
}

interface CodeLine {
  type: 'addition' | 'deletion' | 'modification' | 'context';
  original?: string;
  refactored?: string;
  lineNumberOrig?: number;
  lineNumberRef?: number;
}

export function DiffViewer({ jobId, filePath }: DiffViewerProps) {
  const [diff, setDiff] = useState<CodeLine[]>([]);
  
  useEffect(() => {
    // Fetch diff from /api/v1/iteration/{job_id}/diff
    fetchDiff(jobId, filePath).then(setDiff);
  }, [jobId, filePath]);
  
  return (
    <div className="diff-viewer">
      <div className="diff-header">
        <span className="file-path">{filePath}</span>
        <button>Download Patch</button>
      </div>
      
      <div className="diff-content">
        <table>
          <tbody>
            {diff.map((line, idx) => (
              <tr key={idx} className={`diff-line diff-${line.type}`}>
                <td className="line-num original">{line.lineNumberOrig}</td>
                <td className="code original">
                  <code>{line.original}</code>
                </td>
                
                <td className="line-num refactored">{line.lineNumberRef}</td>
                <td className="code refactored">
                  <code>{line.refactored}</code>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

**Styling:**
```css
.diff-line.diff-addition .code.refactored { background: #efe; }
.diff-line.diff-deletion .code.original   { background: #fee; }
.diff-line.diff-modification .code       { background: #ffe; }

/* Inline highlighting */
.diff-addition { color: #0a0; }
.diff-deletion { color: #a00; }
```

#### 4. ProgressTracker Component

Real-time iteration status display

```typescript
// components/ProgressTracker.tsx

interface ProgressTrackerProps {
  status: JobStatus;
}

export function ProgressTracker({ status }: ProgressTrackerProps) {
  if (!status) return <div>Loading...</div>;
  
  const progressPercent = (status.currentIteration / status.maxIterations) * 100;
  
  return (
    <div className="progress-tracker">
      <div className="grade-display">
        <div className="grade current">{status.currentGrade}</div>
        <div className="arrow">→</div>
        <div className="grade target">{status.targetGrade}</div>
      </div>
      
      <div className="progress-bar">
        <div 
          className="progress-fill"
          style={{ width: `${progressPercent}%` }}
        >
          {status.currentIteration}/{status.maxIterations}
        </div>
      </div>
      
      <div className="metrics-mini">
        <span>Issues: {status.issuesRemaining}</span>
        <span>Complexity: {status.complexityReduction}%</span>
        <span>Coverage: {status.testCoverage}%</span>
      </div>
    </div>
  );
}
```

---

### API Endpoints (New for Phase 4)

#### GET /api/v1/iteration/{job_id}/files

**List files that need refactoring**

```json
{
  "files": [
    {
      "path": "scanner.py",
      "severity": "critical",
      "issues_count": 12,
      "lines_changed": 145,
      "metrics": {
        "complexity": 28,
        "duplication": 45
      }
    },
    ...
  ]
}
```

#### GET /api/v1/iteration/{job_id}/diff?file={filepath}

**Get side-by-side diff for a file**

```json
{
  "file_path": "scanner.py",
  "original_lines": 250,
  "refactored_lines": 180,
  "additions": 45,
  "deletions": 115,
  "diff_lines": [
    {
      "type": "context",
      "original": "def analyze_code():",
      "refactored": "def analyze_code():",
      "line_number": 1
    },
    {
      "type": "deletion",
      "original": "    # Long complex function",
      "refactored": null,
      "line_number": 2
    },
    {
      "type": "addition",
      "original": null,
      "refactored": "    # Refactored into helpers",
      "line_number": 2
    }
  ]
}
```

#### WebSocket /api/v1/iteration/{job_id}/ws

**Real-time iteration updates**

```json
{
  "event": "iteration_completed",
  "data": {
    "iteration_number": 1,
    "grade_before": "C",
    "grade_after": "B-",
    "issues_fixed": 5,
    "agent_selected": "Agent A",
    "progress_percent": 10
  }
}
```

#### POST /api/v1/iteration/{job_id}/create-pr

**Create GitHub PR**

Request:
```json
{
  "branch_name": "refactor/codepulse-20260606",
  "pr_title": "Refactor: Reduce code complexity from 28 to 8",
  "assignees": ["@user1", "@user2"],
  "labels": ["refactor", "auto-generated"]
}
```

Response:
```json
{
  "pr_number": 42,
  "pr_url": "https://github.com/owner/repo/pull/42",
  "branch": "refactor/codepulse-20260606",
  "status": "created"
}
```

---

## Implementation Breakdown

### Phase 4A: Backend (40-50 hours)

**Week 1:**

| Day | Task | Hours |
|-----|------|-------|
| Mon-Tue | GitHubService + OAuth setup | 10 |
| Wed | NotificationService (Slack + Email) | 10 |
| Thu-Fri | DiffGenerator + file list API | 10 |

**Week 2:**

| Day | Task | Hours |
|-----|------|-------|
| Mon-Tue | WebSocket integration | 10 |
| Wed-Thu | Testing & integration | 10 |

**Deliverables:**
- ✅ GitHubService with PR creation
- ✅ NotificationService with 3 channels
- ✅ DiffGenerator with character-level diffs
- ✅ 4 new REST endpoints
- ✅ WebSocket for real-time updates
- ✅ 20+ integration tests

---

### Phase 4B: Frontend (50-60 hours)

**Week 1:**

| Day | Task | Hours |
|-----|------|-------|
| Mon-Tue | Project setup + DiffViewer | 15 |
| Wed-Fri | FileBrowser + ProgressTracker | 15 |

**Week 2:**

| Day | Task | Hours |
|-----|------|-------|
| Mon-Tue | RefactoringLounge integration | 15 |
| Wed-Thu | Styling + polish | 15 |

**Stack:**
- React 18.x (TypeScript)
- TailwindCSS for styling
- Zustand for state management
- React Query for data fetching
- WebSocket client for real-time
- GitHub OAuth for authentication

**Deliverables:**
- ✅ 5 main React components
- ✅ Real-time WebSocket integration
- ✅ Responsive design (mobile-friendly)
- ✅ Dark/light mode
- ✅ 30+ UI tests

---

### Phase 4C: Integration & Testing (20-30 hours)

**Week 2-3:**

| Task | Hours |
|------|-------|
| E2E tests (full workflow) | 10 |
| Performance optimization | 5 |
| Documentation | 5 |
| CI/CD setup | 5 |
| Buffer/debugging | 5 |

**Deliverables:**
- ✅ End-to-end tests
- ✅ Performance benchmarks
- ✅ API documentation
- ✅ Frontend documentation
- ✅ Deployment guide

---

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| GitHub OAuth complexity | Medium | Medium | Use github.py library, test early |
| Real-time WebSocket lag | Low | High | Use Redis for message queue, test load |
| Diff generation performance | Medium | Medium | Cache diffs, use efficient difflib |
| Frontend complexity | High | Medium | Component library (headless UI), storybook |
| Integration testing difficulty | Medium | High | Local GitHub test account, docker compose |

---

## Success Criteria

✅ **Backend:**
- [ ] All 4 new REST endpoints working
- [ ] WebSocket streaming real-time updates
- [ ] GitHub PR created successfully
- [ ] Notifications sent to 3 channels
- [ ] 20+ integration tests passing

✅ **Frontend:**
- [ ] All 5 components rendering correctly
- [ ] Real-time updates flowing to UI
- [ ] Side-by-side diff viewer showing changes
- [ ] File browser with severity badges
- [ ] "Create PR" button creating actual PRs

✅ **Integration:**
- [ ] E2E test: Start job → View diff → Create PR → Verify on GitHub
- [ ] No regressions from Phase 3.5
- [ ] Performance: diff generation < 500ms
- [ ] WebSocket latency < 100ms

✅ **Documentation:**
- [ ] API reference for new endpoints
- [ ] Frontend component storybook
- [ ] Deployment guide for frontend + backend
- [ ] Architecture diagram updated

---

## Dependencies

**External Services:**
- GitHub API v3 (or GraphQL)
- Slack API (for notifications)
- Email service (SendGrid, SES, etc.)

**Frontend Dependencies:**
- React 18+
- TypeScript
- TailwindCSS
- React Query
- Zustand
- github.js (client)

**Backend Dependencies:**
- PyGithub (or httpx for GitHub API)
- aiosmtplib (for email)
- slack-sdk
- websockets
- redis (already in Phase 3.5)

---

## Phase 4 Features Summary

| Feature | MVP | Nice-to-Have |
|---------|-----|--------------|
| File browser | ✅ | - |
| Side-by-side diff | ✅ | Syntax highlighting |
| Real-time progress | ✅ | Progress graph |
| GitHub PR creation | ✅ | Auto-assign reviewers |
| Slack notifications | ✅ | Slack app integration |
| Email notifications | ✅ | Customizable templates |
| PR metrics comment | ✅ | PR status checks |

**MVP Focus:** Core workflow (view → create PR)
**Nice-to-Have:** Polish and advanced features

---

## Post-Phase 4 Ideas

- Mobile app for code review
- Advanced caching with Redis
- Multi-language support (Go, Rust, Java)
- Custom refactoring rules engine
- Machine learning pattern detection
- GraphQL API
- Advanced search/filtering
- Export reports (PDF, HTML)
- Team dashboard with aggregate metrics
- Integration with CI/CD pipelines

---

## Comparison: Before vs. After Phase 4

| Aspect | Before Phase 4 | After Phase 4 |
|--------|---|---|
| **Iteration Visibility** | REST polling only | Real-time dashboard |
| **Code Review** | Manual code reading | Visual diff viewer |
| **PR Creation** | Manual (copy/paste) | One-click automatic |
| **Team Communication** | Manual Slack posts | Auto-notifications |
| **Developer Experience** | CLI-only | Web UI + CLI |
| **Time to PR** | 15-30 minutes | 5 minutes |
| **Learning Curve** | High | Low |

---

## Go/No-Go Criteria for Phase 4

**Must-Have:**
- ✅ Phase 3.5 fully stable (no critical bugs)
- ✅ All Phase 3.5 tests passing
- ✅ 2+ developers available
- ✅ GitHub API access confirmed

**Nice-to-Have:**
- [ ] Design mockups pre-approved
- [ ] React expertise on team
- [ ] DevOps for frontend hosting

---

## Success Metrics (KPIs)

**After Phase 4 Launch:**
- **Time to refactored PR:** < 5 minutes vs. 15 min before
- **Team adoption:** > 50% of developers using UI
- **GitHub integration:** 100+ PRs created via CodePulse
- **Notification engagement:** 80%+ Slack notifications opened
- **Customer satisfaction:** NPS > 40

---

## Conclusion

Phase 4 completes the CodePulse AI product by wrapping Phase 3.5's powerful iteration engine in a **beautiful, intuitive interface** that teams will actually want to use daily.

**Status:** Ready for implementation  
**Timeline:** 2-3 weeks  
**Team:** 2 developers (1 backend, 1 frontend)  
**Effort:** 110-140 hours  

**Success Criteria:** Real-time visual refactoring dashboard + one-click GitHub PR creation

---

## Next Steps

1. ✅ Get approval on this plan
2. ✅ Design UI mockups (if not already done)
3. ✅ Set up GitHub OAuth application
4. ✅ Configure email/Slack services
5. ✅ Create React project template
6. ✅ Begin Phase 4A (Backend) development

**Phase 4 is ready to start when Phase 3.5 is declared stable!** 🚀

