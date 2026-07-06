import { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Grid,
  Typography,
  CircularProgress,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface PerformanceSummary {
  total_requests: number;
  avg_response_time_ms: number;
  p50_response_time_ms: number;
  p95_response_time_ms: number;
  p99_response_time_ms: number;
  min_response_time_ms: number;
  max_response_time_ms: number;
  error_count: number;
  error_rate_percent: number;
  time_period_minutes: number;
}

interface EndpointStats {
  [key: string]: {
    request_count: number;
    avg_response_time_ms: number;
    min_response_time_ms: number;
    max_response_time_ms: number;
    error_count: number;
    error_rate_percent: number;
  };
}

export function PerformanceMonitoring() {
  const [summary, setSummary] = useState<PerformanceSummary | null>(null);
  const [endpoints, setEndpoints] = useState<EndpointStats | null>(null);
  const [distribution, setDistribution] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [minutes, setMinutes] = useState(60);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all metrics in parallel
      const [summaryRes, endpointsRes, distRes] = await Promise.all([
        fetch(`http://localhost:8000/api/v1/performance/summary?minutes=${minutes}`),
        fetch(`http://localhost:8000/api/v1/performance/endpoints?minutes=${minutes}`),
        fetch(`http://localhost:8000/api/v1/performance/distribution?minutes=${minutes}`),
      ]);

      const [summaryData, endpointsData, distData] = await Promise.all([
        summaryRes.json(),
        endpointsRes.json(),
        distRes.json(),
      ]);

      setSummary(summaryData);
      setEndpoints(endpointsData);
      setDistribution(distData);
    } catch (err) {
      setError('Failed to load performance metrics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, [minutes]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  // Prepare distribution data for pie chart
  const distributionData = distribution
    ? Object.entries(distribution).map(([key, value]) => ({
        name: key,
        value: value,
      }))
    : [];

  const COLORS = ['#4caf50', '#8bc34a', '#ffc107', '#ff9800', '#f57c00', '#d32f2f'];

  return (
    <Box sx={{ p: 2 }}>
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            {[60, 1440].map(m => (
              <Chip
                key={m}
                label={m === 60 ? 'Last Hour' : 'Last 24 Hours'}
                onClick={() => setMinutes(m)}
                color={minutes === m ? 'primary' : 'default'}
                variant={minutes === m ? 'filled' : 'outlined'}
              />
            ))}
          </Box>
        </Grid>
      </Grid>

      {error && (
        <Box sx={{ color: 'error.main', mb: 2 }}>
          {error}
        </Box>
      )}

      {summary && (
        <>
          {/* Summary Cards */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography color="textSecondary" gutterBottom>
                    Total Requests
                  </Typography>
                  <Typography variant="h4">{summary.total_requests}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography color="textSecondary" gutterBottom>
                    Avg Response Time
                  </Typography>
                  <Typography variant="h4">{summary.avg_response_time_ms.toFixed(1)}ms</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography color="textSecondary" gutterBottom>
                    P95 Response Time
                  </Typography>
                  <Typography variant="h4" sx={{ color: summary.p95_response_time_ms > 500 ? '#d32f2f' : '#4caf50' }}>
                    {summary.p95_response_time_ms.toFixed(1)}ms
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography color="textSecondary" gutterBottom>
                    Error Rate
                  </Typography>
                  <Typography variant="h4" sx={{ color: summary.error_rate_percent > 2 ? '#d32f2f' : '#4caf50' }}>
                    {summary.error_rate_percent.toFixed(2)}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Charts */}
          <Grid container spacing={2}>
            {/* Distribution Chart */}
            {distributionData.length > 0 && (
              <Grid item xs={12} md={6}>
                <Card>
                  <CardHeader title="Response Time Distribution" />
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={distributionData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={(entry) => `${entry.name}: ${entry.value}`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {distributionData.map((_, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* Percentiles Chart */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader title="Response Time Percentiles" />
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart
                      data={[
                        { name: 'P50', value: summary.p50_response_time_ms },
                        { name: 'P95', value: summary.p95_response_time_ms },
                        { name: 'P99', value: summary.p99_response_time_ms },
                      ]}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="value" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>

            {/* Slowest Endpoints */}
            {endpoints && (
              <Grid item xs={12}>
                <Card>
                  <CardHeader title="Endpoint Performance" />
                  <TableContainer>
                    <Table>
                      <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
                        <TableRow>
                          <TableCell>Endpoint</TableCell>
                          <TableCell align="right">Requests</TableCell>
                          <TableCell align="right">Avg (ms)</TableCell>
                          <TableCell align="right">Min (ms)</TableCell>
                          <TableCell align="right">Max (ms)</TableCell>
                          <TableCell align="right">Errors</TableCell>
                          <TableCell align="right">Error Rate</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {Object.entries(endpoints)
                          .sort((a, b) => b[1].avg_response_time_ms - a[1].avg_response_time_ms)
                          .slice(0, 10)
                          .map(([endpoint, stats]) => (
                            <TableRow key={endpoint}>
                              <TableCell sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                {endpoint}
                              </TableCell>
                              <TableCell align="right">{stats.request_count}</TableCell>
                              <TableCell align="right" sx={{ color: stats.avg_response_time_ms > 500 ? '#d32f2f' : 'inherit' }}>
                                {stats.avg_response_time_ms.toFixed(1)}
                              </TableCell>
                              <TableCell align="right">{stats.min_response_time_ms.toFixed(1)}</TableCell>
                              <TableCell align="right">{stats.max_response_time_ms.toFixed(1)}</TableCell>
                              <TableCell align="right">{stats.error_count}</TableCell>
                              <TableCell align="right">{stats.error_rate_percent.toFixed(2)}%</TableCell>
                            </TableRow>
                          ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Card>
              </Grid>
            )}
          </Grid>
        </>
      )}
    </Box>
  );
}

export default PerformanceMonitoring;
