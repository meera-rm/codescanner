import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Button, TextField, Paper, Grid, Card, CardContent, Typography, List, ListItem, ListItemText, Chip, FormGroup, FormControlLabel, Checkbox, RadioGroup, FormControl, FormLabel, Radio } from '@mui/material';

interface Issue {
  file: string;
  line: number;
  type: string;
  message: string;
  severity: 'WARNING' | 'ERROR' | 'INFO';
}

const CodeScannerExplorer: React.FC = () => {
  const navigate = useNavigate();
  const [issues, setIssues] = useState<Issue[]>([]);
  const [severity, setSeverity] = useState<'all' | 'warning' | 'error'>('all');
  const [selectedCategories, setSelectedCategories] = useState<string[]>(['unused_import', 'high_complexity']);
  const [apiUrl, setApiUrl] = useState('http://localhost:8000');
  const [isLive, setIsLive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [lastAttemptTime, setLastAttemptTime] = useState<number | null>(null);

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

  const getErrorMessage = (error: any, statusCode?: number): string => {
    if (error instanceof TypeError) {
      if (error.message.includes('Failed to fetch')) {
        return `Network Error: Unable to reach ${apiUrl}. Check if the API is running and the URL is correct.`;
      }
      return `Network Error: ${error.message}`;
    }

    if (statusCode === 400) return 'Bad Request: Invalid scan parameters. Check the API documentation.';
    if (statusCode === 401) return 'Unauthorized: API key required or invalid.';
    if (statusCode === 403) return 'Forbidden: Access denied to this endpoint.';
    if (statusCode === 404) return 'Not Found: API endpoint not found. Ensure the API is running correctly.';
    if (statusCode === 500) return 'Server Error: The API encountered an internal error. Check API logs.';
    if (statusCode === 503) return 'Service Unavailable: The API is temporarily down. Try again in a moment.';

    if (error.message.includes('timeout')) {
      return `Timeout: API request took too long (>10s). The server may be overloaded.`;
    }

    return `API Error: ${error.message || 'Unknown error occurred'}`;
  };

  const getRecoverySuggestions = (error: string): string[] => {
    const suggestions: string[] = [];

    if (error.includes('Network Error') || error.includes('reach')) {
      suggestions.push('✓ Ensure the CodeScanner API is running: python -m uvicorn api.main:app --host 0.0.0.0 --port 8000');
      suggestions.push('✓ Check the API URL is correct (default: http://localhost:8000)');
      suggestions.push('✓ Check your internet connection and firewall settings');
    }

    if (error.includes('Not Found')) {
      suggestions.push('✓ Verify the API is running and responding to health checks');
      suggestions.push('✓ Check that the /api/v1/scan/sync endpoint exists');
    }

    if (error.includes('Timeout')) {
      suggestions.push('✓ The API is processing a large scan. Wait and try again.');
      suggestions.push('✓ Check server resources (CPU, memory, disk space)');
    }

    if (suggestions.length === 0) {
      suggestions.push('✓ Try refreshing the page');
      suggestions.push('✓ Check the browser console for detailed error information');
      suggestions.push('✓ Verify the API endpoint is accessible');
    }

    return suggestions;
  };

  const validateApiUrl = (url: string): boolean => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  };

  const fetchLiveData = async (retryAttempt = 0) => {
    // Validate URL format
    if (!validateApiUrl(apiUrl)) {
      setError(`Invalid API URL: "${apiUrl}". Please enter a valid URL like http://localhost:8000`);
      setIsLive(false);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    setLastAttemptTime(Date.now());

    try {
      // Create abort controller for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

      const response = await fetch(`${apiUrl}/api/v1/scan/sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          directory_path: 'api',
          language: 'python',
          options: { security: true, quality_score: true }
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      // Check response status
      if (!response.ok) {
        const errorMsg = getErrorMessage(new Error(`HTTP ${response.status}`), response.status);
        setError(errorMsg);
        setIsLive(false);
        return;
      }

      // Parse response
      const data = await response.json();

      // Validate response structure
      if (!data || typeof data !== 'object') {
        setError('Invalid API Response: Expected JSON object from API');
        setIsLive(false);
        return;
      }

      if (!Array.isArray(data.findings)) {
        setError('Invalid API Response: Missing or invalid "findings" array');
        setIsLive(false);
        return;
      }

      // Transform and set issues
      const transformedIssues = data.findings
        .map((f: any) => ({
          file: f.file?.split('/').pop() || 'unknown',
          line: f.line || 0,
          type: f.type || 'unknown',
          message: f.message || 'No message',
          severity: f.severity || 'INFO'
        }))
        .filter((issue: Issue) => issue.file && issue.line >= 0);

      if (transformedIssues.length === 0) {
        setError('No issues found in scan results');
        setIsLive(false);
        return;
      }

      setIssues(transformedIssues);
      setIsLive(true);
      setRetryCount(0);
      setError(null);
    } catch (err: any) {
      const errorMessage = getErrorMessage(err);
      setError(errorMessage);
      setIsLive(false);

      // Auto-retry logic for network errors (up to 2 retries)
      if (retryAttempt < 2 && (err instanceof TypeError || err.name === 'AbortError')) {
        const backoffMs = Math.pow(2, retryAttempt) * 1000; // Exponential backoff: 1s, 2s
        console.log(`Auto-retrying in ${backoffMs}ms... (attempt ${retryAttempt + 1}/2)`);

        setTimeout(() => {
          setRetryCount(retryAttempt + 1);
          fetchLiveData(retryAttempt + 1);
        }, backoffMs);
      } else {
        setRetryCount(0);
      }
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
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        {/* <Button
          variant="outlined"
          size="small"
          onClick={() => navigate('/dashboard')}
          sx={{ height: 'fit-content' }}
        >
          ← Back to Dashboard
        </Button> */}
        <Box>
          <Typography variant="h4" sx={{ mb: 1 }}>
            🔍 CodeScanner Explorer
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Interactive analysis tool for exploring and filtering code scan results
          </Typography>
        </Box>
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
                <Box sx={{ mt: 2, p: 2, bgcolor: '#fee2e2', borderRadius: 1, border: '1px solid #fecaca' }}>
                  <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                    <span style={{ fontSize: 14, color: '#dc2626', flexShrink: 0 }}>❌</span>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="caption" sx={{ color: '#7f1d1d', fontWeight: 600, display: 'block', mb: 0.5 }}>
                        Connection Error
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#991b1b', display: 'block', mb: 1 }}>
                        {error}
                      </Typography>
                      {retryCount > 0 && (
                        <Typography variant="caption" sx={{ color: '#92400e', display: 'block', mb: 1 }}>
                          ⏳ Auto-retrying... (attempt {retryCount}/2)
                        </Typography>
                      )}
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="caption" sx={{ color: '#7c2d12', fontWeight: 600, display: 'block', mb: 0.5 }}>
                          Recovery suggestions:
                        </Typography>
                        {getRecoverySuggestions(error).map((suggestion, idx) => (
                          <Typography
                            key={idx}
                            variant="caption"
                            sx={{ color: '#92400e', display: 'block', fontSize: '11px', lineHeight: 1.4 }}
                          >
                            {suggestion}
                          </Typography>
                        ))}
                      </Box>
                    </Box>
                  </Box>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => fetchLiveData()}
                    sx={{ mt: 1, bgcolor: '#fff5f5', borderColor: '#fca5a5', color: '#991b1b', fontSize: '11px' }}
                  >
                    🔄 Retry Now
                  </Button>
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
