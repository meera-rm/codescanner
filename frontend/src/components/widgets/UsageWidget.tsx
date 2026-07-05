import React, { useEffect, useState } from 'react';
import { Paper, Typography, Box, Grid, LinearProgress } from '@mui/material';
import { Zap } from 'lucide-react';

const UsageWidget: React.FC = () => {
  const [usage, setUsage] = useState({
    api_calls: 0,
    analyses: 0,
    storage_mb: 0,
    limits: {
      monthly_analyses: 1000,
    },
  });

  useEffect(() => {
    fetch('/api/v1/dashboard/widgets/usage', {
      headers: { 'X-API-Key': localStorage.getItem('apiKey') || '' },
    })
      .then(r => r.json())
      .then(d => setUsage(d.data))
      .catch(console.error);
  }, []);

  const getUsagePercent = (used: number, limit: number) => {
    return limit > 0 ? (used / limit) * 100 : 0;
  };

  return (
    <Paper sx={{ p: 3, borderRadius: '12px' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <Zap size={28} color="#FF9800" />
        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
          Plan Usage
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6}>
          <Typography variant="body2" sx={{ mb: 1, color: '#666' }}>
            Monthly Analyses
          </Typography>
          <LinearProgress
            variant="determinate"
            value={getUsagePercent(usage.analyses, usage.limits.monthly_analyses)}
            sx={{ height: 8, borderRadius: '4px' }}
          />
          <Typography variant="caption" sx={{ mt: 1, display: 'block', color: '#999' }}>
            {usage.analyses} / {usage.limits.monthly_analyses}
          </Typography>
        </Grid>

        <Grid item xs={12} sm={6}>
          <Typography variant="body2" sx={{ mb: 1, color: '#666' }}>
            Storage Used
          </Typography>
          <Box>
            <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
              {usage.storage_mb.toFixed(1)} MB
            </Typography>
          </Box>
        </Grid>

        <Grid item xs={12} sm={6}>
          <Typography variant="body2" sx={{ mb: 1, color: '#666' }}>
            API Calls
          </Typography>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            {usage.api_calls}
          </Typography>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default UsageWidget;
