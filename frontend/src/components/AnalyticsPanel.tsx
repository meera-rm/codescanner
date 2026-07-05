import React, { useEffect, useState } from 'react';
import { Paper, Grid, Typography, Box } from '@mui/material';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp } from 'lucide-react';

const AnalyticsPanel: React.FC = () => {
  const [analytics, setAnalytics] = useState({
    monitoring: {
      total_requests: 0,
      total_errors: 0,
      error_rate: 0,
      avg_response_time_ms: 0,
    },
    performance: {
      min_ms: 0,
      max_ms: 0,
      avg_ms: 0,
      p95_ms: 0,
      p99_ms: 0,
    },
    learning: {
      total_experiences: 0,
      avg_improvement: 0,
    },
  });

  useEffect(() => {
    fetch('/api/v1/dashboard/analytics', {
      headers: { 'X-API-Key': localStorage.getItem('apiKey') || '' },
    })
      .then(r => r.json())
      .then(d => setAnalytics(d))
      .catch(console.error);
  }, []);

  const performanceData = [
    { name: 'Min', value: analytics.performance.min_ms },
    { name: 'Avg', value: analytics.performance.avg_ms },
    { name: 'P95', value: analytics.performance.p95_ms },
    { name: 'P99', value: analytics.performance.p99_ms },
    { name: 'Max', value: analytics.performance.max_ms },
  ];

  return (
    <Grid container spacing={3}>
      {/* Key Metrics */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3, borderRadius: '12px' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <TrendingUp size={28} color="#2196F3" />
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
              Request Metrics
            </Typography>
          </Box>

          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Box>
                <Typography variant="body2" sx={{ color: '#999' }}>
                  Total Requests
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mt: 0.5 }}>
                  {analytics.monitoring.total_requests}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box>
                <Typography variant="body2" sx={{ color: '#999' }}>
                  Total Errors
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mt: 0.5, color: '#F44336' }}>
                  {analytics.monitoring.total_errors}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box>
                <Typography variant="body2" sx={{ color: '#999' }}>
                  Error Rate
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mt: 0.5 }}>
                  {analytics.monitoring.error_rate.toFixed(2)}%
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box>
                <Typography variant="body2" sx={{ color: '#999' }}>
                  Avg Response Time
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mt: 0.5 }}>
                  {analytics.monitoring.avg_response_time_ms.toFixed(0)}ms
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Paper>
      </Grid>

      {/* Learning Metrics */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3, borderRadius: '12px' }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
            AI Learning Progress
          </Typography>

          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Box>
                <Typography variant="body2" sx={{ color: '#999' }}>
                  Total Experiences
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mt: 0.5 }}>
                  {analytics.learning.total_experiences}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box>
                <Typography variant="body2" sx={{ color: '#999' }}>
                  Avg Improvement
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mt: 0.5, color: '#4CAF50' }}>
                  {(analytics.learning.avg_improvement * 100).toFixed(1)}%
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Paper>
      </Grid>

      {/* Performance Chart */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3, borderRadius: '12px' }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
            Response Time Distribution
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#2196F3" />
            </BarChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default AnalyticsPanel;
