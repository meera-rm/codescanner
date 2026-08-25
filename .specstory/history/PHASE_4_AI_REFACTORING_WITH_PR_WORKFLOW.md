---
created_at: 2026-06-12T18:16:43Z
title: Phase 4 Ai Refactoring With Pr Workflow
source: claude-code
project: codescanner
---

# Phase 4: AI Refactoring with PR Workflow & Line Highlighting

**Project:** CODEPULSE AI - Advanced Refactoring Interface  
**Phase:** 4 of 5+ (follows Phase 1-3 complete)  
**Status:** Planning  
**Date:** 2026-06-06

---

## Overview

Enhancement to AI Refactoring Service from Phase 3 to include:
1. **Visual Refactoring Interface** — Side-by-side code diff view
2. **Line Highlighting** — Highlight changed/refactored lines
3. **File Browser** — List all files needing refactoring with severity
4. **PR Workflow** — Create and push PRs to GitHub
5. **Team Notifications** — Notify via GitHub/Slack

---

## Part 1: AI Refactoring Interface

### Feature: File List with Refactoring Needs

**UI Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  AI REFACTORING LOUNGE                                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Files Needing Refactoring (23 total)                  │
│                                                         │
│  ┌──────────────────────────────────────┐              │
│  │ ❌ scanner/scanner.py (CRITICAL)     │  Severity   │
│  │    └─ Cyclomatic complexity: 28      │  ████████░  │
│  │    └─ Hardcoded secrets: 3           │              │
│  │    └─ God class: 45 methods          │              │
│  │                                      │              │
│  │ ⚠️  api/main.py (HIGH)               │  ██████░░░  │
│  │    └─ Long function: 120 lines       │              │
│  │    └─ Circular imports: 2            │              │
│  │                                      │              │
│  │ 🟡 scanner/caqi.py (MEDIUM)          │  ████░░░░░  │
│  │    └─ Code duplication: 45%          │              │
│  │    └─ Unused variables: 5            │              │
│  │                                      │              │
│  └──────────────────────────────────────┘              │
│                                                         │
│  Showing 1-10 of 23. [Load More]                       │
└─────────────────────────────────────────────────────────┘
```

**File Card Details:**
- File path + severity icon
- Top issues detected
- Risk score (0-100)
- File size
- Last modified date
- Refactoring impact estimate

**Sorting/Filtering:**
- By severity (Critical → Low)
- By issue type (complexity, duplication, smells)
- By file size
- By last modified

---

### Feature: Side-by-Side Code Diff View

**When User Clicks File:**

```
┌──────────────────────────────────────────────────────────────┐
│  REFACTORING: scanner/scanner.py                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Issue: Function 'analyze_code' has cyclomatic complexity 28 │
│  Severity: CRITICAL                                         │
│  Suggested Fix: Extract methods into separate functions     │
│  Risk Level: LOW                                            │
│  Estimated improvement: Complexity 28 → 8                   │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ORIGINAL CODE                 │  REFACTORED CODE            │
│  ────────────────────────────── │  ─────────────────────────  │
│                                │                            │
│  def analyze_code(code):       │  def analyze_code(code):    │
│    findings = []               │    findings = []            │
│    if os.path.exists(code):    │    if os.path.exists(code): │
│      ┌──────────────────┐      │      findings += check_...()│
│      │ with open as f:  │      │      findings += scan_...()│
│      │   data = f.read()│      │      findings += detect...()│
│      │   if len(data)>1│       │                            │
│      │    : ┌────────┐ │      │                            │
│      │      │for l in│ │      │ def _check_complexity(code)│
│      │      │ data   │ │      │   ...                      │
│      │      │  if    │ │      │                            │
│      │      │'secret'│ │      │ def _scan_for_issues(code) │
│      │      │ in l:  │ │      │   ...                      │
│      │      │  f.add │ │      │                            │
│      │      │ find() │ │      │ def _detect_patterns(code) │
│      │      └────────┘ │      │   ...                      │
│      │    elif bad_pat │      │                            │
│      │      : findings.│      │                            │
│      │      append()   │      │                            │
│      │    else: pass   │      │                            │
│      │  return findings│      │   return findings          │
│      └──────────────────┘      │                            │
│                                │                            │
│  ┌─ LINES 45-52 HIGHLIGHTED   │  ┌─ EXTRACTED TO 3 FUNC   │
│  │  (These will be removed)    │  │  (Lines 45-52 replaced) │
│  └─────────────────────────────┴──┴─────────────────────────┘
│                                                              │
│  Diff Stats: -18 lines, +42 lines (complexity reduction)    │
│                                                              │
│  [✓ Accept]  [✗ Reject]  [ⓘ Explain More]  [Preview]       │
└──────────────────────────────────────────────────────────────┘
```

**Features:**
- Side-by-side original ↔ refactored
- Syntax highlighting (matching IDE)
- Line numbers on both sides
- Diff summary (lines added/removed)
- Highlighted diff blocks (red boxes = removed, green boxes = added)
- Original lines that will be affected (boxed in red)
- New code sections (highlighted in green)

---

### Feature: Line Highlighting

**Mechanics:**
```javascript
// When user hovers over original code
- Highlight the specific lines being refactored (red background)
- Show arrows/lines connecting to refactored code (green)
- Show what changes (removed, moved, added)

