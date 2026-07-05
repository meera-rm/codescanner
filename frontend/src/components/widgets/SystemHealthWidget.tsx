import React, { useEffect, useState } from 'react';
import { Paper, Typography, Box } from '@mui/material';
import { Heart } from 'lucide-react';

const SystemHealthWidget: React.FC = () => {
  const [health, setHealth] = useState({
    availability: 99.9,
    error_rate: 0.1,
    response_time: 150,
    status: 'healthy',
  });

  useEffect(() => {
    fetch('/api/v1/dashboard/widgets/system-health', {
      headers: { 'X-API-Key': localStorage.getItem('apiKey') || '' },
    })
      .then(r => r.json())
      .then(d => setHealth(d.data))
      .catch(console.error);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return '#4CAF50';
      case 'degraded':
        return '#FF9800';
      default:
        return '#F44336';
    }
  };

  return (
    <Paper sx={{ p: 3, borderRadius: '12px' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
        <Heart size={28} color={getStatusColor(health.status)} />
        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
          System Health
        </Typography>
      </Box>

      <Box sx={{ mb: 2 }}>
        <Box
          sx={{
            width: '100%',
            height: '8px',
            background: '#e0e0e0',
            borderRadius: '4px',
            overflow: 'hidden',
          }}
        >
          <Box
            sx={{
              width: `${health.availability}%`,
              height: '100%',
              background: getStatusColor(health.status),
              transition: 'width 0.3s',
            }}
          />
        </Box>
        <Typography variant="body2" sx={{ mt: 1, color: '#666' }}>
          Availability: {health.availability.toFixed(1)}%
        </Typography>
      </Box>

      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" sx={{ color: '#666' }}>
          Error Rate
        </Typography>
        <Typography variant="h6" sx={{ fontWeight: 'bold', mt: 0.5 }}>
          {health.error_rate.toFixed(2)}%
        </Typography>
      </Box>

      <Box>
        <Typography variant="body2" sx={{ color: '#666' }}>
          Avg Response Time
        </Typography>
        <Typography variant="h6" sx={{ fontWeight: 'bold', mt: 0.5 }}>
          {health.response_time}ms
        </Typography>
      </Box>

      <Box sx={{ mt: 2, p: 1.5, background: '#f5f5f5', borderRadius: '8px' }}>
        <Typography
          variant="body2"
          sx={{
            fontWeight: 'bold',
            color: getStatusColor(health.status),
            textTransform: 'uppercase',
          }}
        >
          Status: {health.status}
        </Typography>
      </Box>
    </Paper>
  );
};

export default SystemHealthWidget;
