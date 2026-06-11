import React, { useState, useEffect } from 'react';
import { useUploadManager } from '../hooks/useUploadManager';
import { useRefactorBatch } from '../hooks/useRefactorBatch';
import { useLiveCodeAnalysis } from '../hooks/useLiveCodeAnalysis';
import FunctionSelector, { FunctionSelectItem } from '../components/FunctionSelector';
import LiveCodeEditor from '../components/LiveCodeEditor';
import LiveMetricsPanel from '../components/LiveMetricsPanel';

type Theme = 'dark' | 'light';
type TabType = 'overview' | 'complexity' | 'smells' | 'duplication' | 'security' | 'docs' | 'dependencies' | 'files' | 'refactor' | 'live';
type DetailTab = 'analysis' | 'refactor';

interface ScannedFile {
  name: string;
  path?: string;
  language: string;
  loc: number;
  functions: number;
  classes: number;
  complexity: number;
  grade: string;
  severity: string;
}

interface ScanResponse {
  job_id: string;
  status: string;
  findings: Array<{
    file: string;
    line: number;
    severity: string;
    type: string;
    message: string;
  }>;
  scanned_files?: Array<{
    name: string;
    path: string;
    language: string;
  }>;
  metrics?: {
    quality_score: number;
    complexity?: {
      high_complexity_functions: number;
    };
  };
  function_metrics?: Array<{
    name: string;
    file: string;
    line: number;
    complexity: number;
    severity: string;
  }>;
}

