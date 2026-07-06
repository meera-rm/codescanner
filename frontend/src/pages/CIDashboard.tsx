import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Box,
  Typography,
  CircularProgress,
  Button,
  TextField,
  MenuItem,
  Alert,
  Pagination,
  Badge,
} from '@mui/material';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import SearchFilters from '../components/SearchFilters';
import useWebSocket from '../hooks/useWebSocket';

interface ScanHistory {
  id: string;
  repository: string;
  branch: string;
  platform: string;
  event_type: string;
  status: string;
  critical_count: number;
  error_count: number;
  warning_count: number;
  total_findings: number;
  files_scanned: number;
  duration_ms?: number;
  created_at: string;
  completed_at?: string;
}

interface TrendMetrics {
  repository: string;
  last_scan_at?: string;
  total_scans: number;
  successful_scans: number;
  failed_scans: number;
  pass_rate: number;
  avg_critical_per_scan: number;
  avg_error_per_scan: number;
  avg_warning_per_scan: number;
  avg_scan_duration_ms: number;
  critical_trend: Array<{ date: string; count: number }>;
  error_trend: Array<{ date: string; count: number }>;
  warning_trend: Array<{ date: string; count: number }>;
  pass_rate_trend: Array<{ date: string; pass_rate: number }>;
  platforms: Record<string, number>;
}

interface DashboardSummary {
  total_scans: number;
  successful_scans: number;
  failed_scans: number;
  pass_rate: number;
  total_critical: number;
  total_error: number;
  total_warning: number;
  repositories: Array<{
    name: string;
    scans: number;
    critical: number;
    error: number;
    warning: number;
    last_scan: string;
    last_status: string;
  }>;
  platforms: Record<string, number>;
}

const CIDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [history, setHistory] = useState<ScanHistory[]>([]);
  const navigate = useNavigate();
  const [selectedRepo, setSelectedRepo] = useState<string>('');
  const [trends, setTrends] = useState<TrendMetrics | null>(null);
  const [days, setDays] = useState<number>(30);
  const [error, setError] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<ScanHistory[]>([]);
  const [totalSearchResults, setTotalSearchResults] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [isSearchMode, setIsSearchMode] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [recentUpdateCount, setRecentUpdateCount] = useState(0);

  useEffect(() => {
    fetchDashboardData();
  }, [days]);

  // WebSocket for real-time updates (fixed with exponential backoff)
  const { isConnected } = useWebSocket({
    url: `http://localhost:8000/api/v1/ws/dashboard`,
    onMessage: (message) => {
      if (message.type === 'scan_complete') {
        console.log('Scan completed, refreshing dashboard');
        fetchDashboardData();
        setRecentUpdateCount(prev => prev + 1);
        setTimeout(() => setRecentUpdateCount(0), 3000);
      } else if (message.type === 'dashboard_refresh') {
        console.log('Dashboard refresh message received');
        setSummary(message.data);
      }
    },
    onConnect: () => {
      console.log('WebSocket connected');
      setWsConnected(true);
    },
    onDisconnect: () => {
      console.log('WebSocket disconnected');
      setWsConnected(false);
    },
    onError: (error) => {
      console.warn('WebSocket error:', error);
    },
  });

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch summary
      const summaryRes = await fetch(`http://localhost:8000/api/v1/ci-dashboard/summary?days=${days}`);
      if (summaryRes.ok) {
        const summaryData = await summaryRes.json();
        setSummary(summaryData);
      }

      // Fetch history
      const historyRes = await fetch(`http://localhost:8000/api/v1/ci-dashboard/history?days=${days}`);
      if (historyRes.ok) {
        const historyData = await historyRes.json();
        setHistory(historyData);
      }
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (filters: Record<string, any>) => {
    try {
      setLoading(true);
      setError(null);
      setCurrentPage(1);

      // Build query string
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value));
        }
      });
      params.append('limit', '50');
      params.append('offset', '0');

      const response = await fetch(`http://localhost:8000/api/v1/search/scans?${params}`);
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results);
        setTotalSearchResults(data.total);
        setIsSearchMode(true);
      } else {
        setError('Failed to perform search');
      }
    } catch (err) {
      setError('Search failed');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleClearSearch = () => {
    setIsSearchMode(false);
    setSearchResults([]);
    setTotalSearchResults(0);
    setCurrentPage(1);
  };

  const fetchTrends = async (repository: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/ci-dashboard/trends/${encodeURIComponent(repository)}`);
      if (res.ok) {
        const data = await res.json();
        setTrends(data);
      }
    } catch (err) {
      console.error('Failed to fetch trends:', err);
    }
  };

  const handleSelectRepository = (repo: string) => {
    setSelectedRepo(repo);
    fetchTrends(repo);
  };

  const exportAsCSV = async () => {
    try {
      const queryParams = new URLSearchParams({ days: days.toString() });
      const response = await fetch(`http://localhost:8000/api/v1/ci-dashboard/export/csv?${queryParams}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `codepulse-scans-${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err) {
      setError('Failed to export CSV');
    }
  };

  const exportAsPDF = async () => {
    try {
      const queryParams = new URLSearchParams({ days: days.toString() });
      const response = await fetch(`http://localhost:8000/api/v1/ci-dashboard/export/pdf?${queryParams}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `codepulse-report-${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err) {
      setError('Failed to export PDF');
    }
  };

  const getStatusColor = (status: string): 'success' | 'error' | 'warning' | 'default' => {
    switch (status) {
      case 'success':
        return 'success';
      case 'failure':
        return 'error';
      case 'warning':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getPlatformIcon = (platform: string): string => {
    switch (platform) {
      case 'github':
        return '🐙';
      case 'gitlab':
        return '🦊';
      case 'jenkins':
        return '🔧';
      case 'circleci':
        return '🔵';
      default:
        return '🔄';
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          CI/CD Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          {recentUpdateCount > 0 && (
            <Badge badgeContent={recentUpdateCount} color="success">
              <Chip label="Updates" color="success" size="small" />
            </Badge>
          )}
          <Chip
            label={wsConnected ? 'Live' : 'Offline'}
            color={wsConnected ? 'success' : 'error'}
            size="small"
            variant={wsConnected ? 'filled' : 'outlined'}
          />
          <Button variant="outlined" size="small" onClick={() => navigate('/')}>
            ← Home
          </Button>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {wsConnected && (
        <Alert severity="info" sx={{ mb: 2 }}>
          🔄 Real-time updates enabled. Dashboard will auto-refresh when scans complete.
        </Alert>
      )}

      {/* Search Filters */}
      <SearchFilters onSearch={handleSearch} onClear={handleClearSearch} />

      {/* Time Filter & Export */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
            <TextField
              select
              label="Time Period"
              value={days}
              onChange={(e) => setDays(parseInt(e.target.value))}
              size="small"
              sx={{ minWidth: 200 }}
            >
              <MenuItem value={7}>Last 7 days</MenuItem>
              <MenuItem value={14}>Last 14 days</MenuItem>
              <MenuItem value={30}>Last 30 days</MenuItem>
              <MenuItem value={90}>Last 90 days</MenuItem>
            </TextField>

            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="outlined"
                size="small"
                onClick={exportAsCSV}
              >
                📊 Export CSV
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={exportAsPDF}
              >
                📄 Export PDF
              </Button>
              <Button
                variant="contained"
                size="small"
                onClick={() => navigate('/monitoring')}
              >
                🔧 Monitoring & Management
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      {summary && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography color="textSecondary" gutterBottom>
                  Total Scans
                </Typography>
                <Typography variant="h4">{summary.total_scans}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography color="textSecondary" gutterBottom>
                  Pass Rate
                </Typography>
                <Typography variant="h4" sx={{ color: summary.pass_rate > 80 ? 'green' : 'red' }}>
                  {summary.pass_rate.toFixed(1)}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography color="textSecondary" gutterBottom>
                  Critical Issues
                </Typography>
                <Typography variant="h4" sx={{ color: summary.total_critical > 0 ? '#d32f2f' : 'green' }}>
                  {summary.total_critical}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography color="textSecondary" gutterBottom>
                  Repositories
                </Typography>
                <Typography variant="h4">{summary.repositories.length}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Scan History Table */}
      <Card sx={{ mb: 3 }}>
        <CardHeader
          title={isSearchMode ? `Search Results (${totalSearchResults} found)` : 'Recent Scans'}
        />
        <TableContainer>
          <Table>
            <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
              <TableRow>
                <TableCell>Repository</TableCell>
                <TableCell>Platform</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Critical</TableCell>
                <TableCell align="right">Errors</TableCell>
                <TableCell align="right">Warnings</TableCell>
                <TableCell>Time</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(isSearchMode ? searchResults : history.slice(0, 10)).map((scan) => (
                <TableRow key={scan.id} sx={{ '&:hover': { backgroundColor: '#f9f9f9' } }}>
                  <TableCell>{scan.repository}</TableCell>
                  <TableCell>{getPlatformIcon(scan.platform)} {scan.platform}</TableCell>
                  <TableCell>
                    <Chip
                      label={scan.status}
                      color={getStatusColor(scan.status)}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <span style={{ color: scan.critical_count > 0 ? '#d32f2f' : 'inherit' }}>
                      {scan.critical_count}
                    </span>
                  </TableCell>
                  <TableCell align="right">
                    <span style={{ color: scan.error_count > 0 ? '#f57c00' : 'inherit' }}>
                      {scan.error_count}
                    </span>
                  </TableCell>
                  <TableCell align="right">
                    <span style={{ color: scan.warning_count > 0 ? '#fbc02d' : 'inherit' }}>
                      {scan.warning_count}
                    </span>
                  </TableCell>
                  <TableCell>{new Date(scan.created_at).toLocaleDateString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        {isSearchMode && totalSearchResults > 50 && (
          <Box sx={{ p: 2, display: 'flex', justifyContent: 'center' }}>
            <Pagination
              count={Math.ceil(totalSearchResults / 50)}
              page={currentPage}
              onChange={(_, page) => setCurrentPage(page)}
            />
          </Box>
        )}
      </Card>

      {/* Repository Selection for Trends */}
      {summary && summary.repositories.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardHeader title="Repository Trends" />
          <CardContent>
            <TextField
              select
              label="Select Repository"
              value={selectedRepo}
              onChange={(e) => handleSelectRepository(e.target.value)}
              fullWidth
              size="small"
              sx={{ mb: 2 }}
            >
              {summary.repositories.map((repo) => (
                <MenuItem key={repo.name} value={repo.name}>
                  {repo.name} ({repo.scans} scans)
                </MenuItem>
              ))}
            </TextField>

            {trends && (
              <Box sx={{ mt: 3 }}>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                      Critical Issues Trend
                    </Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={trends.critical_trend}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Line type="monotone" dataKey="count" stroke="#d32f2f" name="Critical" />
                      </LineChart>
                    </ResponsiveContainer>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                      Pass Rate Trend
                    </Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={trends.pass_rate_trend}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis domain={[0, 100]} />
                        <Tooltip formatter={(value) => `${value.toFixed(1)}%`} />
                        <Line type="monotone" dataKey="pass_rate" stroke="#4caf50" name="Pass Rate %" />
                      </LineChart>
                    </ResponsiveContainer>
                  </Grid>

                  <Grid item xs={12}>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                      Issues Breakdown
                    </Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={[
                        {
                          name: 'Issues',
                          critical: trends.avg_critical_per_scan,
                          error: trends.avg_error_per_scan,
                          warning: trends.avg_warning_per_scan,
                        },
                      ]}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="critical" fill="#d32f2f" name="Avg Critical" />
                        <Bar dataKey="error" fill="#f57c00" name="Avg Error" />
                        <Bar dataKey="warning" fill="#fbc02d" name="Avg Warning" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Grid>
                </Grid>
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {/* Platform Breakdown */}
      {summary && (
        <Card>
          <CardHeader title="Platform Usage" />
          <CardContent>
            <Grid container spacing={2}>
              {Object.entries(summary.platforms).map(([platform, count]) => (
                <Grid item xs={12} sm={6} md={3} key={platform}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Typography variant="h5">{getPlatformIcon(platform)}</Typography>
                      <Typography color="textSecondary" gutterBottom>
                        {platform.charAt(0).toUpperCase() + platform.slice(1)}
                      </Typography>
                      <Typography variant="h6">{count} scans</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}
    </Container>
  );
};

export default CIDashboard;
