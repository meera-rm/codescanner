import React, { useState, useEffect } from 'react';
import { Box, Button, TextField, Paper, Grid, Card, CardContent, Typography, List, ListItem, ListItemText, Chip, FormGroup, FormControlLabel, Checkbox, RadioGroup, FormControl, FormLabel, Radio } from '@mui/material';

interface Issue {
  file: string;
  line: number;
  type: string;
  message: string;
  severity: 'WARNING' | 'ERROR' | 'INFO';
}

const CodeScannerExplorer: React.FC = () => {
  const [issues, setIssues] = useState<Issue[]>([]);
  const [severity, setSeverity] = useState<'all' | 'warning' | 'error'>('all');
  const [selectedCategories, setSelectedCategories] = useState<string[]>(['unused_import', 'high_complexity']);
  const [apiUrl, setApiUrl] = useState('http://localhost:8000');
  const [isLive, setIsLive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const defaultIssues: Issue[] = [
    { file: 'main.py', line: 38, type: 'unused_import', message: "Import 'job_queue' is unused", severity: 'WARNING' },
    { file: 'auth_middleware.py', line: 4, type: 'unused_import', message: "Import 'RateLimiter' is unused", severity: 'WARNING' },
    { file: 'scanning.py', line: 19, type: 'high_complexity', message: "Function 'scan_codebase_task' has complexity 16 (threshold: 10)", severity: 'WARNING' },
    { file: 'remote_handler.py', line: 25, type: 'high_complexity', message: "Function 'download_github_repo' has complexity 17 (threshold: 10)", severity: 'WARNING' },
    { file: 'scanner_service.py', line: 102, type: 'high_complexity', message: "Function 'scan' has complexity 20 (threshold: 10)", severity: 'WARNING' },
  ];

  // Initialize with default issues
  useEffect(() => {
    setIssues(defaultIssues);
  }, []);

  const fetchLiveData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiUrl}/api/v1/scan/sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          directory_path: 'api',
          language: 'python',
          options: { security: true, quality_score: true }
        })
      });

      if (!response.ok) throw new Error(`API error: ${response.status}`);

      const data = await response.json();
      if (data.findings) {
        const transformedIssues = data.findings.map((f: any) => ({
          file: f.file.split('/').pop(),
          line: f.line,
          type: f.type,
          message: f.message,
          severity: f.severity
        }));
        setIssues(transformedIssues);
        setIsLive(true);
      }
    } catch (err) {
      setError(`Failed to fetch from ${apiUrl}: ${err}`);
      setIsLive(false);
    } finally {
      setLoading(false);
    }
  };

  const filteredIssues = issues.filter(issue => {
    if (severity !== 'all' && issue.severity.toLowerCase() !== severity) return false;
    if (!selectedCategories.includes(issue.type)) return false;
    return true;
  });

  const stats = {
    total: filteredIssues.length,
    warnings: filteredIssues.filter(i => i.severity === 'WARNING').length,
    errors: filteredIssues.filter(i => i.severity === 'ERROR').length
  };

  const handleCategoryChange = (category: string) => {
    setSelectedCategories(prev =>
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  return (
    <Box sx={{ p: 3, maxWidth: '1400px', mx: 'auto' }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ mb: 1 }}>
          🔍 CodeScanner Explorer
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Interactive analysis tool for exploring and filtering code scan results
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Controls Panel */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            {/* Data Source */}
            <Box sx={{ mb: 3, pb: 2, borderBottom: '1px solid #e0e0e0' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <span style={{ fontSize: 16, color: isLive ? '#10b981' : '#64748b' }}>
                  {isLive ? '✓' : '●'}
                </span>
                <Typography variant="caption" sx={{ fontWeight: 600 }}>
                  {isLive ? 'Live API Data' : 'Standalone (Demo Data)'}
                </Typography>
              </Box>
              <TextField
                fullWidth
                size="small"
                placeholder="http://localhost:8000"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                sx={{ mb: 1 }}
              />
              <Button
                fullWidth
                variant="contained"
                onClick={fetchLiveData}
                disabled={loading}
              >
                {loading ? '⏳ Fetching...' : isLive ? '🔄 Refresh Data' : '🔄 Fetch Live Data'}
              </Button>
              {error && (
                <Box sx={{ mt: 1, p: 1, bgcolor: '#fee2e2', borderRadius: 1, display: 'flex', gap: 1 }}>
                  <span style={{ fontSize: 14, color: '#dc2626' }}>❌</span>
                  <Typography variant="caption" sx={{ color: '#7f1d1d' }}>
                    {error}
                  </Typography>
                </Box>
              )}
            </Box>

            {/* Severity Filter */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                Severity
              </Typography>
              <FormControl component="fieldset" fullWidth>
                <RadioGroup
                  value={severity}
                  onChange={(e) => setSeverity(e.target.value as any)}
                >
                  <FormControlLabel value="all" control={<Radio />} label="All Issues" />
                  <FormControlLabel value="warning" control={<Radio />} label="Warnings Only" />
                  <FormControlLabel value="error" control={<Radio />} label="Errors Only" />
                </RadioGroup>
              </FormControl>
            </Box>

            {/* Category Filter */}
            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                Categories
              </Typography>
              <FormGroup>
                <FormControlLabel
                  control={<Checkbox checked={selectedCategories.includes('unused_import')} onChange={() => handleCategoryChange('unused_import')} />}
                  label="Unused Imports"
                />
                <FormControlLabel
                  control={<Checkbox checked={selectedCategories.includes('high_complexity')} onChange={() => handleCategoryChange('high_complexity')} />}
                  label="High Complexity"
                />
                <FormControlLabel
                  control={<Checkbox checked={selectedCategories.includes('security')} onChange={() => handleCategoryChange('security')} />}
                  label="Security Issues"
                />
                <FormControlLabel
                  control={<Checkbox checked={selectedCategories.includes('documentation')} onChange={() => handleCategoryChange('documentation')} />}
                  label="Documentation"
                />
              </FormGroup>
            </Box>
          </Paper>
        </Grid>

        {/* Preview Panel */}
        <Grid item xs={12} md={8}>
          {/* Statistics */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={4}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" variant="caption" sx={{ fontWeight: 600 }}>
                    TOTAL
                  </Typography>
                  <Typography variant="h5">{stats.total}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={4}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" variant="caption" sx={{ fontWeight: 600 }}>
                    WARNINGS
                  </Typography>
                  <Typography variant="h5" sx={{ color: '#f59e0b' }}>
                    {stats.warnings}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={4}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" variant="caption" sx={{ fontWeight: 600 }}>
                    ERRORS
                  </Typography>
                  <Typography variant="h5" sx={{ color: '#ef4444' }}>
                    {stats.errors}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Issues List */}
          <Paper sx={{ maxHeight: 600, overflow: 'auto' }}>
            {filteredIssues.length === 0 ? (
              <Box sx={{ p: 4, textAlign: 'center', color: '#6b7280' }}>
                <Typography variant="body2">No issues found. Adjust filters to see results.</Typography>
              </Box>
            ) : (
              <List>
                {filteredIssues.map((issue, idx) => (
                  <ListItem key={idx} divider sx={{ flexDirection: 'column', alignItems: 'flex-start', py: 1.5 }}>
                    <Box sx={{ display: 'flex', gap: 1, mb: 0.5, width: '100%', alignItems: 'center' }}>
                      <Typography
                        variant="caption"
                        sx={{ fontFamily: 'monospace', fontWeight: 600, color: '#3b82f6', flex: 1 }}
                      >
                        {issue.file}:{issue.line}
                      </Typography>
                      <Chip
                        label={issue.type.replace(/_/g, ' ')}
                        size="small"
                        variant="outlined"
                        sx={{ height: 20 }}
                      />
                    </Box>
                    <Typography variant="body2" sx={{ color: '#6b7280' }}>
                      {issue.message}
                    </Typography>
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CodeScannerExplorer;