// When user hovers over refactored code
- Show which original lines this came from
- Show new functionality added
- Show why this is better (complexity: 28→8)
```

**Visual Indicators:**
```
Lines to be refactored:
┌─ Line 45: ┌─────────────────┐
│           │ WILL BE REMOVED  │ ← Red background
│           └─────────────────┘
├─ Line 46-52: ┌──────────────────────────────┐
│              │ WILL BE EXTRACTED TO FUNCTION│ ← Orange
│              └──────────────────────────────┘

New code sections:
┌─ Line 12: ┌────────────────────────────────┐
│           │ NEW: Helper function created    │ ← Green background
│           └────────────────────────────────┘
└─ Line 15: ┌────────────────────────────────┐
            │ NEW: Error handling improved    │ ← Green
            └────────────────────────────────┘
```

---

## Part 2: GitHub PR Workflow

### Feature: Create Pull Request

**Flow:**

```
User clicks [Create PR] button
    ↓
System:
1. Create branch: `codepulse-refactor-{date}-{filename}`
2. Apply changes to local copy
3. Validate syntax (no new errors introduced)
4. Create commit with:
   - Message: "Refactor: {issue_type} in {filename}"
   - Body: Details of changes + metrics improvements
   - Author: Meera + CodePulse
5. Create PR on GitHub with:
   - Title: "Refactor: {issue_type} in {filename}"
   - Description: Before/after metrics + diff
   - Labels: refactor, codepulse, high-priority (if critical)
   - Assignees: Team members
6. Notify team
    ↓
PR Ready for Review
```

**PR Template:**

```markdown
## 🔧 Refactoring: {Issue Type}

**File:** `scanner/scanner.py`
**Severity:** CRITICAL
**Estimated Time to Review:** 5 minutes

### Issue
Function `analyze_code()` has cyclomatic complexity of 28, 
making it hard to test and maintain.

### Solution
Extract complex logic into 3 separate functions:
- `_check_complexity()` — Detect code complexity issues
- `_scan_for_issues()` — Scan for violations
- `_detect_patterns()` — Find unsafe patterns

### Metrics
- Cyclomatic Complexity: 28 → 8 ✅
- Test Coverage: Can now test each function independently
- Maintainability: +25% improvement

### Review Checklist
- [ ] Logic is correct and preserves functionality
- [ ] No new security issues introduced
- [ ] Code follows team conventions
- [ ] Tests updated/passing
- [ ] No performance regression

### Before & After
[Link to side-by-side diff in CodePulse UI]

Created by: CodePulse AI Refactoring Service
```

---

### Feature: Team Notifications

**GitHub Notifications:**
```
POST /repos/{owner}/{repo}/pulls
{
  "title": "Refactor: Reduce cyclomatic complexity in scanner.py",
  "body": "[PR template above]",
  "head": "codepulse-refactor-20260606-scanner",
  "base": "main",
  "assignees": ["meera-rm", "team-lead"],
  "labels": ["refactor", "high-priority"],
  "draft": true  // Start as draft for review
}
```

**Slack Notification (Optional):**
```
Message to #code-refactoring channel:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 CodePulse AI Refactoring

New PR ready for review:
📝 Refactor: Reduce cyclomatic complexity in scanner.py

📊 Metrics:
   • Complexity: 28 → 8 (-71%)
   • Functions extracted: 3
   • Risk level: LOW

👥 Assigned to: @meera-rm, @team-lead

