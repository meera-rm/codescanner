import React, { useState, useEffect } from 'react';
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
} from '@mui/material';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

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
  const [selectedRepo, setSelectedRepo] = useState<string>('');
  const [trends, setTrends] = useState<TrendMetrics | null>(null);
  const [days, setDays] = useState<number>(30);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, [days]);

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
      <Typography variant="h4" sx={{ mb: 3 }}>
        CI/CD Dashboard
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Time Filter */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
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
        <CardHeader title="Recent Scans" />
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
              {history.slice(0, 10).map((scan) => (
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
                  <TableCell>{format(new Date(scan.created_at), 'MMM dd, HH:mm')}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
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