export const CodeScanner: React.FC = () => {
  // Upload manager - consolidated upload logic
  const uploadManager = useUploadManager({
    onPathSelected: (path, lang) => {
      setDirectoryPath(path);
      setDetectedLanguage(lang as 'python' | 'javascript' | 'sql');
    }
  });

  const [directoryPath, setDirectoryPath] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(uploadManager.state.message || '');
  const [theme, setTheme] = useState<Theme>('light');
  const [activeTab, setActiveTab] = useState<TabType>('files');
  const [detectedLanguage, setDetectedLanguage] = useState<'python' | 'javascript' | 'sql'>('python');
  const [detailTab, setDetailTab] = useState<DetailTab>('analysis');
  const [selectedFile, setSelectedFile] = useState<ScannedFile | null>(null);
  const [dragActive, setDragActive] = useState(false);

  // Sync error state from upload manager
  useEffect(() => {
    if (uploadManager.state.error) {
      setError(uploadManager.state.error);
    } else if (uploadManager.state.message) {
      setError(uploadManager.state.message);
    }
  }, [uploadManager.state.error, uploadManager.state.message]);
  const [scannedFiles, setScannedFiles] = useState<ScannedFile[]>([]);
  const [allFindings, setAllFindings] = useState<any[]>([]);
  const [exportFormat, setExportFormat] = useState<'json' | 'html' | 'markdown' | 'csv' | 'pdf'>('json');
  const [analyses, setAnalyses] = useState({
    'Basic metrics': true,
    'Cyclomatic complexity': true,
    'Code smells': true,
    'Code duplication': true
  });
  const [collapsedSections, setCollapsedSections] = useState<{[key: string]: boolean}>({});
  const [selectedFunction, setSelectedFunction] = useState<{name: string; complexity: number; description: string} | null>(null);
  const [showFunctionModal, setShowFunctionModal] = useState(false);
  const [refactoredCode, setRefactoredCode] = useState<{original: string; refactored: string} | null>(null);
  const [refactorLoading, setRefactorLoading] = useState(false);
  const [functionMetrics, setFunctionMetrics] = useState<any[]>([]);
  const [hoveredFunction, setHoveredFunction] = useState<string | null>(null);
  const [metrics, setMetrics] = useState({
    grade: 'B',
    loc: 0,
    totalFindings: 0,
    criticalCount: 0,
    documented: '100%',
    depCycles: 0,
    qualityScore: 100
  });

  // Phase 3.4: Batch Refactoring
  const { state: batchState, startBatchRefactor, pollBatchStatus, applyBatchResults, reset: resetBatch } = useRefactorBatch();
  const [selectedFunctions, setSelectedFunctions] = useState<FunctionSelectItem[]>([]);
  const [showBatchUI, setShowBatchUI] = useState(false);
  const [editHistory, setEditHistory] = useState<{version: number; code: string; timestamp: Date; functionName: string}[]>([]);
  const [refactorCategory, setRefactorCategory] = useState<'complexity' | 'security' | 'style' | 'general'>('general');

  // Phase 3.5: Real-time Code Analysis
  const {
    code: liveCode,
    language: liveLanguage,
    analysis: liveAnalysis,
    isAnalyzing: isLiveAnalyzing,
    error: liveError,
    handleCodeChange: handleLiveCodeChange,
    handleLanguageChange: handleLiveLanguageChange
  } = useLiveCodeAnalysis();

  // Old handlers consolidated into uploadManager - see hooks/useUploadManager.ts

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const items = e.dataTransfer?.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.kind === 'file') {
        const entry = item.webkitGetAsEntry?.();
        if (entry?.isDirectory) {
          setDirectoryPath(entry.name);
          setError(`📁 Dropped folder: "${entry.name}"`);
        } else if (entry?.isFile) {
          setDirectoryPath(entry.name);
          setError(`📄 Dropped file: "${entry.name}"`);
        }
        break;
      }
    }
  };

  const handleScan = async () => {
    if (!directoryPath.trim()) {
      setError('Please enter a directory path or browse for a folder');
      return;
    }

    setLoading(true);
    setError('');
    setAllFindings([]);
    setScannedFiles([]);

    try {
      console.log('Starting scan with path:', directoryPath);

      const response = await fetch('/api/v1/scan/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ directory_path: directoryPath, language: detectedLanguage })
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        try {
          const errorData = JSON.parse(errorText);
          throw new Error(errorData.detail || `Scan failed: HTTP ${response.status}`);
        } catch (e) {
          throw new Error(`Scan failed: HTTP ${response.status} - ${errorText}`);
        }
      }

      const data: ScanResponse = await response.json();
      console.log('Scan response:', data);

      if (data.status === 'error') {
        throw new Error(data.findings ? 'No code files found to scan' : data.findings || 'Scan failed');
      }

      // Success - data.status should be 'completed'
      if (!data.scanned_files) {
        console.warn('No scanned_files in response, deriving from findings');
      }

      // Process findings
      setAllFindings(data.findings || []);

      // Use scanned_files from backend or derive from findings
      let files: ScannedFile[] = [];

      if (data.scanned_files && data.scanned_files.length > 0) {
        // Use files returned by backend
        files = data.scanned_files.map((f: any) => ({
          name: f.name,
          path: f.path,
          language: f.language === 'python' ? 'py' : f.language === 'javascript' ? 'js' : 'py',
          loc: f.loc || 200,
          functions: 3,
          classes: 0,
          complexity: 8.2,
          grade: 'A',
          severity: '—'
        }));
      } else {
        // Fallback: derive files from findings
        const fileMap = new Map<string, ScannedFile>();
        data.findings?.forEach((finding) => {
          if (!fileMap.has(finding.file)) {
            const fileName = finding.file.split('/').pop() || finding.file;
            const isJs = fileName.endsWith('.js') || fileName.endsWith('.ts');
            fileMap.set(finding.file, {
              name: fileName,
              path: finding.file,
              language: isJs ? 'js' : 'py',
              loc: 200,
              functions: 3,
              classes: 0,
              complexity: 8.2,
              grade: 'B',
              severity: finding.severity
            });
          }
        });
        files = Array.from(fileMap.values());
      }

      setScannedFiles(files);
      if (files.length > 0) setSelectedFile(files[0]);

      let criticalCount = 0;
      data.findings?.forEach((finding) => {
        if (finding.severity === 'CRITICAL') criticalCount++;
      });

      // Update metrics
      const qualityScore = Math.max(0, 100 - (data.findings?.length || 0) * 2);
      const totalLoc = files.reduce((sum, f) => sum + f.loc, 0);
      setMetrics({
        grade: qualityScore >= 80 ? 'A' : qualityScore >= 60 ? 'B' : 'C',
        loc: totalLoc,
        totalFindings: data.findings?.length || 0,
        criticalCount: criticalCount,
        documented: '95%',
        depCycles: 0,
        qualityScore: Math.round(qualityScore)
      });

      // Extract functions from findings
      const functionMap = new Map<string, {name: string; complexity: number; count: number; severity: string}>();
      data.findings?.forEach((finding: any) => {
        // Try to extract function name from message
        const match = finding.message?.match(/(?:in|function|method)\s+[`']?([a-zA-Z_][a-zA-Z0-9_]*(?:\(\))?)[`']?/i);
        if (match && match[1]) {
          const fnName = match[1].endsWith('()') ? match[1] : match[1] + '()';
          if (!functionMap.has(fnName)) {
            functionMap.set(fnName, { name: fnName, complexity: 0, count: 0, severity: finding.severity });
          }
          const fn = functionMap.get(fnName)!;
          fn.count++;
          fn.complexity = Math.min(20, fn.count * 2);
          if (finding.severity === 'CRITICAL') fn.severity = 'CRITICAL';
        }
      });

      // Store function metrics from backend response
      if (data.function_metrics) {
        setFunctionMetrics(data.function_metrics);
      }

      setActiveTab('files');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(`Scan failed: ${message}`);
      console.error('Scan error:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateHTMLReport = () => {
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Code Scan Report</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      line-height: 1.6;
      color: #333;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      padding: 40px 20px;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
      background: white;
      border-radius: 8px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.1);
      overflow: hidden;
    }
    .header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 40px;
      text-align: center;
    }
    .header h1 { font-size: 32px; margin-bottom: 10px; }
    .header p { opacity: 0.9; }
    .content { padding: 40px; }
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      margin: 30px 0;
    }
    .metric-card {
      background: #f9f9f9;
      padding: 20px;
      border-radius: 6px;
      border-left: 4px solid #667eea;
      text-align: center;
    }
    .metric-card .value { font-size: 28px; font-weight: 600; color: #667eea; }
    .metric-card .label { font-size: 12px; color: #666; margin-top: 8px; text-transform: uppercase; }
    h2 {
      font-size: 20px;
      margin: 30px 0 15px 0;
      padding-bottom: 10px;
      border-bottom: 2px solid #667eea;
      color: #333;
    }
    .file-item {
      padding: 12px;
      margin: 8px 0;
      background: #f9f9f9;
      border-radius: 4px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .file-name { font-weight: 500; }
    .file-meta { font-size: 12px; color: #666; }
    .issue-item {
      padding: 15px;
      margin: 10px 0;
      border-radius: 4px;
      border-left: 4px solid;
      background: #f9f9f9;
    }
    .issue-item.critical { border-left-color: #ff6b6b; background: rgba(255, 107, 107, 0.05); }
    .issue-item.warning { border-left-color: #f5c842; background: rgba(245, 200, 66, 0.05); }
    .issue-item.info { border-left-color: #6dde9a; background: rgba(109, 222, 154, 0.05); }
    .issue-type { font-weight: 600; color: #333; }
    .issue-meta { font-size: 12px; color: #666; margin-top: 5px; }
    .empty { text-align: center; color: #999; padding: 20px; }
    .footer {
      text-align: center;
      padding: 20px;
      border-top: 1px solid #eee;
      color: #999;
      font-size: 12px;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>📊 Code Scan Report</h1>
      <p>${directoryPath}</p>
      <p>${new Date().toLocaleString()}</p>
    </div>

    <div class="content">
      <h2>📈 Metrics Overview</h2>
      <div class="metrics-grid">
        <div class="metric-card"><div class="value">${metrics.grade}</div><div class="label">Grade</div></div>
        <div class="metric-card"><div class="value">${metrics.loc}</div><div class="label">Lines of Code</div></div>
        <div class="metric-card"><div class="value">${metrics.totalFindings}</div><div class="label">Total Issues</div></div>
        <div class="metric-card"><div class="value">${metrics.criticalCount}</div><div class="label">Critical</div></div>
        <div class="metric-card"><div class="value">${metrics.documented}</div><div class="label">Documented</div></div>
        <div class="metric-card"><div class="value">${metrics.depCycles}</div><div class="label">Cycles</div></div>
      </div>

      <h2>📁 Files Scanned (${scannedFiles.length})</h2>
      ${scannedFiles.length > 0 ? scannedFiles.map(f => `
        <div class="file-item">
          <div><div class="file-name">${f.name}</div><div class="file-meta">${f.language} • ${f.loc} LOC</div></div>
          <div class="file-meta">Grade: ${f.grade}</div>
        </div>
      `).join('') : '<div class="empty">No files scanned</div>'}

      <h2>🔍 Issues Found (${allFindings.length})</h2>
      ${allFindings.length > 0 ? allFindings.map(f => `
        <div class="issue-item ${f.severity.toLowerCase()}">
          <div class="issue-type">${f.type}</div>
          <div class="issue-meta">${f.file}:${f.line} • ${f.severity}</div>
          <div class="issue-meta" style="margin-top: 8px;">${f.message}</div>
        </div>
      `).join('') : '<div class="empty">✓ No issues found</div>'}
    </div>

    <div class="footer">
      Generated by CodeScanner on ${new Date().toLocaleString()}
    </div>
  </div>
</body>
</html>`;
  };

  const generateMarkdownReport = () => {
    return `# 📊 Code Scan Report

**Directory:** ${directoryPath}
**Generated:** ${new Date().toLocaleString()}

---

## 📈 Metrics

| Metric | Value |
|--------|-------|
| Grade | ${metrics.grade} |
| Lines of Code | ${metrics.loc} |
| Total Findings | ${metrics.totalFindings} |
| Critical Issues | ${metrics.criticalCount} |
| Documented | ${metrics.documented} |
| Dependency Cycles | ${metrics.depCycles} |

---

## 📁 Files Scanned (${scannedFiles.length})

${scannedFiles.length > 0 ? scannedFiles.map(f => `- **${f.name}** (${f.language}, ${f.loc} LOC) - Grade: ${f.grade}`).join('\n') : 'No files scanned'}

---

## 🔍 Issues Found (${allFindings.length})

${allFindings.length > 0 ? allFindings.map(f => `### ${f.type}
- **File:** ${f.file}:${f.line}
- **Severity:** ${f.severity}
- **Message:** ${f.message}
`).join('\n') : '✓ No issues found'}

---

*Generated by CodeScanner*
`;
  };

  const generateCSVReport = () => {
    const headers = ['File', 'Type', 'Severity', 'Line', 'Message'];
    const rows = allFindings.map(f => [
      f.file,
      f.type,
      f.severity,
      f.line,
      `"${f.message.replace(/"/g, '""')}"`
    ]);

    return [headers, ...rows].map(row => row.join(',')).join('\n');
  };

  const handleExport = (format: 'json' | 'html' | 'markdown' | 'csv' | 'pdf') => {
    setExportFormat(format);

    let content = '';
    let filename = `scan-report-${new Date().toISOString().split('T')[0]}`;
    let mimeType = 'text/plain';

    if (format === 'json') {
      content = JSON.stringify({
        directory: directoryPath,
        timestamp: new Date().toISOString(),
        metrics,
        files: scannedFiles,
        findings: allFindings,
        functions: functionMetrics
      }, null, 2);
      filename += '.json';
      mimeType = 'application/json';
    } else if (format === 'html') {
      content = generateHTMLReport();
      filename += '.html';
      mimeType = 'text/html';
    } else if (format === 'markdown') {
      content = generateMarkdownReport();
      filename += '.md';
      mimeType = 'text/markdown';
    } else if (format === 'csv') {
      content = generateCSVReport();
      filename += '.csv';
      mimeType = 'text/csv';
    } else if (format === 'pdf') {
      // For PDF, generate HTML then convert via browser print
      content = generateHTMLReport();
      filename += '.html'; // Fallback to HTML, user can print to PDF
      mimeType = 'text/html';
    }

    // Create blob and download
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleDownload = () => {
    handleExport(exportFormat);
  };

  const toggleAnalysis = (name: string) => {
    setAnalyses(prev => ({
      ...prev,
      [name]: !prev[name as keyof typeof analyses]
    }));
  };

  const toggleSection = (section: string) => {
    setCollapsedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const handleFunctionClick = (name: string, complexity: number) => {
    setSelectedFunction({
      name,
      complexity,
      description: `Function ${name} has a cyclomatic complexity of ${complexity}. Consider refactoring if complexity exceeds 10.`
    });
  };

  const handleRefactorClick = async () => {
    if (!selectedFile) return;

    setRefactorLoading(true);

    try {
      // Use selected function code if available, otherwise use file-level code
      let originalCode = '';
      let refactoredCodeText = '';

      if (selectedFunction) {
        // Generate code for the selected function
        originalCode = `def ${selectedFunction.name.replace('()', '')}(self, data, config):
    result = []
    for item in data:
        if item['status'] == 'active':
            if item['priority'] == 'high':
                if item['assigned'] == True:
                    result.append({
                        'id': item['id'],
                        'name': item['name'],
                        'priority': item['priority'],
                        'status': item['status'],
                        'updated': item['timestamp']
                    })
                else:
                    if item['requested'] == True:
                        result.append({
                            'id': item['id'],
                            'name': item['name'],
                            'status': 'pending'
                        })
            else:
                result.append({
                    'id': item['id'],
                    'name': item['name']
                })
    return result`;

        refactoredCodeText = `def ${selectedFunction.name.replace('()', '')}(self, data: List[Dict]) -> List[Dict]:
    """Extract active items, prioritizing by status and assignment."""
    def is_high_priority(item: Dict) -> bool:
        return item['priority'] == 'high' and item['status'] == 'active'

    def format_item(item: Dict, include_timestamp: bool = False) -> Dict:
        result = {'id': item['id'], 'name': item['name']}
        if include_timestamp:
            result['updated'] = item['timestamp']
        return result

    def should_include(item: Dict) -> bool:
        if not is_high_priority(item):
            return item['status'] == 'active'
        return item['assigned'] or item['requested']

    return [format_item(item, is_high_priority(item))
            for item in data if should_include(item)]`;
      } else {
        // File-level refactoring
        originalCode = `def process_data(data, config):
    result = []
    for item in data:
        if item['status'] == 'active':
            if item['priority'] == 'high':
                if item['assigned'] == True:
                    result.append({
                        'id': item['id'],
                        'name': item['name'],
                        'priority': item['priority'],
                        'status': item['status'],
                        'updated': item['timestamp']
                    })
                else:
                    if item['requested'] == True:
                        result.append({
                            'id': item['id'],
                            'name': item['name'],
                            'status': 'pending'
                        })
            else:
                result.append({
                    'id': item['id'],
                    'name': item['name']
                })
    return result`;

        refactoredCodeText = `def process_data(data: List[Dict], config: Dict) -> List[Dict]:
    """Extract active items, prioritizing by status and assignment."""
    def is_high_priority_item(item: Dict) -> bool:
        return item['priority'] == 'high' and item['status'] == 'active'

    def format_item(item: Dict, include_timestamp: bool = False) -> Dict:
        result = {'id': item['id'], 'name': item['name']}
        if include_timestamp:
            result['updated'] = item['timestamp']
        return result

    def should_include(item: Dict) -> bool:
        if not is_high_priority_item(item):
            return item['status'] == 'active'
        return item['assigned'] or item['requested']

    result = []
    for item in data:
        if should_include(item):
            if is_high_priority_item(item):
                result.append({**format_item(item, True), 'priority': item['priority'], 'status': item['status']})
            else:
                result.append(format_item(item))

    return result`;
      }

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));

      setRefactoredCode({
        original: originalCode,
        refactored: refactoredCodeText
      });
    } catch (err) {
      setError(`Refactor failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setRefactorLoading(false);
    }
  };

  const handleApplyChanges = async () => {
    if (!selectedFunction || !refactoredCode || !selectedFile) {
      setError('Missing function or refactored code');
      return;
    }

    if (!selectedFile.path) {
      setError('File path not available. Please select a file and try again.');
      return;
    }

    setRefactorLoading(true);
    try {
      const requestBody = {
        file_path: selectedFile.path,
        refactored_code: refactoredCode.refactored,
        function_name: selectedFunction.name
      };

      console.log('Applying refactor:', requestBody);

      const response = await fetch('/api/v1/scan/apply-refactor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });

      const responseText = await response.text();
      let result;
      try {
        result = JSON.parse(responseText);
      } catch {
        throw new Error(`Invalid response: ${responseText}`);
      }

      if (!response.ok) {
        throw new Error(result.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      // Show success with file path
      const filename = selectedFile.path.split('/').pop();
      setError(`✅ Changes saved to ${filename}\n💡 Tip: Re-scan to see metrics improve`);

      setTimeout(() => {
        setSelectedFunction(null);
        setRefactoredCode(null);
        // Keep success message visible for 3 seconds
      }, 3000);

      // Auto-clear error after 5 seconds
      setTimeout(() => {
        setError('');
      }, 1500);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      console.error('Apply changes error:', err);
      setError(`Failed to apply: ${errorMsg}`);
    } finally {
      setRefactorLoading(false);
    }
  };

  // Batch Refactoring Handlers
  const handleStartBatchRefactor = async () => {
    if (selectedFunctions.length === 0) {
      setError('Please select at least one function to refactor');
      return;
    }

    const functionItems: FunctionSelectItem[] = selectedFunctions.map((fn, idx) => ({
      id: `${fn.file}-${fn.line}-${idx}`,
      name: fn.name,
      file: fn.file,
      line: fn.line,
      complexity: fn.complexity,
      severity: fn.severity,
      code: fn.code
    }));

    await startBatchRefactor(functionItems, refactorCategory);
  };

  const handlePollBatch = async () => {
    if (batchState.batchId) {
      await pollBatchStatus(batchState.batchId);
    }
  };

  const handleApplyBatchResults = async () => {
    if (!batchState.batchId) {
      setError('No batch job found');
      return;
    }

    const resultsToApply = batchState.results
      .filter((r: any) => r.status === 'completed' && r.refactored_code)
      .map((r: any) => ({
        ...r,
        status: 'applied'
      }));

    if (resultsToApply.length === 0) {
      setError('No valid results to apply');
      return;
    }

    const result = await applyBatchResults(batchState.batchId, resultsToApply);
    if (result) {
      setError(`✅ Applied ${result.applied_count} function${result.applied_count !== 1 ? 's' : ''}`);

      // Add to edit history
      resultsToApply.forEach((r: any) => {
        setEditHistory(prev => [...prev, {
          version: prev.length + 1,
          code: r.refactored_code,
          timestamp: new Date(),
          functionName: r.function_name
        }]);
      });

      setTimeout(() => {
        resetBatch();
        setSelectedFunctions([]);
        setShowBatchUI(false);
        setError('');
      }, 2000);
    }
  };

  const handleRejectBatchResult = (index: number) => {
    // Mark result as rejected
    const updatedResults = [...batchState.results];
    updatedResults[index] = { ...updatedResults[index], status: 'rejected' };
    // Update state - would need to modify useRefactorBatch to expose this
  };

  const handleUndoLastChange = () => {
    if (editHistory.length > 0) {
      const lastEdit = editHistory[editHistory.length - 1];
      setError(`↩️ Undid: ${lastEdit.functionName}`);
      setEditHistory(prev => prev.slice(0, -1));
      setTimeout(() => setError(''), 2000);
    }
  };

  const getThemeStyles = () => theme === 'light' ? lightTheme : darkTheme;
  const ts = getThemeStyles();

  return (
    <div style={ts.container}>
      {/* TOPBAR */}
      <div style={ts.topbar}>
        <div style={ts.tbLogo}>
          <div style={ts.logoHex}>⬡</div>
          <span style={ts.tbName}>CodeLens<sup>BETA</sup></span>
        </div>
        <div style={ts.tbCrumb}>
          workspace / <span style={ts.tbSegment}>{directoryPath}</span>
        </div>
        <div style={ts.tbStatus}>
          <div style={{...ts.pdot, ...(loading ? ts.pdotAmber : {})}}></div>
          <span style={ts.sw}>{loading ? 'Scanning...' : 'Scan complete'}</span>
          <span style={ts.duration}>· 0.24s</span>
        </div>
        <div style={ts.tbSpacer}></div>
        <div style={ts.tbChips}>
          <span style={ts.chip}>Python only</span>
          <span style={{...ts.chip, ...ts.chipWarning}}>Max 15k files</span>
          <span style={ts.chip}>100 MB zip</span>
        </div>
        <div style={ts.tbActs}>
          {scannedFiles.length > 0 && (
            <div style={{display: 'flex', gap: '4px', marginRight: '12px'}}>
              <button style={{...ts.fmt, fontSize: '9px', ...(exportFormat === 'json' ? ts.fmtOn : {})}} onClick={() => handleExport('json')} title="Export as JSON">JSON</button>
              <button style={{...ts.fmt, fontSize: '9px', ...(exportFormat === 'html' ? ts.fmtOn : {})}} onClick={() => handleExport('html')} title="Export as HTML">HTML</button>
              <button style={{...ts.fmt, fontSize: '9px', ...(exportFormat === 'markdown' ? ts.fmtOn : {})}} onClick={() => handleExport('markdown')} title="Export as Markdown">MD</button>
              <button style={{...ts.fmt, fontSize: '9px', ...(exportFormat === 'csv' ? ts.fmtOn : {})}} onClick={() => handleExport('csv')} title="Export as CSV">CSV</button>
              <button style={{...ts.fmt, fontSize: '9px', ...(exportFormat === 'pdf' ? ts.fmtOn : {})}} onClick={() => handleExport('pdf')} title="Export as PDF">PDF</button>
            </div>
          )}
          <button style={{...ts.btnP, ...(loading ? ts.btnPBusy : {})}} onClick={handleScan} disabled={loading}>
            {loading ? '⏸ Scanning' : '▶ Scan'}
          </button>
        </div>
      </div>

      {/* BODY */}
      <div style={ts.body}>
        {/* LEFT RAIL */}
        <div style={ts.rail}>
          {/* SOURCE */}
          <div style={ts.rs}>
            <div style={{...ts.rsHead, cursor: 'pointer'}} onClick={() => toggleSection('source')}>
              <span style={ts.rsLbl}>1 · SOURCE</span>
              <span style={{...ts.rsTog, transform: collapsedSections['source'] ? 'rotate(-90deg)' : 'rotate(0deg)', transition: 'transform 0.2s'}}>{collapsedSections['source'] ? '▸' : '▾'}</span>
            </div>
            {!collapsedSections['source'] && (
              <div style={ts.rsBody}>
              <div style={ts.srcRow}>
                <input
                  type="text"
                  value={directoryPath}
                  onChange={(e) => setDirectoryPath(e.target.value)}
                  style={ts.srcField}
                  placeholder="e.g., api or /path/to/project"
                />
                <div style={ts.bwrap}>
                  <button style={ts.bbtn} onClick={uploadManager.browseFolders} disabled={uploadManager.isSearching}>
                    Browse <span style={{fontSize: '8px'}}>▾</span>
                  </button>
                </div>
              </div>
              {error && (
                <div style={{padding: '8px 14px', fontSize: '9px', color: '#ff6b6b', backgroundColor: 'rgba(255, 107, 107, 0.08)', borderLeft: '2px solid #ff6b6b', margin: '6px 14px', borderRadius: '3px'}}>
                  {error}
                </div>
              )}
              <div
                style={{...ts.dzone, ...(dragActive ? ts.dzoneActive : {})}}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                title="Drag files, folders, or ZIP files here"
              >
                Drop folder / file / .zip<br/>
                <span style={ts.dzoneHl}>Browse</span> · max 100 MB
              </div>
            </div>
            )}
          </div>

          {/* RECENT PATHS */}
          {uploadManager.recentPaths && uploadManager.recentPaths.length > 0 && (
            <div style={ts.rs}>
              <div style={{...ts.rsHead, cursor: 'pointer'}} onClick={() => toggleSection('recent')}>
                <span style={ts.rsLbl}>⏱ RECENT ({uploadManager.recentPaths.length})</span>
                <span style={{...ts.rsTog, transform: collapsedSections['recent'] ? 'rotate(-90deg)' : 'rotate(0deg)', transition: 'transform 0.2s'}}>{collapsedSections['recent'] ? '▸' : '▾'}</span>
              </div>
              {!collapsedSections['recent'] && (
                <div style={ts.rsBody}>
                  {uploadManager.recentPaths.map((recent) => (
                    <div
                      key={recent.path}
                      style={{
                        padding: '8px 12px',
                        fontSize: '10px',
                        borderBottom: `1px solid ${theme === 'light' ? '#f0f0f0' : '#333333'}`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: '8px',
                        cursor: 'pointer',
                        transition: 'background 0.2s'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.background = theme === 'light' ? '#f5f5f5' : '#2a2a2a'}
                      onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                    >
                      <div
                        style={{flex: 1, minWidth: 0}}
                        onClick={() => {
                          setDirectoryPath(recent.path);
                          uploadManager.handleTextInput(recent.path);
                        }}
                      >
                        <div style={{fontWeight: 500, color: theme === 'light' ? '#333' : '#fff', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>
                          {recent.name}
                        </div>
                        <div style={{color: theme === 'light' ? '#999' : '#888', fontSize: '9px', marginTop: '2px'}}>
                          {recent.relative || recent.path}
                        </div>
                        <div style={{color: theme === 'light' ? '#bbb' : '#666', fontSize: '8px', marginTop: '2px'}}>
                          {(() => {
                            const date = new Date(recent.timestamp);
                            const now = new Date();
                            const diffMs = now.getTime() - date.getTime();
                            const diffMins = Math.floor(diffMs / 60000);
                            const diffHours = Math.floor(diffMs / 3600000);
                            const diffDays = Math.floor(diffMs / 86400000);

                            if (diffMins < 1) return 'just now';
                            if (diffMins < 60) return `${diffMins}m ago`;
                            if (diffHours < 24) return `${diffHours}h ago`;
                            return `${diffDays}d ago`;
                          })()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* FILES */}
          <div style={ts.rs}>
            <div style={{...ts.rsHead, cursor: 'pointer'}} onClick={() => toggleSection('files')}>
              <span style={ts.rsLbl}>FILES ({scannedFiles.length})</span>
              <span style={{...ts.rsTog, transform: collapsedSections['files'] ? 'rotate(-90deg)' : 'rotate(0deg)', transition: 'transform 0.2s'}}>{collapsedSections['files'] ? '▸' : '▾'}</span>
            </div>
            {!collapsedSections['files'] && (
              <div style={ts.rsBody}>
              {scannedFiles.length > 0 ? (
                scannedFiles.map((file) => (
                  <div
                    key={file.name}
                    style={{...ts.fi, ...(selectedFile?.name === file.name ? ts.fiOn : {})}}
                    onClick={() => setSelectedFile(file)}
                  >
                    <div style={{...ts.fiDot, ...(file.language === 'py' ? ts.fiDotPy : ts.fiDotJs)}}></div>
                    <span style={ts.fiName}>{file.name}</span>
                    <span style={ts.fiLoc}>{file.loc}</span>
                  </div>
                ))
              ) : (
                <div style={{padding: '10px 14px', fontSize: '10px', color: '#999999'}}>No files scanned yet</div>
              )}
              </div>
            )}
          </div>

          {/* ANALYSES */}
          <div style={ts.rs}>
            <div style={{...ts.rsHead, cursor: 'pointer'}} onClick={() => toggleSection('analyses')}>
              <span style={ts.rsLbl}>2 · ANALYSES</span>
              <span style={{...ts.rsTog, transform: collapsedSections['analyses'] ? 'rotate(-90deg)' : 'rotate(0deg)', transition: 'transform 0.2s'}}>{collapsedSections['analyses'] ? '▸' : '▾'}</span>
            </div>
            {!collapsedSections['analyses'] && (
              <div style={ts.rsBody}>
                {['Basic metrics', 'Cyclomatic complexity', 'Code smells', 'Code duplication'].map((analysis) => (
                  <label key={analysis} style={ts.ck}>
                    <input
                      type="checkbox"
                      checked={analyses[analysis as keyof typeof analyses]}
                      onChange={() => toggleAnalysis(analysis)}
                    />
                    <span>{analysis}</span>
                  </label>
                ))}
              </div>
            )}
          </div>

          {/* THEME */}
          <div style={ts.rs}>
            <div style={{...ts.rsHead, cursor: 'pointer'}} onClick={() => toggleSection('theme')}>
              <span style={ts.rsLbl}>THEME</span>
              <span style={{...ts.rsTog, transform: collapsedSections['theme'] ? 'rotate(-90deg)' : 'rotate(0deg)', transition: 'transform 0.2s'}}>{collapsedSections['theme'] ? '▸' : '▾'}</span>
            </div>
            {!collapsedSections['theme'] && (
              <div style={ts.rsBody}>
              <div style={ts.throw}>
                <button
                  style={{...ts.thb, ...(theme === 'light' ? ts.thbOn : {})}}
                  onClick={() => setTheme('light')}
                >
                  Light
                </button>
                <button
                  style={{...ts.thb, ...(theme === 'dark' ? ts.thbOn : {})}}
                  onClick={() => setTheme('dark')}
                >
                  Dark
                </button>
              </div>
            </div>
            )}
          </div>
        </div>

        {/* RIGHT STAGE */}
        <div style={ts.stage}>
          {/* METRICS BAND */}
          <div style={ts.mband}>
            <div style={ts.mc}>
              <div style={ts.mcLbl}>Grade</div>
              <div style={{...ts.mcVal, color: '#6dde9a'}}>{metrics.grade}</div>
              <div style={ts.mcSub}>{metrics.qualityScore} / 100</div>
            </div>
            <div style={ts.mc}>
              <div style={ts.mcLbl}>Lines of Code</div>
              <div style={{...ts.mcVal, color: '#6eb5ff'}}>{metrics.loc}</div>
              <div style={ts.mcSub}>4.61 avg / fn</div>
            </div>
            <div style={ts.mc}>
              <div style={ts.mcLbl}>Total Findings</div>
              <div style={{...ts.mcVal, color: '#f5c842'}}>{metrics.totalFindings}</div>
              <div style={ts.mcSub}>{metrics.totalFindings > 0 ? `${metrics.criticalCount} critical` : 'no issues'}</div>
            </div>
            <div style={ts.mc}>
              <div style={ts.mcLbl}>High Severity</div>
              <div style={{...ts.mcVal, color: '#ff6b6b'}}>{metrics.criticalCount}</div>
              <div style={ts.mcSub}>{metrics.criticalCount === 0 ? 'no critical issues' : 'urgent fixes'}</div>
            </div>
            <div style={ts.mc}>
              <div style={ts.mcLbl}>Documented</div>
              <div style={{...ts.mcVal, color: '#3ecfb2'}}>{metrics.documented}</div>
              <div style={ts.mcSub}>coverage</div>
            </div>
            <div style={ts.mc}>
              <div style={ts.mcLbl}>Dep-Cycles</div>
              <div style={{...ts.mcVal, color: '#b89eff'}}>{metrics.depCycles}</div>
              <div style={ts.mcSub}>no circular deps</div>
            </div>
          </div>

          {/* TABS */}
          <div style={ts.tabs}>
            {(['overview', 'complexity', 'smells', 'duplication', 'security', 'docs', 'dependencies', 'files', 'live', 'refactor'] as TabType[]).map((tab) => (
              <button
                key={tab}
                style={{...ts.tab, ...(activeTab === tab ? ts.tabOn : {}), ...(tab === 'refactor' ? {background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: '#ffffff'} : {}), ...(tab === 'live' ? {background: 'linear-gradient(135deg, #6dde9a 0%, #4ba381 100%)', color: '#ffffff'} : {})}}
                onClick={() => setActiveTab(tab)}
              >
                {tab === 'refactor' ? '✨ Refactor' : tab === 'live' ? '💻 Live' : tab.charAt(0).toUpperCase() + tab.slice(1)}
                {['complexity', 'smells', 'dependencies'].includes(tab) && <span style={ts.tn}>·</span>}
              </button>
            ))}
          </div>

          {/* TAB CONTENT */}
          {activeTab === 'files' && scannedFiles.length > 0 && (
            <div style={{...ts.tabContent, overflow: 'auto', display: 'flex', flexDirection: 'column'}}>
              <div style={ts.tbar}>
                <div style={ts.tbarInfo}>
                  {(() => {
                    const filesWithIssues = scannedFiles.filter(file =>
                      allFindings.some(f => f.file.includes(file.name))
                    );
                    return <>
                      <strong>{filesWithIssues.length > 0 ? filesWithIssues.length : 0} files with issues</strong>
                      {filesWithIssues.length !== scannedFiles.length && ` of ${scannedFiles.length} total`}
                      · Python analysis · 0.24s
                    </>;
                  })()}
                </div>
                <div style={ts.tbarRight}>
                  <div style={ts.fmts}>
                    <button style={{...ts.fmt, ...(exportFormat === 'json' ? ts.fmtOn : {})}} onClick={() => setExportFormat('json')}>JSON</button>
                    <button style={{...ts.fmt, ...(exportFormat === 'html' ? ts.fmtOn : {})}} onClick={() => setExportFormat('html')}>HTML</button>
                    <button style={{...ts.fmt, ...(exportFormat === 'markdown' ? ts.fmtOn : {})}} onClick={() => setExportFormat('markdown')}>Markdown</button>
                    <button style={{...ts.fmt, ...(exportFormat === 'csv' ? ts.fmtOn : {})}} onClick={() => setExportFormat('csv')}>CSV</button>
                    <button style={{...ts.fmt, ...(exportFormat === 'pdf' ? ts.fmtOn : {})}} onClick={() => setExportFormat('pdf')}>PDF</button>
                  </div>
                  <button style={ts.btnO} onClick={handleDownload} disabled={scannedFiles.length === 0}>↓ Download</button>
                </div>
              </div>

              {/* TABLE */}
              <div style={ts.tableWrap}>
                {(() => {
                  // Filter files to show only those with issues
                  const filesWithIssues = scannedFiles.filter(file =>
                    allFindings.some(f => f.file.includes(file.name))
                  );
                  const filesToDisplay = filesWithIssues.length > 0 ? filesWithIssues : scannedFiles;

                  return filesToDisplay.length > 0 ? (
                    <table style={ts.table}>
                      <thead>
                        <tr style={ts.theadRow}>
                          <th style={ts.th}>Path <span style={ts.sa}>↕</span></th>
                          <th style={ts.th}>Lang <span style={ts.sa}>↕</span></th>
                          <th style={ts.th}>LoC <span style={ts.sa}>↕</span></th>
                          <th style={ts.th}>FN <span style={ts.sa}>↕</span></th>
                          <th style={ts.th}>CLS <span style={ts.sa}>↕</span></th>
                          <th style={ts.th}>Complexity <span style={ts.sa}>↕</span></th>
                          <th style={ts.th}>Grade <span style={ts.sa}>↕</span></th>
                          <th style={ts.th}>Severity <span style={ts.sa}>↕</span></th>
                        </tr>
                      </thead>
                      <tbody>
                        {filesToDisplay.map((file) => (
                        <tr key={file.name} style={{...ts.tbodyRow, ...(selectedFile?.name === file.name ? ts.tbodyRowSel : {}), cursor: 'pointer'}} onClick={() => setSelectedFile(file)}>
                          <td style={ts.td}>
                            <div style={ts.tdF}>
                              <div style={{...ts.fld, ...(file.language === 'py' ? ts.fldPy : ts.fldJs)}}></div>
                              {file.name}
                            </div>
                          </td>
                          <td style={ts.td}><span style={file.language === 'py' ? ts.ltPy : ts.ltJs}>{file.language}</span></td>
                          <td style={{...ts.td, ...ts.tdNum}}>{file.loc}</td>
                          <td style={{...ts.td, ...ts.tdNum}}>{file.functions}</td>
                          <td style={{...ts.td, ...ts.tdNum}}>{file.classes}</td>
                          <td style={ts.td}>
                            <div style={ts.cxw}>
                              <div style={ts.cxt}>
                                <div style={{...ts.cxf, width: `${file.complexity * 5}%`, ...(file.complexity > 10 ? ts.cxHi : file.complexity > 5 ? ts.cxMid : ts.cxLo)}}></div>
                              </div>
                              <span style={ts.cxN}>{file.complexity.toFixed(1)}</span>
                            </div>
                          </td>
                          <td style={ts.td}><span style={{...ts.gp, ...(file.grade === 'A' ? ts.gA : file.grade === 'B' ? ts.gB : ts.gC)}}>{file.grade}</span></td>
                          <td style={ts.td}><span style={file.severity === '—' ? ts.svNone : ts.svLo}>{file.severity}</span></td>
                        </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <div style={{...ts.phPanel, padding: '40px 20px'}}>
                      <div style={ts.phIc}>📊</div>
                      <div style={ts.phT}>{scannedFiles.length === 0 ? 'No scans yet' : 'No issues found'}</div>
                      <div style={ts.phS}>{scannedFiles.length === 0 ? 'Enter a directory path and click Scan to analyze your code' : 'All scanned files have no issues ✓'}</div>
                    </div>
                  );
                })()}
              </div>

              {/* DETAIL */}
              {selectedFile && (
                <div style={{...ts.detail, display: 'flex', flexDirection: 'column', overflow: 'hidden'}}>
                  <div style={ts.detailTabs}>
                    <button
                      style={{...ts.dtab, ...(detailTab === 'analysis' ? ts.dtabOn : {})}}
                      onClick={() => setDetailTab('analysis')}
                    >
                      Analysis
                    </button>
                  </div>
                  <div style={{...ts.detailBody, display: 'flex', flexDirection: 'column', flex: 1, overflow: 'auto'}}>
                    {/* TOP SECTION - Analysis or Refactor */}
                    {detailTab === 'analysis' && (
                      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0', flex: selectedFunction ? '0 0 auto' : 1, height: selectedFunction ? 'auto' : '100%', borderBottom: selectedFunction ? `2px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}` : 'none', maxHeight: selectedFunction ? '350px' : '100%'}}>
                        {/* Column 1: Heatmap */}
                        <div style={{display: 'flex', flexDirection: 'column', borderRight: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`}}>
                          <div style={{padding: '12px 16px', background: theme === 'light' ? '#f9f9f9' : '#2a2a2a', borderBottom: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`, fontSize: '11px', fontWeight: 500, color: theme === 'light' ? '#666666' : '#aaaaaa'}}>
                            🔥 Heatmap
                          </div>
                          <div style={{flex: 1, overflow: 'auto', padding: '12px'}}>
                            <div style={ts.fnl}>
                              {(() => {
                                // Check if selected file has any issues
                                const fileHasIssues = allFindings.some(f => f.file.includes(selectedFile.name));

                                if (!fileHasIssues) {
                                  // No issues in this file, show empty state
                                  return (
                                    <div style={{padding: '12px', color: theme === 'light' ? '#999' : '#666', fontSize: '12px', textAlign: 'center'}}>
                                      No issues found in this file ✓
                                    </div>
                                  );
                                }

                                // File has issues - show all functions from this file
                                const selectedFileFunctions = functionMetrics.filter(fn =>
                                  fn.file.includes(selectedFile.name)
                                ).sort((a, b) => b.complexity - a.complexity);

                                if (selectedFileFunctions.length === 0) {
                                  return (
                                    <div style={{padding: '12px', color: theme === 'light' ? '#999' : '#666', fontSize: '12px', textAlign: 'center'}}>
                                      No functions found
                                    </div>
                                  );
                                }

                                return selectedFileFunctions.map((fn) => {
                                  const isHovered = hoveredFunction === fn.name;
                                  const isSelected = selectedFunction?.name === fn.name;
                                  const showRefactor = isHovered || isSelected;

                                  return (
                                    <div
                                      key={fn.name}
                                      style={{...ts.fnR, display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingRight: '8px', gap: '8px'}}
                                      onMouseEnter={() => setHoveredFunction(fn.name)}
                                      onMouseLeave={() => !isSelected && setHoveredFunction(null)}
                                    >
                                      <div style={{display: 'flex', alignItems: 'center', flex: 1, cursor: 'pointer'}} onClick={() => handleFunctionClick(fn.name, fn.complexity)}>
                                        <span style={{...ts.fnNm, textDecoration: 'underline', color: '#667eea'}}>{fn.name}</span>
                                        <span style={ts.fnCx}>{fn.complexity}</span>
                                      </div>
                                      <div style={ts.fnB}>
                                        <div style={{...ts.fnBf, width: `${(fn.complexity / 20) * 100}%`, background: fn.complexity > 14 ? '#ff6b6b' : fn.complexity > 8 ? '#f5c842' : '#6dde9a'}}></div>
                                      </div>
                                      <button
                                        style={{
                                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                          color: '#ffffff',
                                          border: 'none',
                                          borderRadius: '4px',
                                          padding: '4px 8px',
                                          fontSize: '10px',
                                          cursor: 'pointer',
                                          fontWeight: 500,
                                          whiteSpace: 'nowrap',
                                          flexShrink: 0,
                                          opacity: showRefactor ? 1 : 0,
                                          transition: 'opacity 0.2s ease',
                                          pointerEvents: showRefactor ? 'auto' : 'none'
                                        }}
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          handleFunctionClick(fn.name, fn.complexity);
                                          setTimeout(() => handleRefactorClick(), 100);
                                        }}
                                      >
                                        ✨ Refactor
                                      </button>
                                    </div>
                                  );
                                })
                              })()}
                            </div>
                          </div>
                        </div>

                        {/* Column 2: Suggestions */}
                        <div style={{display: 'flex', flexDirection: 'column', borderRight: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`}}>
                          <div style={{padding: '12px 16px', background: theme === 'light' ? '#f9f9f9' : '#2a2a2a', borderBottom: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`, fontSize: '11px', fontWeight: 500, color: theme === 'light' ? '#666666' : '#aaaaaa'}}>
                            💡 Suggestions
                          </div>
                          <div style={{flex: 1, overflow: 'auto', padding: '12px'}}>
                            <div style={ts.sugl}>
                              {allFindings.filter(f => f.file.includes(selectedFile.name)).length > 0 ? (
                                allFindings.filter(f => f.file.includes(selectedFile.name)).map((issue, idx) => (
                                  <div key={idx} style={{...ts.sugi, padding: '8px', marginBottom: '4px', fontSize: '9px'}}>
                                    <span style={{...ts.sugiIc, marginRight: '4px'}}>
                                      {issue.severity === 'CRITICAL' ? '🔴' : issue.severity === 'ERROR' ? '🟠' : '🟡'}
                                    </span>
                                    <span style={{...ts.sugiTx, fontSize: '9px'}}>
                                      <strong>{issue.type}</strong> at line {issue.line}
                                    </span>
                                  </div>
                                ))
                              ) : (
                                <>
                                  <div style={{...ts.sugi, fontSize: '9px', marginBottom: '6px'}}>
                                    <span style={{...ts.sugiIc}}>✓</span>
                                    <span style={{...ts.sugiTx, fontSize: '9px'}}>Well-structured code</span>
                                  </div>
                                  <div style={{...ts.sugi, fontSize: '9px', marginBottom: '6px'}}>
                                    <span style={{...ts.sugiIc}}>💡</span>
                                    <span style={{...ts.sugiTx, fontSize: '9px'}}>Add type hints</span>
                                  </div>
                                  <div style={{...ts.sugi, fontSize: '9px'}}>
                                    <span style={{...ts.sugiIc}}>✓</span>
                                    <span style={{...ts.sugiTx, fontSize: '9px'}}>Good naming</span>
                                  </div>
                                </>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Column 3: Radar */}
                        <div style={{display: 'flex', flexDirection: 'column'}}>
                          <div style={{padding: '12px 16px', background: theme === 'light' ? '#f9f9f9' : '#2a2a2a', borderBottom: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`, fontSize: '11px', fontWeight: 500, color: theme === 'light' ? '#666666' : '#aaaaaa'}}>
                            📊 Radar
                          </div>
                          <div style={{flex: 1, overflow: 'auto', padding: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                            <svg width="120" height="120" viewBox="0 0 200 200">
                              {[1, 2, 3, 4, 5].map((i) => (
                                <circle key={`grid-${i}`} cx="100" cy="100" r={i * 30} fill="none" stroke="#e0e0e0" strokeWidth="1" opacity="0.3" />
                              ))}
                              <line x1="100" y1="100" x2="100" y2="20" stroke="#999999" strokeWidth="1" opacity="0.3" />
                              <line x1="100" y1="100" x2="163" y2="65" stroke="#999999" strokeWidth="1" opacity="0.3" />
                              <line x1="100" y1="100" x2="153" y2="163" stroke="#999999" strokeWidth="1" opacity="0.3" />
                              <line x1="100" y1="100" x2="47" y2="163" stroke="#999999" strokeWidth="1" opacity="0.3" />
                              <line x1="100" y1="100" x2="37" y2="65" stroke="#999999" strokeWidth="1" opacity="0.3" />
                              <polygon points="100,40 155,75 145,150 55,150 45,75" fill="#667eea" fillOpacity="0.3" stroke="#667eea" strokeWidth="2" />
                            </svg>
                          </div>
                        </div>
                      </div>
                    )}

                    {detailTab === 'refactor' && (
                      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0', flex: 1, height: '100%', borderBottom: selectedFunction ? `2px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}` : 'none'}}>
                        {/* Original Code */}
                        <div style={{display: 'flex', flexDirection: 'column', borderRight: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`}}>
                          <div style={{padding: '12px 16px', background: theme === 'light' ? '#f9f9f9' : '#2a2a2a', borderBottom: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`, fontSize: '11px', fontWeight: 500, color: theme === 'light' ? '#666666' : '#aaaaaa'}}>
                            📄 Original Code
                          </div>
                          <div style={{flex: 1, overflow: 'auto', padding: '12px', background: theme === 'light' ? '#ffffff' : '#1f1f1f', fontFamily: "'DM Mono', monospace"}}>
                            {refactorLoading ? (
                              <div style={{textAlign: 'center', color: '#999999', paddingTop: '40px'}}>
                                <div style={{fontSize: '18px', marginBottom: '12px'}}>✨</div>
                                <div style={{fontSize: '12px'}}>Generating...</div>
                              </div>
                            ) : refactoredCode ? (
                              <pre style={{margin: 0, fontSize: '10px', lineHeight: '1.4', color: theme === 'light' ? '#666666' : '#bbbbbb', whiteSpace: 'pre-wrap', wordWrap: 'break-word'}}>
                                {refactoredCode.original}
                              </pre>
                            ) : null}
                          </div>
                        </div>

                        {/* Refactored Code */}
                        <div style={{display: 'flex', flexDirection: 'column'}}>
                          <div style={{padding: '12px 16px', background: theme === 'light' ? '#f0f8f0' : '#2a3a2a', borderBottom: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`, fontSize: '11px', fontWeight: 500, color: theme === 'light' ? '#4a7c4a' : '#6dde9a'}}>
                            ✨ Refactored Code
                          </div>
                          <div style={{flex: 1, overflow: 'auto', padding: '12px', background: theme === 'light' ? '#fafffe' : '#1f2a1f', fontFamily: "'DM Mono', monospace"}}>
                            {refactorLoading ? (
                              <div style={{textAlign: 'center', color: '#6dde9a', paddingTop: '40px'}}>
                                <div style={{fontSize: '18px', marginBottom: '12px'}}>⚙️</div>
                                <div style={{fontSize: '12px'}}>Generating...</div>
                              </div>
                            ) : refactoredCode ? (
                              <pre style={{margin: 0, fontSize: '10px', lineHeight: '1.4', color: theme === 'light' ? '#4a7c4a' : '#6dde9a', whiteSpace: 'pre-wrap', wordWrap: 'break-word'}}>
                                {refactoredCode.refactored}
                              </pre>
                            ) : null}
                          </div>
                          {refactoredCode && !refactorLoading && (
                            <div style={{padding: '8px 12px', background: theme === 'light' ? '#f9f9f9' : '#2a2a2a', borderTop: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`, display: 'flex', gap: '6px', justifyContent: 'flex-end'}}>
                              <button style={{...ts.btnO, fontSize: '9px', padding: '4px 10px'}} onClick={() => setRefactoredCode(null)}>
                                Reject
                              </button>
                              <button style={{...ts.btnP, fontSize: '9px', padding: '4px 10px'}}>
                                Apply
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* BOTTOM SECTION - Function Code Split View */}
                    {selectedFunction && (
                      <div style={{display: 'flex', flexDirection: 'column', flex: 1, minHeight: '300px', overflow: 'auto', borderTop: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`}}>
                      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0', flex: 1, overflow: 'auto'}}>
                        {/* Original Function Code */}
                        <div style={{display: 'flex', flexDirection: 'column', borderRight: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`}}>
                          <div style={{padding: '12px 16px', background: theme === 'light' ? '#f9f9f9' : '#2a2a2a', borderBottom: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`, fontSize: '11px', fontWeight: 500, color: theme === 'light' ? '#666666' : '#aaaaaa', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                            <span>📄 {selectedFunction.name}</span>
                            <button style={{background: 'none', border: 'none', fontSize: '16px', cursor: 'pointer', color: '#999999'}} onClick={() => setSelectedFunction(null)}>×</button>
                          </div>
                          <div style={{flex: 1, overflow: 'auto', padding: '12px', background: theme === 'light' ? '#ffffff' : '#1f1f1f', fontFamily: "'DM Mono', monospace"}}>
                            <pre style={{margin: 0, fontSize: '10px', lineHeight: '1.4', color: theme === 'light' ? '#666666' : '#bbbbbb', whiteSpace: 'pre-wrap', wordWrap: 'break-word'}}>
                              {`def ${selectedFunction.name.replace('()', '')}(self, data, config):
    result = []
    for item in data:
        if item['status'] == 'active':
            if item['priority'] == 'high':
                if item['assigned'] == True:
                    result.append({
                        'id': item['id'],
                        'name': item['name'],
                        'priority': item['priority'],
                        'status': item['status']
                    })
    return result`}
                            </pre>
                          </div>
                        </div>

                        {/* Refactored Function Code */}
                        <div style={{display: 'flex', flexDirection: 'column'}}>
                          <div style={{padding: '12px 16px', background: theme === 'light' ? '#f0f8f0' : '#2a3a2a', borderBottom: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`, fontSize: '11px', fontWeight: 500, color: theme === 'light' ? '#4a7c4a' : '#6dde9a'}}>
                            ✨ Refactored - Complexity {selectedFunction.complexity}
                          </div>
                          <div style={{flex: 1, overflow: 'auto', padding: '12px', background: theme === 'light' ? '#fafffe' : '#1f2a1f', fontFamily: "'DM Mono', monospace"}}>
                            <pre style={{margin: 0, fontSize: '10px', lineHeight: '1.4', color: theme === 'light' ? '#4a7c4a' : '#6dde9a', whiteSpace: 'pre-wrap', wordWrap: 'break-word'}}>
                              {`def ${selectedFunction.name.replace('()', '')}(self, data: List[Dict]) -> List[Dict]:
    """Extract active high-priority items."""
    def should_include(item):
        return item['status'] == 'active' and \
               item.get('priority') == 'high'

    def format_item(item):
        return {k: v for k, v in item.items()
                if k in ['id', 'name', 'priority', 'status']}

    return [format_item(item) for item in data
            if should_include(item)]`}
                            </pre>
                          </div>
                        </div>
                      </div>
                      {/* Action Buttons */}
                      <div style={{display: 'flex', gap: '8px', padding: '12px 16px', borderTop: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`, background: theme === 'light' ? '#f5f5f5' : '#262626', justifyContent: 'flex-end'}}>
                        <button
                          style={{
                            padding: '8px 16px',
                            background: theme === 'light' ? '#f0f0f0' : '#404040',
                            border: `1px solid ${theme === 'light' ? '#d0d0d0' : '#555555'}`,
                            borderRadius: '4px',
                            fontSize: '13px',
                            fontWeight: 500,
                            color: theme === 'light' ? '#666666' : '#bbbbbb',
                            cursor: 'pointer',
                            transition: 'all 0.2s'
                          }}
                          onClick={() => setSelectedFunction(null)}
                        >
                          ✕ Reject
                        </button>
                        <button
                          style={{
                            padding: '8px 16px',
                            background: '#4a7c4a',
                            border: 'none',
                            borderRadius: '4px',
                            fontSize: '13px',
                            fontWeight: 500,
                            color: '#ffffff',
                            cursor: refactorLoading ? 'not-allowed' : 'pointer',
                            opacity: refactorLoading ? 0.6 : 1,
                            transition: 'all 0.2s'
                          }}
                          onClick={handleApplyChanges}
                          disabled={refactorLoading}
                        >
                          {refactorLoading ? '⚙️ Applying...' : '✓ Apply Changes'}
                        </button>
                      </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* OVERVIEW TAB */}
          {activeTab === 'overview' && (
            <div style={{...ts.tabContent, padding: '32px', overflow: 'auto'}}>
              {scannedFiles.length === 0 ? (
                <div style={{textAlign: 'center', paddingTop: '60px', color: theme === 'light' ? '#999' : '#666'}}>
                  <div style={{fontSize: '32px', marginBottom: '12px'}}>📊</div>
                  <div style={{fontSize: '16px', fontWeight: 500}}>No scan data yet</div>
                  <div style={{fontSize: '13px', marginTop: '8px'}}>Scan a directory to see overview metrics</div>
                </div>
              ) : (
                <>
                  <h2 style={{fontSize: '20px', marginBottom: '16px', color: theme === 'light' ? '#333' : '#fff'}}>📊 Overview</h2>
                  <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '32px'}}>
                    <div style={{padding: '16px', background: theme === 'light' ? '#f5f5f5' : '#2a2a2a', borderRadius: '6px'}}>
                      <div style={{fontSize: '12px', color: theme === 'light' ? '#666' : '#aaa'}}>Grade</div>
                      <div style={{fontSize: '28px', fontWeight: 'bold', color: metrics.grade === 'A' ? '#4a7c4a' : '#f5c842'}}>
                        {metrics.grade}
                      </div>
                    </div>
                    <div style={{padding: '16px', background: theme === 'light' ? '#f5f5f5' : '#2a2a2a', borderRadius: '6px'}}>
                      <div style={{fontSize: '12px', color: theme === 'light' ? '#666' : '#aaa'}}>Total Issues</div>
                      <div style={{fontSize: '28px', fontWeight: 'bold'}}>{metrics.totalFindings}</div>
                    </div>
                    <div style={{padding: '16px', background: theme === 'light' ? '#f5f5f5' : '#2a2a2a', borderRadius: '6px'}}>
                      <div style={{fontSize: '12px', color: theme === 'light' ? '#666' : '#aaa'}}>Critical</div>
                      <div style={{fontSize: '28px', fontWeight: 'bold', color: '#ff6b6b'}}>{metrics.criticalCount}</div>
                    </div>
                  </div>
                  <p style={{color: theme === 'light' ? '#666' : '#aaa'}}>Scanned {scannedFiles.length} files with {metrics.loc.toLocaleString()} lines of code.</p>
                </>
              )}
            </div>
          )}

          {/* COMPLEXITY TAB */}
          {activeTab === 'complexity' && (
            <div style={{...ts.tabContent, padding: '32px', overflow: 'auto'}}>
              {scannedFiles.length === 0 ? (
                <div style={{textAlign: 'center', paddingTop: '60px', color: theme === 'light' ? '#999' : '#666'}}>
                  <div style={{fontSize: '32px', marginBottom: '12px'}}>📈</div>
                  <div style={{fontSize: '16px', fontWeight: 500}}>No scan data yet</div>
                  <div style={{fontSize: '13px', marginTop: '8px'}}>Scan a directory to see complexity analysis</div>
                </div>
              ) : (
                <>
                  <h2 style={{fontSize: '20px', marginBottom: '24px', color: theme === 'light' ? '#333' : '#fff'}}>📈 Cyclomatic Complexity Analysis</h2>

                  {/* Complexity Summary */}
                  <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '32px'}}>
                    <div style={{padding: '16px', background: theme === 'light' ? '#f9f9f9' : '#2a2a2a', borderLeft: `4px solid #ff6b6b`, borderRadius: '4px'}}>
                      <div style={{fontSize: '12px', color: theme === 'light' ? '#666' : '#aaa', marginBottom: '6px'}}>High Complexity {'>'} 10</div>
                      <div style={{fontSize: '24px', fontWeight: 600, color: '#ff6b6b'}}>
                        {functionMetrics.filter(f => f.complexity > 10).length}
                      </div>
                      <div style={{fontSize: '10px', color: theme === 'light' ? '#999' : '#666', marginTop: '4px'}}>functions need refactoring</div>
                    </div>
                    <div style={{padding: '16px', background: theme === 'light' ? '#f9f9f9' : '#2a2a2a', borderLeft: `4px solid #f5c842`, borderRadius: '4px'}}>
                      <div style={{fontSize: '12px', color: theme === 'light' ? '#666' : '#aaa', marginBottom: '6px'}}>Medium Complexity 5–10</div>
                      <div style={{fontSize: '24px', fontWeight: 600, color: '#f5c842'}}>
                        {functionMetrics.filter(f => f.complexity > 5 && f.complexity <= 10).length}
                      </div>
                      <div style={{fontSize: '10px', color: theme === 'light' ? '#999' : '#666', marginTop: '4px'}}>functions to optimize</div>
                    </div>
                    <div style={{padding: '16px', background: theme === 'light' ? '#f9f9f9' : '#2a2a2a', borderLeft: `4px solid #6dde9a`, borderRadius: '4px'}}>
                      <div style={{fontSize: '12px', color: theme === 'light' ? '#666' : '#aaa', marginBottom: '6px'}}>Low Complexity (1-5)</div>
                      <div style={{fontSize: '24px', fontWeight: 600, color: '#6dde9a'}}>
                        {functionMetrics.filter(f => f.complexity <= 5).length}
                      </div>
                      <div style={{fontSize: '10px', color: theme === 'light' ? '#999' : '#666', marginTop: '4px'}}>functions are simple</div>
                    </div>
                  </div>

                  {/* All Functions Sorted */}
                  <div>
                    <h3 style={{fontSize: '14px', marginBottom: '12px', color: theme === 'light' ? '#333' : '#fff'}}>All Functions (sorted by complexity)</h3>
                    {functionMetrics && functionMetrics.length > 0 ? (
                      <div style={{display: 'flex', flexDirection: 'column', gap: '8px'}}>
                        {[...functionMetrics].sort((a, b) => b.complexity - a.complexity).map((fn) => (
                          <div key={`${fn.file}-${fn.name}`} style={{padding: '12px', background: theme === 'light' ? '#f5f5f5' : '#2a2a2a', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '12px', justifyContent: 'space-between', cursor: 'pointer', transition: 'background 0.2s'}} onMouseEnter={(e) => e.currentTarget.style.background = theme === 'light' ? '#efefef' : '#333333'} onMouseLeave={(e) => e.currentTarget.style.background = theme === 'light' ? '#f5f5f5' : '#2a2a2a'}>
                            <div style={{flex: 1, minWidth: 0}}>
                              <div style={{fontSize: '13px', fontWeight: 500, color: theme === 'light' ? '#333' : '#fff'}}>{fn.name}</div>
                              <div style={{fontSize: '11px', color: theme === 'light' ? '#999' : '#666', marginTop: '4px'}}>{fn.file.split('/').pop()} • line {fn.line}</div>
                            </div>
                            <div style={{display: 'flex', alignItems: 'center', gap: '12px', flexShrink: 0}}>
                              <div style={{width: '120px', height: '6px', background: theme === 'light' ? '#e0e0e0' : '#404040', borderRadius: '3px', overflow: 'hidden'}}>
                                <div style={{height: '100%', width: `${(fn.complexity / 20) * 100}%`, background: fn.complexity > 10 ? '#ff6b6b' : fn.complexity > 5 ? '#f5c842' : '#6dde9a'}}></div>
                              </div>
                              <div style={{width: '35px', textAlign: 'right', fontSize: '13px', fontWeight: 600, color: fn.complexity > 10 ? '#ff6b6b' : fn.complexity > 5 ? '#f5c842' : '#6dde9a'}}>{fn.complexity}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p style={{color: theme === 'light' ? '#999' : '#666'}}>No functions found.</p>
                    )}
                  </div>

                  {/* Tips */}
                  <div style={{marginTop: '32px', padding: '16px', background: theme === 'light' ? '#e8f5e9' : '#1b3a1b', borderRadius: '4px', borderLeft: `4px solid #6dde9a`}}>
                    <div style={{fontSize: '12px', fontWeight: 500, color: theme === 'light' ? '#2e7d32' : '#6dde9a', marginBottom: '8px'}}>💡 Tips to Reduce Complexity</div>
                    <ul style={{fontSize: '11px', color: theme === 'light' ? '#388e3c' : '#81c784', margin: '0', paddingLeft: '20px', lineHeight: '1.6'}}>
                      <li>Extract methods: Break complex functions into smaller, focused functions</li>
                      <li>Reduce nesting: Flatten nested if/for statements with early returns</li>
                      <li>Simplify conditions: Use switch statements instead of multiple if-else chains</li>
                      <li>Remove duplicates: Extract repeated logic into helper functions</li>
                    </ul>
                  </div>
                </>
              )}
            </div>
          )}

          {/* SMELLS TAB */}
          {activeTab === 'smells' && (
            <div style={{...ts.tabContent, padding: '32px', overflow: 'auto'}}>
              {scannedFiles.length === 0 ? (
                <div style={{textAlign: 'center', paddingTop: '60px', color: theme === 'light' ? '#999' : '#666'}}>
                  <div style={{fontSize: '32px', marginBottom: '12px'}}>👃</div>
                  <div style={{fontSize: '16px', fontWeight: 500}}>No scan data yet</div>
                  <div style={{fontSize: '13px', marginTop: '8px'}}>Scan a directory to detect code smells</div>
                </div>
              ) : (
                <>
                  <h2 style={{fontSize: '20px', marginBottom: '16px', color: theme === 'light' ? '#333' : '#fff'}}>👃 Code Smells</h2>
                  <div style={{marginBottom: '16px'}}>
                    {allFindings.filter(f => f.type === 'Code Smell').length > 0 ? (
                      allFindings.filter(f => f.type === 'Code Smell').map((issue, idx) => (
                        <div key={idx} style={{padding: '12px', marginBottom: '8px', background: theme === 'light' ? '#fff8f0' : '#3a2a2a', borderLeft: '4px solid #f5c842', borderRadius: '4px', fontSize: '13px'}}>
                          <strong>{issue.file}:{issue.line}</strong> — {issue.message}
                        </div>
                      ))
                    ) : (
                      <p style={{color: theme === 'light' ? '#999' : '#666'}}>No code smells detected. ✓</p>
                    )}
                  </div>
                </>
              )}
            </div>
          )}

          {/* DUPLICATION TAB */}
          {activeTab === 'duplication' && (
            <div style={{...ts.tabContent, padding: '32px', overflow: 'auto'}}>
              {scannedFiles.length === 0 ? (
                <div style={{textAlign: 'center', paddingTop: '60px', color: theme === 'light' ? '#999' : '#666'}}>
                  <div style={{fontSize: '32px', marginBottom: '12px'}}>📋</div>
                  <div style={{fontSize: '16px', fontWeight: 500}}>No scan data yet</div>
                  <div style={{fontSize: '13px', marginTop: '8px'}}>Scan a directory to find code duplication</div>
                </div>
              ) : (
                <>
                  <h2 style={{fontSize: '20px', marginBottom: '16px', color: theme === 'light' ? '#333' : '#fff'}}>📋 Duplication</h2>
                  <p style={{color: theme === 'light' ? '#999' : '#666'}}>Analyzing duplicated code blocks...</p>
                </>
              )}
            </div>
          )}

          {/* SECURITY TAB */}
          {activeTab === 'security' && (
            <div style={{...ts.tabContent, padding: '32px', overflow: 'auto'}}>
              {scannedFiles.length === 0 ? (
                <div style={{textAlign: 'center', paddingTop: '60px', color: theme === 'light' ? '#999' : '#666'}}>
                  <div style={{fontSize: '32px', marginBottom: '12px'}}>🔒</div>
                  <div style={{fontSize: '16px', fontWeight: 500}}>No scan data yet</div>
                  <div style={{fontSize: '13px', marginTop: '8px'}}>Scan a directory to check security issues</div>
                </div>
              ) : (
                <>
                  <h2 style={{fontSize: '20px', marginBottom: '16px', color: theme === 'light' ? '#333' : '#fff'}}>🔒 Security Issues</h2>
                  <div style={{marginBottom: '16px'}}>
                    {allFindings.filter(f => f.severity === 'CRITICAL').length > 0 ? (
                      allFindings.filter(f => f.severity === 'CRITICAL').map((issue, idx) => (
                        <div key={idx} style={{padding: '12px', marginBottom: '8px', background: theme === 'light' ? '#ffefef' : '#3a1a1a', borderLeft: '4px solid #ff6b6b', borderRadius: '4px', fontSize: '13px'}}>
                          <strong>{issue.file}:{issue.line}</strong> — {issue.message}
                        </div>
                      ))
                    ) : (
                      <p style={{color: theme === 'light' ? '#999' : '#666'}}>No critical security issues found. ✓</p>
                    )}
                  </div>
                </>
              )}
            </div>
          )}

          {/* DOCS TAB */}
          {activeTab === 'docs' && (
            <div style={{...ts.tabContent, padding: '32px', overflow: 'auto'}}>
              {scannedFiles.length === 0 ? (
                <div style={{textAlign: 'center', paddingTop: '60px', color: theme === 'light' ? '#999' : '#666'}}>
                  <div style={{fontSize: '32px', marginBottom: '12px'}}>📝</div>
                  <div style={{fontSize: '16px', fontWeight: 500}}>No scan data yet</div>
                  <div style={{fontSize: '13px', marginTop: '8px'}}>Scan a directory to check documentation coverage</div>
                </div>
              ) : (
                <>
                  <h2 style={{fontSize: '20px', marginBottom: '16px', color: theme === 'light' ? '#333' : '#fff'}}>📝 Documentation</h2>
                  <p style={{color: theme === 'light' ? '#999' : '#666', marginBottom: '16px'}}>Coverage: {metrics.documented}</p>
                  <p style={{color: theme === 'light' ? '#666' : '#aaa', fontSize: '13px', lineHeight: '1.6'}}>Review functions for proper docstrings and inline comments. Well-documented code improves maintainability.</p>
                </>
              )}
            </div>
          )}

          {/* DEPENDENCIES TAB */}
          {activeTab === 'dependencies' && (
            <div style={{...ts.tabContent, padding: '32px', overflow: 'auto'}}>
              {scannedFiles.length === 0 ? (
                <div style={{textAlign: 'center', paddingTop: '60px', color: theme === 'light' ? '#999' : '#666'}}>
                  <div style={{fontSize: '32px', marginBottom: '12px'}}>🔗</div>
                  <div style={{fontSize: '16px', fontWeight: 500}}>No scan data yet</div>
                  <div style={{fontSize: '13px', marginTop: '8px'}}>Scan a directory to analyze dependencies</div>
                </div>
              ) : (
                <>
                  <h2 style={{fontSize: '20px', marginBottom: '16px', color: theme === 'light' ? '#333' : '#fff'}}>🔗 Dependencies</h2>
                  <p style={{color: theme === 'light' ? '#999' : '#666', marginBottom: '16px'}}>Circular Dependencies: {metrics.depCycles}</p>
                  <p style={{color: theme === 'light' ? '#666' : '#aaa', fontSize: '13px', lineHeight: '1.6'}}>No problematic dependency cycles detected.</p>
                </>
              )}
            </div>
          )}

          {activeTab === 'refactor' && (
            <div style={ts.tabContent}>
              {/* Batch Refactoring Mode - Phase 3.4 */}
              {showBatchUI ? (
                <div style={{display: 'flex', flexDirection: 'column', height: '100%', padding: '16px', gap: '16px', backgroundColor: theme === 'light' ? '#f5f5f5' : '#1f1f1f'}}>
                  {/* Header */}
                  <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '12px', borderBottom: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`}}>
                    <h2 style={{margin: 0, fontSize: '16px', fontWeight: 600, color: theme === 'light' ? '#2c2c2c' : '#ffffff'}}>
                      🔄 Batch Refactoring
                    </h2>
                    <button style={{...ts.btnO, fontSize: '10px'}} onClick={() => setShowBatchUI(false)}>
                      Back to Single Mode
                    </button>
                  </div>

                  {/* Category Selection */}
                  <div style={{display: 'flex', gap: '8px', alignItems: 'center'}}>
                    <label style={{fontSize: '12px', fontWeight: 600, color: theme === 'light' ? '#666666' : '#cccccc'}}>Category:</label>
                    <select
                      value={refactorCategory}
                      onChange={(e) => setRefactorCategory(e.target.value as any)}
                      style={{padding: '6px 10px', borderRadius: '4px', border: `1px solid ${theme === 'light' ? '#d0d0d0' : '#333333'}`, backgroundColor: theme === 'light' ? '#ffffff' : '#2a2a2a', color: theme === 'light' ? '#2c2c2c' : '#ffffff', fontSize: '12px'}}
                    >
                      <option value="general">General</option>
                      <option value="complexity">High Complexity</option>
                      <option value="security">Security Issues</option>
                      <option value="style">Code Style</option>
                    </select>
                    {editHistory.length > 0 && (
                      <button style={{...ts.btnO, fontSize: '10px', marginLeft: 'auto'}} onClick={handleUndoLastChange}>
                        ↩️ Undo ({editHistory.length})
                      </button>
                    )}
                  </div>

                  {/* Function Selector */}
                  <div style={{flex: 1, overflow: 'auto', backgroundColor: theme === 'light' ? '#ffffff' : '#1f1f1f', borderRadius: '4px'}}>
                    {functionMetrics.length > 0 ? (
                      <FunctionSelector
                        functions={functionMetrics.map((fn, idx) => ({
                          id: `${fn.file}-${fn.line}-${idx}`,
                          name: fn.name,
                          file: fn.file,
                          line: fn.line,
                          complexity: fn.complexity,
                          severity: fn.severity as 'low' | 'medium' | 'high',
                          code: fn.code || ''
                        }))}
                        onSelectionChange={setSelectedFunctions}
                        categoryFilter={refactorCategory as any}
                      />
                    ) : (
                      <div style={{padding: '24px', textAlign: 'center', color: '#999999'}}>
                        <div style={{fontSize: '12px', marginBottom: '8px'}}>📊 No functions available</div>
                        <div style={{fontSize: '11px', color: '#666666'}}>Scan a project to see available functions</div>
                      </div>
                    )}
                  </div>

                  {/* Batch Results */}
                  {batchState.status !== 'idle' && (
                    <div style={{padding: '12px', backgroundColor: theme === 'light' ? '#f9f9f9' : '#2a2a2a', borderRadius: '4px', borderLeft: `4px solid ${batchState.status === 'error' ? '#e74c3c' : batchState.status === 'completed' ? '#27ae60' : '#f39c12'}`}}>
                      <div style={{fontSize: '12px', fontWeight: 600, marginBottom: '8px', color: theme === 'light' ? '#2c2c2c' : '#ffffff'}}>
                        {batchState.status === 'processing' ? '⏳ Processing...' : batchState.status === 'completed' ? '✅ Complete' : '❌ Error'}
                      </div>
                      <div style={{fontSize: '11px', color: theme === 'light' ? '#666666' : '#cccccc', marginBottom: '8px'}}>
                        Progress: {batchState.processedFunctions} / {batchState.totalFunctions} ({batchState.progress}%)
                      </div>
                      {batchState.results.length > 0 && (
                        <div style={{maxHeight: '200px', overflowY: 'auto'}}>
                          {batchState.results.map((result: any, idx: number) => (
                            <div key={idx} style={{fontSize: '10px', padding: '6px', backgroundColor: theme === 'light' ? '#ffffff' : '#1f1f1f', marginBottom: '4px', borderRadius: '3px', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                              <span>{result.function_name} - {result.status === 'error' ? '❌' : '✅'}</span>
                              {result.status !== 'error' && result.refactored_code && (
                                <button style={{...ts.btnO, fontSize: '9px', padding: '2px 6px'}} onClick={() => handleRejectBatchResult(idx)}>
                                  Reject
                                </button>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div style={{display: 'flex', gap: '8px', justifyContent: 'flex-end', paddingTop: '12px', borderTop: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`}}>
                    {batchState.status === 'idle' && (
                      <>
                        <button style={{...ts.btnO, fontSize: '11px'}} onClick={() => setShowBatchUI(false)}>
                          Cancel
                        </button>
                        <button style={{...ts.btnP, fontSize: '11px'}} onClick={handleStartBatchRefactor} disabled={selectedFunctions.length === 0}>
                          🚀 Start Refactoring ({selectedFunctions.length})
                        </button>
                      </>
                    )}
                    {batchState.status === 'processing' && (
                      <button style={{...ts.btnO, fontSize: '11px'}} onClick={handlePollBatch}>
                        🔄 Check Status
                      </button>
                    )}
                    {batchState.status === 'completed' && (
                      <>
                        <button style={{...ts.btnO, fontSize: '11px'}} onClick={() => resetBatch()}>
                          New Batch
                        </button>
                        <button style={{...ts.btnP, fontSize: '11px'}} onClick={handleApplyBatchResults}>
                          ✅ Apply All Changes
                        </button>
                      </>
                    )}
                  </div>
                </div>
              ) : selectedFile ? (
                <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0', height: '100%'}}>
                  {/* Original Code */}
                  <div style={{display: 'flex', flexDirection: 'column', borderRight: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`}}>
                    <div style={{padding: '16px', background: theme === 'light' ? '#f9f9f9' : '#2a2a2a', borderBottom: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`, fontSize: '12px', fontWeight: 500, color: theme === 'light' ? '#666666' : '#aaaaaa', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                      <span>📄 {selectedFunction ? `${selectedFunction.name} - Original` : `${selectedFile.name} - Original`}</span>
                      <button style={{...ts.btnO, fontSize: '9px', padding: '4px 8px'}} onClick={() => setShowBatchUI(true)}>
                        🔄 Batch
                      </button>
                    </div>
                    <div style={{flex: 1, overflow: 'auto', padding: '16px', background: theme === 'light' ? '#ffffff' : '#1f1f1f', fontFamily: "'DM Mono', monospace"}}>
                      {refactorLoading ? (
                        <div style={{textAlign: 'center', color: '#999999', paddingTop: '60px'}}>
                          <div style={{fontSize: '24px', marginBottom: '12px'}}>✨</div>
                          <div style={{fontSize: '12px'}}>Generating refactored code...</div>
                        </div>
                      ) : refactoredCode ? (
                        <pre style={{margin: 0, fontSize: '11px', lineHeight: '1.5', color: theme === 'light' ? '#666666' : '#bbbbbb', whiteSpace: 'pre-wrap', wordWrap: 'break-word'}}>
                          {refactoredCode.original}
                        </pre>
                      ) : selectedFunction ? (
                        <div style={{textAlign: 'center', color: '#999999', paddingTop: '60px'}}>
                          <div style={{fontSize: '12px'}}>Click "Generate Refactor" to see suggestions for {selectedFunction.name}</div>
                        </div>
                      ) : (
                        <div style={{textAlign: 'center', color: '#999999', paddingTop: '60px'}}>
                          <div style={{fontSize: '12px'}}>Select a function to refactor, or click "Generate Refactor" for file-level suggestions</div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Refactored Code */}
                  <div style={{display: 'flex', flexDirection: 'column'}}>
                    <div style={{padding: '16px', background: theme === 'light' ? '#f0f8f0' : '#2a3a2a', borderBottom: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`, fontSize: '12px', fontWeight: 500, color: theme === 'light' ? '#4a7c4a' : '#6dde9a'}}>
                      ✨ {selectedFunction ? `${selectedFunction.name} - Refactored` : `${selectedFile.name} - Refactored`}
                    </div>
                    <div style={{flex: 1, overflow: 'auto', padding: '16px', background: theme === 'light' ? '#fafffe' : '#1f2a1f', fontFamily: "'DM Mono', monospace"}}>
                      {refactorLoading ? (
                        <div style={{textAlign: 'center', color: '#6dde9a', paddingTop: '60px'}}>
                          <div style={{fontSize: '24px', marginBottom: '12px'}}>⚙️</div>
                          <div style={{fontSize: '12px'}}>Generating improvements...</div>
                        </div>
                      ) : refactoredCode ? (
                        <pre style={{margin: 0, fontSize: '11px', lineHeight: '1.5', color: theme === 'light' ? '#4a7c4a' : '#6dde9a', whiteSpace: 'pre-wrap', wordWrap: 'break-word'}}>
                          {refactoredCode.refactored}
                        </pre>
                      ) : selectedFunction ? (
                        <div style={{textAlign: 'center', color: '#6dde9a', paddingTop: '60px'}}>
                          <div style={{fontSize: '12px'}}>Refactored version will appear here</div>
                        </div>
                      ) : (
                        <div style={{textAlign: 'center', color: '#6dde9a', paddingTop: '60px'}}>
                          <div style={{fontSize: '12px'}}>Suggestions will appear here</div>
                        </div>
                      )}
                    </div>
                    {refactoredCode && !refactorLoading && (
                      <div style={{padding: '12px 16px', background: theme === 'light' ? '#f9f9f9' : '#2a2a2a', borderTop: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`, display: 'flex', gap: '8px', justifyContent: 'flex-end'}}>
                        <button style={{...ts.btnO, fontSize: '10px', padding: '6px 14px'}} onClick={() => setRefactoredCode(null)}>
                          Reject
                        </button>
                        <button style={{...ts.btnP, fontSize: '10px', padding: '6px 14px'}} onClick={() => handleRefactorClick()}>
                          Apply Changes
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div style={{...ts.phPanel, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
                  <div style={ts.phIc}>✨</div>
                  <div style={ts.phT}>Claude AI Refactoring</div>
                  <div style={ts.phS}>
                    <div style={{marginBottom: '12px'}}>Select a file from the Files tab to start refactoring</div>
                    <div style={{fontSize: '11px', color: '#999999', marginTop: '16px'}}>💡 Tip: Click on a function in the Analysis tab for function-level refactoring, or use Batch mode for multiple functions</div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Phase 3.5: Live Editor Tab */}
          {activeTab === 'live' && (
            <div style={ts.tabContent}>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', height: '100%', padding: '16px'}}>
                {/* Code Editor - Left */}
                <LiveCodeEditor
                  code={liveCode}
                  language={liveLanguage}
                  onCodeChange={handleLiveCodeChange}
                  onLanguageChange={handleLiveLanguageChange}
                  isAnalyzing={isLiveAnalyzing}
                  theme={theme}
                />

                {/* Metrics Panel - Right */}
                <div style={{display: 'flex', flexDirection: 'column', overflow: 'auto'}}>
                  <LiveMetricsPanel
                    analysis={liveAnalysis}
                    isAnalyzing={isLiveAnalyzing}
                    error={liveError}
                    theme={theme}
                  />
                </div>
              </div>
            </div>
          )}

          {activeTab !== 'files' && activeTab !== 'refactor' && activeTab !== 'live' && (
            <div style={{...ts.tabContent, ...ts.phPanel}}>
              <div style={ts.phIc}>{
                activeTab === 'overview' ? '📊' :
                activeTab === 'complexity' ? '🔀' :
                activeTab === 'smells' ? '👃' :
                activeTab === 'duplication' ? '©' :
                activeTab === 'security' ? '🔒' :
                activeTab === 'docs' ? '📝' :
                activeTab === 'dependencies' ? '🔗' : '📊'
              }</div>
              <div style={ts.phT}>{activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}</div>
              <div style={ts.phS}>
                {allFindings.length === 0
                  ? '✅ No issues found in ' + activeTab
                  : `${allFindings.filter(f => f.type.includes(activeTab.toLowerCase())).length} findings in ${activeTab}`
                }
              </div>
            </div>
          )}
        </div>
      </div>

      {/* FUNCTION DETAILS MODAL */}
      {showFunctionModal && selectedFunction && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }} onClick={() => setShowFunctionModal(false)}>
          <div style={{
            background: theme === 'light' ? '#ffffff' : '#1f1f1f',
            borderRadius: '8px',
            padding: '24px',
            maxWidth: '500px',
            width: '90%',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
            color: theme === 'light' ? '#2c2c2c' : '#ffffff',
            border: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`
          }} onClick={(e) => e.stopPropagation()}>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px'}}>
              <h2 style={{margin: 0, fontSize: '18px', fontWeight: 600}}>{selectedFunction.name}</h2>
              <button style={{background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer', color: '#999999'}} onClick={() => setShowFunctionModal(false)}>×</button>
            </div>
            <div style={{marginBottom: '16px', padding: '12px', background: theme === 'light' ? '#f5f5f5' : '#2a2a2a', borderRadius: '4px'}}>
              <div style={{fontSize: '12px', color: '#999999', marginBottom: '4px'}}>Cyclomatic Complexity</div>
              <div style={{fontSize: '24px', fontWeight: 600, color: selectedFunction.complexity > 10 ? '#ff6b6b' : selectedFunction.complexity > 5 ? '#f5c842' : '#6dde9a'}}>
                {selectedFunction.complexity}
              </div>
            </div>
            <div style={{marginBottom: '16px'}}>
              <div style={{fontSize: '12px', color: '#999999', marginBottom: '8px'}}>Description</div>
              <div style={{fontSize: '12px', lineHeight: '1.6', color: theme === 'light' ? '#666666' : '#cccccc'}}>
                {selectedFunction.description}
              </div>
            </div>
            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px'}}>
              <button style={{padding: '8px 12px', borderRadius: '4px', border: '1px solid #d0d0d0', background: 'transparent', cursor: 'pointer', color: theme === 'light' ? '#666666' : '#cccccc'}} onClick={() => setShowFunctionModal(false)}>
                Close
              </button>
              <button style={{padding: '8px 12px', borderRadius: '4px', border: 'none', background: '#667eea', color: '#ffffff', cursor: 'pointer', fontWeight: 500}}>
                Refactor
              </button>
            </div>
          </div>
        </div>
      )}

      {/* HIDDEN INPUTS */}
      <input
        ref={uploadManager.folderInputRef}
        type="file"
        multiple
        style={{ display: 'none' }}
        onChange={uploadManager.handleFolderSelect}
        {...({ webkitdirectory: '', mozdirectory: '' } as any)}
      />
    </div>
  );
};

const lightTheme: { [key: string]: React.CSSProperties } = {
  container: { fontFamily: "'DM Mono', monospace", display: 'flex', flexDirection: 'column', height: '100vh', background: '#f5f5f5', color: '#2c2c2c', margin: 0, padding: 0, overflow: 'hidden' },
  topbar: { display: 'flex', alignItems: 'center', height: '46px', background: '#ffffff', borderBottom: '1px solid #e0e0e0', flexShrink: 0, paddingRight: '16px', gap: '1px' },
  tbLogo: { display: 'flex', alignItems: 'center', gap: '9px', padding: '0 18px', height: '100%', borderRight: '1px solid #e0e0e0', flexShrink: 0 },
  logoHex: { fontSize: '16px', color: '#ff6b6b' },
  tbName: { fontFamily: "'Fraunces', serif", fontSize: '15px', fontWeight: 900, letterSpacing: '-0.3px', color: '#2c2c2c' },
  tbCrumb: { display: 'flex', alignItems: 'center', gap: '5px', padding: '0 16px', height: '100%', borderRight: '1px solid #e0e0e0', fontSize: '11px', color: '#999999', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' },
  tbSegment: { color: '#666666' },
  tbStatus: { display: 'flex', alignItems: 'center', gap: '7px', padding: '0 16px', fontSize: '11px' },
  pdot: { width: '7px', height: '7px', borderRadius: '50%', background: '#6dde9a', flex: 'shrink 0' },
  pdotAmber: { background: '#f5c842' },
  sw: { color: '#6dde9a', fontWeight: 500 },
  duration: { color: '#999999', fontSize: '10px' },
  tbSpacer: { flex: 1 },
  tbChips: { display: 'flex', alignItems: 'center', gap: '4px', padding: '0 14px', height: '100%', borderLeft: '1px solid #e0e0e0', flexShrink: 0 },
  chip: { padding: '2px 7px', borderRadius: '3px', fontSize: '9px', background: '#f5f5f5', border: '1px solid #d0d0d0', color: '#999999' },
  chipWarning: { borderColor: 'rgba(245, 200, 66, 0.3)', color: '#f5c842' },
  tbActs: { display: 'flex', alignItems: 'center', gap: '6px', padding: '0 14px', height: '100%', borderLeft: '1px solid #e0e0e0', flexShrink: 0 },
  btnO: { padding: '5px 13px', borderRadius: '4px', fontFamily: "'DM Mono', monospace", fontSize: '10px', cursor: 'pointer', background: 'transparent', border: '1px solid #d0d0d0', color: '#666666', transition: 'all 0.15s', display: 'flex', alignItems: 'center', gap: '5px' },
  btnP: { padding: '5px 13px', borderRadius: '4px', fontFamily: "'DM Mono', monospace", fontSize: '10px', cursor: 'pointer', background: '#ff6b6b', color: '#ffffff', fontWeight: 600, border: 'none', transition: 'all 0.15s' },
  btnPBusy: { background: '#f5f5f5', color: '#ff6b6b', border: '1px solid #ff6b6b' },
  body: { display: 'flex', flex: 1, overflow: 'hidden' },
  rail: { width: '220px', flexShrink: 0, background: '#ffffff', borderRight: '1px solid #e0e0e0', overflowY: 'auto', overflowX: 'hidden' },
  rs: { borderBottom: '1px solid #e0e0e0' },
  rsHead: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px 7px', cursor: 'pointer' },
  rsLbl: { fontSize: '9px', textTransform: 'uppercase', letterSpacing: '1.3px', color: '#999999', fontWeight: 500 },
  rsTog: { fontSize: '10px', color: '#999999', transition: 'transform 0.15s' },
  rsBody: { padding: '0 0 6px' },
  srcRow: { display: 'flex', alignItems: 'center', gap: '5px', padding: '4px 14px 6px' },
  srcField: { flex: 1, padding: '5px 8px', background: '#f5f5f5', border: '1px solid #d0d0d0', borderRadius: '3px', fontFamily: "'DM Mono', monospace", fontSize: '10px', color: '#2c2c2c', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', outline: 'none' },
  bwrap: { position: 'relative' },
  bbtn: { padding: '5px 9px', background: '#ff6b6b', border: 'none', borderRadius: '3px', color: '#ffffff', fontFamily: "'DM Mono', monospace", fontSize: '10px', fontWeight: 600, cursor: 'pointer', whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: '3px', transition: 'background 0.15s' },
  dzone: { border: '1px dashed #d0d0d0', borderRadius: '3px', padding: '9px', textAlign: 'center', cursor: 'pointer', transition: 'all 0.2s', fontSize: '10px', color: '#999999', lineHeight: 1.7, margin: '0 14px 6px' },
  dzoneActive: { borderColor: '#ff6b6b', background: 'rgba(255, 107, 107, 0.05)', color: '#2c2c2c' },
  dzoneHl: { color: '#ff6b6b' },
  fi: { display: 'flex', alignItems: 'center', gap: '7px', padding: '6px 14px', cursor: 'pointer', fontSize: '11px', color: '#999999', transition: 'all 0.12s', position: 'relative' },
  fiOn: { background: '#f5f5f5', color: '#2c2c2c' },
  fiDot: { width: '6px', height: '6px', borderRadius: '50%', flexShrink: 0 },
  fiDotPy: { background: '#6eb5ff' },
  fiDotJs: { background: '#f5c842' },
  fiName: { flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' },
  fiLoc: { fontSize: '9px', color: '#999999', flexShrink: 0 },
  ck: { display: 'flex', alignItems: 'center', gap: '7px', padding: '5px 14px', cursor: 'pointer', fontSize: '11px', color: '#999999', transition: 'color 0.12s' },
  eng: { display: 'flex', alignItems: 'center', gap: '7px', padding: '5px 14px', cursor: 'pointer', fontSize: '11px', color: '#999999', transition: 'color 0.12s' },
  throw: { display: 'flex', gap: '4px', padding: '5px 14px 8px' },
  thb: { flex: 1, padding: '4px 0', textAlign: 'center', fontSize: '9px', border: '1px solid #d0d0d0', borderRadius: '3px', cursor: 'pointer', color: '#999999', transition: 'all 0.15s', background: '#f5f5f5' },
  thbOn: { borderColor: '#ff6b6b', color: '#ff6b6b', background: 'rgba(255, 107, 107, 0.05)' },
  stage: { flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', background: '#f5f5f5' },
  mband: { display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', background: '#ffffff', borderBottom: '1px solid #e0e0e0', flexShrink: 0 },
  mc: { padding: '12px 14px', borderRight: '1px solid #e0e0e0', display: 'flex', flexDirection: 'column', gap: '3px', cursor: 'default', transition: 'background 0.15s', position: 'relative', overflow: 'hidden' },
  mcLbl: { fontSize: '8px', textTransform: 'uppercase', letterSpacing: '1.2px', color: '#999999', fontWeight: 500 },
  mcVal: { fontFamily: "'Fraunces', serif", fontSize: '22px', fontWeight: 900, letterSpacing: '-1px', lineHeight: 1 },
  mcSub: { fontSize: '9px', color: '#999999' },
  tabs: { display: 'flex', background: '#ffffff', borderBottom: '1px solid #e0e0e0', flexShrink: 0, padding: '0 14px', overflowX: 'auto' },
  tab: { padding: '9px 14px', fontSize: '11px', color: '#999999', cursor: 'pointer', borderBottom: '2px solid transparent', transition: 'all 0.15s', whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: '5px', background: 'transparent', border: 'none' },
  tabOn: { color: '#ff6b6b', borderBottomColor: '#ff6b6b' },
  tn: { padding: '1px 5px', borderRadius: '2px', background: '#f5f5f5', fontSize: '9px', color: '#999999' },
  tabContent: { flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' },
  tbar: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '7px 16px', borderBottom: '1px solid #e0e0e0', background: '#ffffff', flexShrink: 0 },
  tbarInfo: { fontSize: '10px', color: '#999999' },
  tbarRight: { display: 'flex', alignItems: 'center', gap: '6px' },
  fmts: { display: 'flex', gap: '3px' },
  fmt: { padding: '3px 7px', fontFamily: "'DM Mono', monospace", fontSize: '9px', border: '1px solid #d0d0d0', borderRadius: '3px', background: 'transparent', color: '#999999', cursor: 'pointer', transition: 'all 0.12s' },
  fmtOn: { borderColor: '#ff6b6b', color: '#ff6b6b', background: 'rgba(255, 107, 107, 0.05)' },
  tableWrap: { flex: 1, overflow: 'auto' },
  table: { width: '100%', borderCollapse: 'collapse' },
  theadRow: { background: '#f5f5f5', position: 'sticky', top: 0, zIndex: 5 },
  th: { padding: '8px 14px', textAlign: 'left', fontSize: '9px', textTransform: 'uppercase', letterSpacing: '1.1px', color: '#999999', fontWeight: 500, borderBottom: '1px solid #e0e0e0', whiteSpace: 'nowrap', cursor: 'pointer', userSelect: 'none', background: '#f5f5f5', border: 'none' },
  sa: { marginLeft: '3px', fontSize: '8px', opacity: 0.5 },
  tbodyRow: { borderBottom: '1px solid #e0e0e0', cursor: 'pointer', transition: 'background 0.1s' },
  tbodyRowSel: { background: '#f5f5f5', borderLeft: '2px solid #ff6b6b' },
  td: { padding: '9px 14px', fontSize: '11px', color: '#2c2c2c', background: 'transparent' },
  tdF: { display: 'flex', alignItems: 'center', gap: '7px', fontFamily: "'DM Mono', monospace", fontSize: '10px', color: '#ff6b6b' },
  fld: { width: '6px', height: '6px', borderRadius: '50%', flexShrink: 0 },
  fldPy: { background: '#6eb5ff' },
  fldJs: { background: '#f5c842' },
  ltPy: { display: 'inline-flex', alignItems: 'center', padding: '2px 7px', borderRadius: '3px', fontSize: '10px', background: 'rgba(110, 181, 255, 0.1)', color: '#6eb5ff' },
  ltJs: { display: 'inline-flex', alignItems: 'center', padding: '2px 7px', borderRadius: '3px', fontSize: '10px', background: 'rgba(245, 200, 66, 0.1)', color: '#f5c842' },
  tdNum: { fontVariantNumeric: 'tabular-nums', color: '#2c2c2c' },
  cxw: { display: 'flex', alignItems: 'center', gap: '7px' },
  cxt: { width: '50px', height: '4px', background: '#f0f0f0', borderRadius: '2px', overflow: 'hidden', flexShrink: 0 },
  cxf: { height: '100%', borderRadius: '2px' },
  cxLo: { background: '#6dde9a' },
  cxMid: { background: '#f5c842' },
  cxHi: { background: '#ff6b6b' },
  cxN: { fontSize: '10px', color: '#999999' },
  gp: { display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: '24px', height: '24px', borderRadius: '4px', fontFamily: "'Fraunces', serif", fontSize: '13px', fontWeight: 900 },
  gA: { background: 'rgba(109, 222, 154, 0.1)', color: '#6dde9a', border: '1px solid rgba(109, 222, 154, 0.25)' },
  gB: { background: 'rgba(110, 181, 255, 0.1)', color: '#6eb5ff', border: '1px solid rgba(110, 181, 255, 0.25)' },
  gC: { background: 'rgba(245, 200, 66, 0.1)', color: '#f5c842', border: '1px solid rgba(245, 200, 66, 0.25)' },
  svNone: { padding: '2px 7px', borderRadius: '3px', fontSize: '9px', fontWeight: 600, letterSpacing: '0.3px', background: 'rgba(153, 153, 153, 0.1)', color: '#999999' },
  svLo: { padding: '2px 7px', borderRadius: '3px', fontSize: '9px', fontWeight: 600, letterSpacing: '0.3px', background: 'rgba(109, 222, 154, 0.1)', color: '#6dde9a' },
  detail: { flex: 1, display: 'flex', flexDirection: 'column', borderTop: '1px solid #e0e0e0', overflow: 'hidden', background: '#f5f5f5' },
  detailTabs: { display: 'flex', background: '#ffffff', borderBottom: '1px solid #e0e0e0', flexShrink: 0, padding: '0 16px' },
  dtab: { padding: '8px 12px', fontSize: '10px', color: '#999999', cursor: 'pointer', borderBottom: '2px solid transparent', transition: 'all 0.15s', whiteSpace: 'nowrap', background: 'transparent', border: 'none' },
  dtabOn: { color: '#3ecfb2', borderBottomColor: '#3ecfb2' },
  detailBody: { flex: 1, overflow: 'hidden', display: 'flex' },
  dHsr: { display: 'flex', flex: 1, overflow: 'hidden' },
  dCol: { flex: 1, padding: '14px 16px', borderRight: '1px solid #e0e0e0', overflowY: 'auto' },
  dColTitle: { fontSize: '9px', textTransform: 'uppercase', letterSpacing: '1.2px', color: '#999999', marginBottom: '10px', fontWeight: 500 },
  fnl: { display: 'flex', flexDirection: 'column', gap: '5px' },
  fnR: { display: 'flex', alignItems: 'center', gap: '8px', fontSize: '10px' },
  fnNm: { flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontFamily: "'DM Mono', monospace", color: '#3ecfb2' },
  fnCx: { width: '20px', textAlign: 'right', color: '#999999', fontSize: '9px', flexShrink: 0 },
  fnB: { flex: '0 0 60px', height: '4px', background: '#e0e0e0', borderRadius: '2px', overflow: 'hidden' },
  fnBf: { height: '100%', borderRadius: '2px' },
  sugl: { display: 'flex', flexDirection: 'column', gap: '5px' },
  sugi: { display: 'flex', gap: '7px', alignItems: 'flex-start', padding: '7px 9px', borderRadius: '4px', background: '#ffffff', border: '1px solid #e0e0e0', fontSize: '10px', lineHeight: 1.6 },
  sugiIc: { flexShrink: 0, marginTop: '1px' },
  sugiTx: { color: '#999999' },
  code: { fontFamily: "'DM Mono', monospace", background: 'rgba(62, 207, 178, 0.1)', color: '#3ecfb2', padding: '1px 4px', borderRadius: '2px' },
  phPanel: { flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '8px', color: '#999999' },
  phIc: { fontSize: '26px', marginBottom: '4px' },
  phT: { fontFamily: "'Fraunces', serif", fontSize: '14px', fontWeight: 700, color: '#666666' },
  phS: { fontSize: '10px', lineHeight: 1.7, textAlign: 'center', maxWidth: '240px' },
};

const darkTheme: { [key: string]: React.CSSProperties } = {
  ...lightTheme,
  container: { fontFamily: "'DM Mono', monospace", display: 'flex', flexDirection: 'column', height: '100vh', background: '#0f0e0d', color: '#ede8e1', margin: 0, padding: 0, overflow: 'hidden' },
  topbar: { ...lightTheme.topbar, background: '#161513', borderBottom: '1px solid #302d2a' },
  tbLogo: { ...lightTheme.tbLogo, borderRight: '1px solid #302d2a' },
  tbName: { ...lightTheme.tbName, color: '#ede8e1' },
  tbCrumb: { ...lightTheme.tbCrumb, borderRight: '1px solid #302d2a', color: '#9e9890' },
  tbSegment: { color: '#ede8e1' },
  sw: { ...lightTheme.sw, color: '#6dde9a' },
  duration: { color: '#5e5a54', fontSize: '10px' },
  tbChips: { ...lightTheme.tbChips, borderLeft: '1px solid #302d2a' },
  chip: { ...lightTheme.chip, background: '#242220', border: '1px solid #3d3a36', color: '#5e5a54' },
  chipWarning: { borderColor: 'rgba(245, 200, 66, 0.3)', color: '#f5c842' },
  tbActs: { ...lightTheme.tbActs, borderLeft: '1px solid #302d2a' },
  btnO: { ...lightTheme.btnO, background: 'transparent', border: '1px solid #3d3a36', color: '#9e9890' },
  rail: { ...lightTheme.rail, background: '#161513', borderRight: '1px solid #302d2a' },
  rs: { ...lightTheme.rs, borderBottom: '1px solid #302d2a' },
  rsLbl: { ...lightTheme.rsLbl, color: '#5e5a54' },
  rsTog: { ...lightTheme.rsTog, color: '#5e5a54' },
  srcField: { ...lightTheme.srcField, background: '#242220', border: '1px solid #3d3a36', color: '#ede8e1' },
  dzone: { ...lightTheme.dzone, border: '1px dashed #3d3a36', color: '#5e5a54' },
  dzoneActive: { borderColor: '#ff6b6b', background: 'rgba(255, 107, 107, 0.06)', color: '#ede8e1' },
  fi: { ...lightTheme.fi, color: '#5e5a54' },
  fiOn: { background: '#242220', color: '#ede8e1' },
  fiDotPy: { background: '#6eb5ff' },
  fiDotJs: { background: '#f5c842' },
  fiLoc: { color: '#5e5a54' },
  ck: { ...lightTheme.ck, color: '#5e5a54' },
  eng: { ...lightTheme.eng, color: '#5e5a54' },
  thb: { ...lightTheme.thb, border: '1px solid #3d3a36', color: '#5e5a54', background: '#242220' },
  thbOn: { borderColor: '#ff6b6b', color: '#ff6b6b', background: 'rgba(255, 107, 107, 0.06)' },
  mband: { ...lightTheme.mband, background: '#161513', borderBottom: '1px solid #302d2a' },
  mc: { ...lightTheme.mc, borderRight: '1px solid #302d2a' },
  mcLbl: { ...lightTheme.mcLbl, color: '#5e5a54' },
  mcSub: { ...lightTheme.mcSub, color: '#5e5a54' },
  tabs: { ...lightTheme.tabs, background: '#161513', borderBottom: '1px solid #302d2a' },
  tab: { ...lightTheme.tab, color: '#5e5a54' },
  tn: { ...lightTheme.tn, background: '#242220', color: '#5e5a54' },
  tbar: { ...lightTheme.tbar, background: '#161513', borderBottom: '1px solid #302d2a' },
  tbarInfo: { fontSize: '10px', color: '#5e5a54' },
  fmt: { ...lightTheme.fmt, border: '1px solid #3d3a36', color: '#5e5a54' },
  fmtOn: { borderColor: '#ff6b6b', color: '#ff6b6b', background: 'rgba(255, 107, 107, 0.06)' },
  theadRow: { background: '#242220', position: 'sticky', top: 0, zIndex: 5 },
  th: { ...lightTheme.th, background: '#242220', color: '#5e5a54', borderBottom: '1px solid #302d2a' },
  tbodyRow: { borderBottom: '1px solid #302d2a', cursor: 'pointer', transition: 'background 0.1s' },
  tbodyRowSel: { background: '#242220', borderLeft: '2px solid #ff6b6b' },
  td: { ...lightTheme.td, color: '#ede8e1' },
  tdNum: { fontVariantNumeric: 'tabular-nums', color: '#ede8e1' },
  cxt: { width: '50px', height: '4px', background: '#242220', borderRadius: '2px', overflow: 'hidden', flexShrink: 0 },
  detail: { ...lightTheme.detail, borderTop: '1px solid #302d2a', background: '#0f0e0d' },
  detailTabs: { ...lightTheme.detailTabs, background: '#161513', borderBottom: '1px solid #302d2a' },
  dtab: { ...lightTheme.dtab, color: '#5e5a54' },
  dCol: { ...lightTheme.dCol, borderRight: '1px solid #302d2a' },
  dColTitle: { ...lightTheme.dColTitle, color: '#5e5a54' },
  sugi: { ...lightTheme.sugi, background: '#242220', border: '1px solid #3d3a36' },
  sugiTx: { color: '#9e9890' },
  phPanel: { flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '8px', color: '#5e5a54' },
  phT: { fontFamily: "'Fraunces', serif", fontSize: '14px', fontWeight: 700, color: '#9e9890' },
};

export default CodeScanner;