🔗 Review: [Link to PR]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Email Notification:**
```
Subject: CodePulse: New refactoring PR waiting for review

Hi Team,

CodePulse AI has identified a critical refactoring opportunity
in scanner/scanner.py and created a PR for your review.

Issue: Cyclomatic complexity (28) - too high
Solution: Extract into 3 separate functions
Complexity: 28 → 8 (-71%)
Risk Level: LOW

👉 Review PR: [GitHub Link]

CodePulse AI
```

---

## Part 3: Implementation Plan

### Backend Changes (api/services/refactoring_service.py)

**New Methods:**

```python
class RefactoringService:
    
    def get_refactoring_files(self, 
                            job_id: str,
                            min_severity: str = "medium") -> List[Dict]:
        """Get all files needing refactoring."""
        # Query database for RefactorSuggestion entries
        # Group by file
        # Calculate severity per file
        # Return list with: file, severity, issues, metrics
    
    def generate_detailed_diff(self,
                              filepath: str,
                              suggestion_id: str) -> Dict:
        """Generate side-by-side diff for UI."""
        # Get original code from file
        # Get suggested code from suggestion
        # Generate diff
        # Calculate line-by-line changes
        # Return: original_lines, refactored_lines, changed_ranges
    
    def create_github_pr(self,
                        filepath: str,
                        suggestion: RefactorSuggestion,
                        repo_url: str,
                        assignees: List[str]) -> Dict:
        """Create PR on GitHub."""
        # Validate suggestion
        # Create branch
        # Apply changes
        # Create commit
        # Create PR
        # Return: pr_url, pr_number, branch_name
    
    def validate_refactored_code(self,
                                code: str,
                                original_code: str) -> Dict:
        """Validate refactored code doesn't introduce errors."""
        # Check syntax
        # Check imports still work
        # Check no regression
        # Return: is_valid, errors, warnings
```

### API Endpoints (api/routes/analysis.py)

**New Endpoints:**

```python
@router.get("/refactor/files")
async def get_refactoring_files(req: Request, 
                                job_id: str,
                                min_severity: str = "medium"):
    """Get all files needing refactoring."""
    # Returns list of files with severity, issues, metrics
    
@router.get("/refactor/file/{filepath}/diff")
async def get_refactor_diff(req: Request,
                           job_id: str,
                           filepath: str,
                           suggestion_id: str):
    """Get side-by-side diff for a refactoring."""
    # Returns: original_code, refactored_code, changes
    
@router.post("/refactor/create-pr")
async def create_pr(req: Request,
                   filepath: str,
                   suggestion_id: str,
                   repo_url: str,
                   github_token: str,
                   assignees: List[str]):
    """Create PR for refactoring."""
    # Returns: pr_url, branch_name, pr_number
    
@router.post("/refactor/accept")
async def accept_refactoring(req: Request,
                            filepath: str,
                            suggestion_id: str):
    """Accept refactoring and apply locally."""
    # Apply changes to file
    # Return success
    
@router.post("/refactor/reject")
async def reject_refactoring(req: Request,
                            suggestion_id: str,
                            reason: str = None):
    """Reject refactoring suggestion."""
    # Mark as rejected in database
    # Return success
```

### Frontend Components (React UI)

**Component: RefactoringLounge.tsx**

```typescript
interface RefactoringFile {
  filepath: string;
  severity: "critical" | "high" | "medium" | "low";
  issues: string[];
  metricsImprovement: {
    before: number;
    after: number;
  };
  riskLevel: "low" | "medium" | "high";
}

interface RefactorDiff {
  originalCode: string[];
  refactoredCode: string[];
  changedRanges: {
    original: [start: number, end: number];
    refactored: [start: number, end: number];
  }[];
}

export function RefactoringLounge() {
  const [files, setFiles] = useState<RefactoringFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<RefactoringFile | null>(null);
  const [diff, setDiff] = useState<RefactorDiff | null>(null);
  
  // Load files needing refactoring
  useEffect(() => {
    fetchRefactoringFiles();
  }, []);
  
  // When file selected, load diff
  const handleFileClick = (file: RefactoringFile) => {
    setSelectedFile(file);
    fetchDiff(file.filepath);
  };
  
  // Create PR workflow
  const handleCreatePR = async () => {
    const response = await createPullRequest({
      filepath: selectedFile!.filepath,
      assignees: [...],
      repo: repo
    });
    showNotification(`PR created: ${response.pr_url}`);
  };
  
  return (
    <div className="refactoring-lounge">
      <FileList 
        files={files}
        onSelectFile={handleFileClick}
      />
      {selectedFile && (
        <DiffViewer
          originalCode={diff?.originalCode}
          refactoredCode={diff?.refactoredCode}
          changedLines={diff?.changedRanges}
          onAccept={handleAcceptRefactor}
          onCreatePR={handleCreatePR}
          onReject={handleRejectRefactor}
        />
      )}
    </div>
  );
}
```

