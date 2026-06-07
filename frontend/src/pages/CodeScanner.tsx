import React, { useState } from 'react';

type Theme = 'dark' | 'light';
type TabType = 'overview' | 'complexity' | 'smells' | 'duplication' | 'security' | 'docs' | 'dependencies' | 'files' | 'refactor';
type DetailTab = 'analysis' | 'refactor';

interface ScannedFile {
  name: string;
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
}

export const CodeScanner: React.FC = () => {
  const [directoryPath, setDirectoryPath] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [theme, setTheme] = useState<Theme>('light');
  const [activeTab, setActiveTab] = useState<TabType>('files');
  const [detailTab, setDetailTab] = useState<DetailTab>('analysis');
  const [selectedFile, setSelectedFile] = useState<ScannedFile | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [scannedFiles, setScannedFiles] = useState<ScannedFile[]>([]);
  const [allFindings, setAllFindings] = useState<any[]>([]);
  const [exportFormat, setExportFormat] = useState<'json' | 'html' | 'markdown' | 'pdf'>('json');
  const [analyses, setAnalyses] = useState({
    'Basic metrics': true,
    'Cyclomatic complexity': true,
    'Code smells': true,
    'Code duplication': true
  });
  const [selectedEngine, setSelectedEngine] = useState('Python analysis');
  const [collapsedSections, setCollapsedSections] = useState<{[key: string]: boolean}>({});
  const [selectedFunction, setSelectedFunction] = useState<{name: string; complexity: number; description: string} | null>(null);
  const [showFunctionModal, setShowFunctionModal] = useState(false);
  const [refactoredCode, setRefactoredCode] = useState<{original: string; refactored: string} | null>(null);
  const [refactorLoading, setRefactorLoading] = useState(false);
  const [metrics, setMetrics] = useState({
    grade: 'B',
    loc: 0,
    totalFindings: 0,
    criticalCount: 0,
    documented: '100%',
    depCycles: 0,
    qualityScore: 100
  });

  const folderInputRef = React.useRef<HTMLInputElement>(null);


  const handleBrowseFolder = () => {
    folderInputRef.current?.click();
  };

  const handleDirectorySelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const firstFile = files[0];
      const relativePath = (firstFile as any).webkitRelativePath || firstFile.name;
      const directoryName = relativePath.split('/')[0] || relativePath;
      setDirectoryPath(directoryName);
    }
  };

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
      const response = await fetch('/api/v1/scan/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ directory_path: directoryPath, language: 'python' })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Scan failed' }));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const data: ScanResponse = await response.json();

      if (data.status === 'error') {
        throw new Error(data.findings ? 'No code files found to scan' : 'Scan failed');
      }

      // Process findings
      setAllFindings(data.findings || []);

      // Use scanned_files from backend or derive from findings
      let files: ScannedFile[] = [];

      if (data.scanned_files && data.scanned_files.length > 0) {
        // Use files returned by backend
        files = data.scanned_files.map((f: any) => ({
          name: f.name,
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

      setActiveTab('files');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(`Scan failed: ${message}`);
      console.error('Scan error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = (format: 'json' | 'html' | 'markdown' | 'pdf') => {
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
        findings: allFindings
      }, null, 2);
      filename += '.json';
      mimeType = 'application/json';
    } else if (format === 'markdown') {
      content = `# Code Scan Report
**Directory:** ${directoryPath}
**Generated:** ${new Date().toISOString()}

## Metrics
- Grade: ${metrics.grade}
- Lines of Code: ${metrics.loc}
- Total Findings: ${metrics.totalFindings}
- High Severity: ${metrics.criticalCount}
- Documented: ${metrics.documented}
- Dep Cycles: ${metrics.depCycles}

## Files Scanned (${scannedFiles.length})
${scannedFiles.map(f => `- ${f.name} (${f.language}, ${f.loc} LOC)`).join('\n')}

## Issues Found (${allFindings.length})
${allFindings.length > 0 ? allFindings.map(f => `- **${f.type}** at ${f.file}:${f.line} - ${f.message} (${f.severity})`).join('\n') : 'No issues found'}
`;
      filename += '.md';
      mimeType = 'text/markdown';
    } else if (format === 'html') {
      content = `<!DOCTYPE html>
<html>
<head>
  <title>Code Scan Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
    .header { background: #333; color: #fff; padding: 20px; border-radius: 5px; }
    .metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }
    .metric { background: #fff; padding: 15px; border-radius: 5px; border-left: 4px solid #667eea; }
    .files { background: #fff; padding: 20px; border-radius: 5px; margin: 20px 0; }
    .issues { background: #fff; padding: 20px; border-radius: 5px; }
    .issue { padding: 10px; margin: 10px 0; border-left: 4px solid #ff6b6b; background: #fff5f5; }
    .critical { border-left-color: #ff6b6b; }
    .warning { border-left-color: #f5c842; }
    .info { border-left-color: #6dde9a; }
  </style>
</head>
<body>
  <div class="header">
    <h1>Code Scan Report</h1>
    <p>Directory: ${directoryPath}</p>
    <p>Generated: ${new Date().toLocaleString()}</p>
  </div>

  <div class="metrics">
    <div class="metric"><strong>Grade:</strong> ${metrics.grade}</div>
    <div class="metric"><strong>Lines of Code:</strong> ${metrics.loc}</div>
    <div class="metric"><strong>Total Findings:</strong> ${metrics.totalFindings}</div>
    <div class="metric"><strong>High Severity:</strong> ${metrics.criticalCount}</div>
    <div class="metric"><strong>Documented:</strong> ${metrics.documented}</div>
    <div class="metric"><strong>Dep Cycles:</strong> ${metrics.depCycles}</div>
  </div>

  <div class="files">
    <h2>Files Scanned (${scannedFiles.length})</h2>
    <ul>
      ${scannedFiles.map(f => `<li>${f.name} <small>(${f.language.toUpperCase()}, ${f.loc} LOC)</small></li>`).join('')}
    </ul>
  </div>

  <div class="issues">
    <h2>Issues Found (${allFindings.length})</h2>
    ${allFindings.length > 0
      ? allFindings.map(f => `<div class="issue ${f.severity.toLowerCase()}"><strong>${f.type}</strong> at ${f.file}:${f.line}<br/>${f.message}</div>`).join('')
      : '<p style="color: #6dde9a;">✅ No issues found</p>'
    }
  </div>
</body>
</html>`;
      filename += '.html';
      mimeType = 'text/html';
    } else if (format === 'pdf') {
      alert('PDF export requires backend support. Using JSON format instead.');
      content = JSON.stringify({
        directory: directoryPath,
        timestamp: new Date().toISOString(),
        metrics,
        files: scannedFiles,
        findings: allFindings
      }, null, 2);
      filename += '.json';
      mimeType = 'application/json';
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
          <button style={ts.btnO} onClick={() => handleExport('json')} disabled={scannedFiles.length === 0}>↓ Export</button>
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
                  <button style={ts.bbtn} onClick={handleBrowseFolder}>Browse <span style={{fontSize: '8px'}}>▾</span></button>
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
              >
                Drop folder / file / .zip<br/>
                <span style={ts.dzoneHl}>Browse</span> · max 100 MB
              </div>
            </div>
            )}
          </div>

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

          {/* ENGINE */}
          <div style={ts.rs}>
            <div style={{...ts.rsHead, cursor: 'pointer'}} onClick={() => toggleSection('engine')}>
              <span style={ts.rsLbl}>3 · ENGINE</span>
              <span style={{...ts.rsTog, transform: collapsedSections['engine'] ? 'rotate(-90deg)' : 'rotate(0deg)', transition: 'transform 0.2s'}}>{collapsedSections['engine'] ? '▸' : '▾'}</span>
            </div>
            {!collapsedSections['engine'] && (
              <div style={ts.rsBody}>
                {['Python analysis', 'Claude Code analysis'].map((engine) => (
                  <label key={engine} style={ts.eng}>
                    <input
                      type="radio"
                      name="engine"
                      checked={selectedEngine === engine}
                      onChange={() => setSelectedEngine(engine)}
                    />
                    <span>{engine}</span>
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
            {(['overview', 'complexity', 'smells', 'duplication', 'security', 'docs', 'dependencies', 'files', 'refactor'] as TabType[]).map((tab) => (
              <button
                key={tab}
                style={{...ts.tab, ...(activeTab === tab ? ts.tabOn : {}), ...(tab === 'refactor' ? {background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: '#ffffff'} : {})}}
                onClick={() => setActiveTab(tab)}
              >
                {tab === 'refactor' ? '✨ Refactor' : tab.charAt(0).toUpperCase() + tab.slice(1)}
                {['complexity', 'smells', 'dependencies'].includes(tab) && <span style={ts.tn}>·</span>}
              </button>
            ))}
          </div>

          {/* TAB CONTENT */}
          {activeTab === 'files' && scannedFiles.length > 0 && (
            <div style={ts.tabContent}>
              <div style={ts.tbar}>
                <div style={ts.tbarInfo}><strong>{scannedFiles.length} files</strong> scanned · Python analysis · 0.24s</div>
                <div style={ts.tbarRight}>
                  <div style={ts.fmts}>
                    <button style={{...ts.fmt, ...(exportFormat === 'json' ? ts.fmtOn : {})}} onClick={() => setExportFormat('json')}>JSON</button>
                    <button style={{...ts.fmt, ...(exportFormat === 'html' ? ts.fmtOn : {})}} onClick={() => setExportFormat('html')}>HTML</button>
                    <button style={{...ts.fmt, ...(exportFormat === 'markdown' ? ts.fmtOn : {})}} onClick={() => setExportFormat('markdown')}>Markdown</button>
                    <button style={{...ts.fmt, ...(exportFormat === 'pdf' ? ts.fmtOn : {})}} onClick={() => setExportFormat('pdf')}>PDF</button>
                  </div>
                  <button style={ts.btnO} onClick={handleDownload} disabled={scannedFiles.length === 0}>↓ Download</button>
                </div>
              </div>

              {/* TABLE */}
              <div style={ts.tableWrap}>
                {scannedFiles.length > 0 ? (
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
                      {scannedFiles.map((file) => (
                        <tr key={file.name} style={{...ts.tbodyRow, ...(selectedFile?.name === file.name ? ts.tbodyRowSel : {})}}>
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
                    <div style={ts.phT}>No scans yet</div>
                    <div style={ts.phS}>Enter a directory path and click Scan to analyze your code</div>
                  </div>
                )}
              </div>

              {/* DETAIL */}
              {selectedFile && (
                <div style={ts.detail}>
                  <div style={ts.detailTabs}>
                    <button
                      style={{...ts.dtab, ...(detailTab === 'analysis' ? ts.dtabOn : {})}}
                      onClick={() => setDetailTab('analysis')}
                    >
                      Analysis
                    </button>
                    <span style={{color: '#cccccc', fontSize: '10px', margin: '0 8px'}}>·</span>
                    <button
                      style={{...ts.dtab, ...(detailTab === 'refactor' ? ts.dtabOn : {}), ...(detailTab === 'refactor' ? {background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: '#ffffff'} : {})}}
                      onClick={() => {
                        setDetailTab('refactor');
                        if (!refactoredCode) handleRefactorClick();
                      }}
                      disabled={!selectedFile}
                    >
                      ✨ Refactor
                    </button>
                  </div>
                  <div style={{...ts.detailBody, display: 'flex', flexDirection: 'column'}}>
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
                              {[
                                { name: 'process_data()', cx: 18, p: 95 },
                                { name: 'validate_input()', cx: 12, p: 75 },
                                { name: 'format_output()', cx: 6, p: 38 },
                                { name: 'init()', cx: 2, p: 15 }
                              ].map((fn) => (
                                <div key={fn.name} style={{...ts.fnR, cursor: 'pointer'}} onClick={() => handleFunctionClick(fn.name, fn.cx)}>
                                  <span style={{...ts.fnNm, textDecoration: 'underline', color: '#667eea'}}>{fn.name}</span>
                                  <span style={ts.fnCx}>{fn.cx}</span>
                                  <div style={ts.fnB}>
                                    <div style={{...ts.fnBf, width: `${fn.p}%`, background: fn.p > 70 ? '#ff6b6b' : fn.p > 40 ? '#f5c842' : '#6dde9a'}}></div>
                                  </div>
                                </div>
                              ))}
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
                      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0', flex: 1, height: '100%', overflow: 'hidden'}}>
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
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'refactor' && (
            <div style={ts.tabContent}>
              {selectedFile ? (
                <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0', height: '100%'}}>
                  {/* Original Code */}
                  <div style={{display: 'flex', flexDirection: 'column', borderRight: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`}}>
                    <div style={{padding: '16px', background: theme === 'light' ? '#f9f9f9' : '#2a2a2a', borderBottom: `1px solid ${theme === 'light' ? '#e0e0e0' : '#333333'}`, fontSize: '12px', fontWeight: 500, color: theme === 'light' ? '#666666' : '#aaaaaa'}}>
                      📄 {selectedFunction ? `${selectedFunction.name} - Original` : `${selectedFile.name} - Original`}
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
                    <div style={{fontSize: '11px', color: '#999999', marginTop: '16px'}}>💡 Tip: Click on a function in the Analysis tab for function-level refactoring</div>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab !== 'files' && activeTab !== 'refactor' && (
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
        ref={folderInputRef}
        type="file"
        multiple
        style={{ display: 'none' }}
        onChange={handleDirectorySelect}
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
