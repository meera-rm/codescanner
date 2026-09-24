import React, { useEffect, useState } from 'react';
import { Paper, Typography, Box, Grid } from '@mui/material';
import { Activity } from 'lucide-react';

const ActivityWidget: React.FC = () => {
  const [activity, setActivity] = useState({
    analyses_today: 0,
    github_prs: 0,
    api_calls: 0,
    errors: 0,
  });

  useEffect(() => {
    fetch('/api/v1/dashboard/widgets/activity', {
      headers: { 'X-API-Key': localStorage.getItem('apiKey') || '' },
    })
      .then(r => r.json())
      .then(d => setActivity(d.data))
      .catch(console.error);
  }, []);

  return (
    <Paper sx={{ p: 3, borderRadius: '12px' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
        <Activity size={28} color="#2196F3" />
        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
          Recent Activity
        </Typography>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={6} sm={3}>
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#2196F3' }}>
              {activity.analyses_today}
            </Typography>
            <Typography variant="caption" sx={{ color: '#999' }}>
              Analyses
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#4CAF50' }}>
              {activity.github_prs}
            </Typography>
            <Typography variant="caption" sx={{ color: '#999' }}>
              GitHub PRs
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#FF9800' }}>
              {activity.api_calls}
            </Typography>
            <Typography variant="caption" sx={{ color: '#999' }}>
              API Calls
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#F44336' }}>
              {activity.errors}
            </Typography>
            <Typography variant="caption" sx={{ color: '#999' }}>
              Errors
            </Typography>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default ActivityWidget;