**Component: FileBrowser.tsx**

```typescript
export function FileBrowser({ files, onSelectFile }) {
  return (
    <div className="file-browser">
      {files.map(file => (
        <div 
          key={file.filepath}
          className="file-card"
          onClick={() => onSelectFile(file)}
        >
          <SeverityBadge severity={file.severity} />
          <FilePath path={file.filepath} />
          <IssuesList issues={file.issues} />
          <MetricsImprovement 
            before={file.metricsImprovement.before}
            after={file.metricsImprovement.after}
          />
          <RiskIndicator risk={file.riskLevel} />
        </div>
      ))}
    </div>
  );
}
```

**Component: DiffViewer.tsx**

```typescript
export function DiffViewer({ 
  originalCode, 
  refactoredCode, 
  changedLines,
  onAccept,
  onCreatePR,
  onReject
}) {
  return (
    <div className="diff-viewer">
      <div className="diff-header">
        <h2>Refactoring Review</h2>
        <div className="issue-summary">
          <Issue title="..." severity="..." />
        </div>
      </div>
      
      <div className="diff-container">
        <CodePanel 
          title="Original Code"
          code={originalCode}
          highlightedLines={changedLines.original}
          color="red"
        />
        
        <CodePanel 
          title="Refactored Code"
          code={refactoredCode}
          highlightedLines={changedLines.refactored}
          color="green"
        />
      </div>
      
      <div className="diff-stats">
        <Stat label="Lines removed" value="-18" />
        <Stat label="Lines added" value="+42" />
        <Stat label="Complexity reduction" value="-71%" />
      </div>
      
      <div className="actions">
        <Button onClick={onAccept} variant="success">
          ✓ Accept Refactoring
        </Button>
        <Button onClick={onCreatePR} variant="primary">
          💾 Create Pull Request
        </Button>
        <Button onClick={onReject} variant="secondary">
          ✗ Reject
        </Button>
      </div>
    </div>
  );
}
```

---

## Part 4: GitHub Integration

### Required Setup

**1. GitHub Token**
```env
GITHUB_TOKEN=ghp_...
GITHUB_REPO_OWNER=meera-rm
GITHUB_REPO_NAME=codescanner
```

**2. Dependencies to Add**
```python
# requirements.txt
PyGithub==1.58.0  # GitHub API wrapper
```

**3. Environment Variables**
```python
# api/config.py
github_token = os.getenv("GITHUB_TOKEN")
github_owner = os.getenv("GITHUB_REPO_OWNER", "meera-rm")
github_repo = os.getenv("GITHUB_REPO_NAME", "codescanner")
```

### PR Creation Logic

```python
from github import Github

class GitHubService:
    def __init__(self, token: str, owner: str, repo: str):
        self.g = Github(token)
        self.repo = self.g.get_user(owner).get_repo(repo)
    
    def create_refactor_pr(self,
                         filepath: str,
                         original_code: str,
                         refactored_code: str,
                         issues: List[str],
                         severity: str) -> str:
        """Create PR for refactoring."""
        
        # Create branch
        branch_name = f"codepulse-refactor-{datetime.now().strftime('%Y%m%d')}-{filename_safe}"
        main_branch = self.repo.get_branch("main")
        self.repo.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=main_branch.commit.sha
        )
        
        # Create commit
        self.repo.update_file(
            path=filepath,
            message=f"Refactor: {severity} issue in {filepath}",
            content=refactored_code,
            branch=branch_name,
            sha=self.repo.get_contents(filepath).sha
        )
        
        # Create PR
        pr = self.repo.create_pull(
            title=f"Refactor: Fix {issues[0]} in {filepath}",
            body=self._create_pr_body(filepath, issues, original_code, refactored_code),
            head=branch_name,
            base="main"
        )
        
        return pr.html_url
    
    def _create_pr_body(self, filepath, issues, original, refactored) -> str:
        """Generate PR description."""
        return f"""
## 🔧 Refactoring: {issues[0]}

**File:** `{filepath}`
**Issues Found:** {len(issues)}
**Severity:** HIGH

### Problems
{chr(10).join([f"- {issue}" for issue in issues])}

### Solution
[Refactored code with improvements]

### Before
```python
{original[:200]}...
```

### After
```python
{refactored[:200]}...
```

### Metrics
- Cyclomatic Complexity: 28 → 8 (-71%)
- Maintainability: +25%
- Risk Level: LOW

🤖 Created by CodePulse AI Refactoring Service
"""
```

---

## Part 5: Timeline & Effort

### Implementation Phases

**Phase 4A: Backend (40-50 hours)**
- [ ] Extend RefactoringService (10 hours)
- [ ] Create GitHubService (10 hours)
- [ ] Add new API endpoints (10 hours)
- [ ] Implement PR creation workflow (10 hours)
- [ ] Write integration tests (10 hours)

**Phase 4B: Frontend (50-60 hours)**
- [ ] Build RefactoringLounge component (15 hours)
- [ ] Build FileBrowser component (10 hours)
- [ ] Build DiffViewer component (15 hours)
- [ ] Implement line highlighting (10 hours)
- [ ] Add styling/animations (10 hours)

**Phase 4C: Integration (20-30 hours)**
- [ ] Connect frontend to backend (10 hours)
- [ ] GitHub integration testing (10 hours)
- [ ] PR notification system (5 hours)
- [ ] End-to-end testing (5 hours)

**Total Estimate: 110-140 hours (2-3 weeks with 2 developers)**

---

## Part 6: Success Criteria

✅ **Backend**
- Get list of files needing refactoring
- Generate side-by-side diffs
- Create GitHub PRs programmatically
- Validate refactored code
- Handle errors gracefully

✅ **Frontend**
- Display refactoring opportunities (file list)
- Show side-by-side diffs
- Highlight changed lines (color-coded)
- Accept/reject/create PR buttons
- Show metrics improvements

✅ **GitHub Integration**
- Create branches automatically
- Push refactored code
- Create PRs with proper descriptions
- Assign reviewers
- Add labels/severity

✅ **Notifications**
- GitHub PR notifications
- Slack/email notifications (optional)
- Team member assignments

---

## Part 7: Architecture

```
User clicks file in Refactoring Lounge
    ↓
Frontend: GET /api/v1/analysis/refactor/file/{filepath}/diff
    ↓
Backend: RefactoringService.generate_detailed_diff()
    ↓
Returns: { originalCode, refactoredCode, changedLines }
    ↓
Frontend: DiffViewer displays side-by-side with highlighting
    ↓
User clicks "Create PR"
    ↓
Frontend: POST /api/v1/analysis/refactor/create-pr
    ↓
Backend: GitHubService.create_refactor_pr()
    ├─ Creates branch
    ├─ Applies changes
    ├─ Creates commit
    ├─ Creates PR
    └─ Returns PR URL
    ↓
Frontend: Shows success + link to PR
    ↓
GitHub: Notifications sent to assignees
```

---

## Part 8: Example Use Case

```
1. User analyzes codebase with CodePulse
2. System finds 23 files needing refactoring
3. User opens "Refactoring Lounge"
4. Sees list: scanner.py (CRITICAL), api/main.py (HIGH), etc.
5. Clicks scanner.py
6. Side-by-side diff appears:
   - Left: Original code (cyclomatic complexity 28)
   - Right: Refactored code (complexity 8)
   - Red highlight: Code to be removed
   - Green highlight: New extracted functions
7. User reviews diff
8. Clicks "Create Pull Request"
9. PR created on GitHub:
   - Branch: codepulse-refactor-20260606-scanner
   - Assigned to: @meera-rm
   - Label: high-priority
   - Description: Shows metrics improvement
10. Slack notification sent to #code-refactoring
11. Team reviews PR, approves, merges
12. Complexity issue resolved automatically
```

---

## Conclusion

This Phase 4 feature transforms CodePulse from "suggesting refactors" to "automating refactoring with team review".

**Status: PLANNING PHASE**

Next: Implement Phase 4A (Backend) when ready.

See also:
- `CODEPULSE_AI_FEATURE_SET.md` — Full feature roadmap
- `PHASE_3_ADVANCED_FEATURES_IMPLEMENTATION_COMPLETE.md` — Phase 3 details
- `CODE_SCANNER_DEVELOPMENT.md` — Project journey
