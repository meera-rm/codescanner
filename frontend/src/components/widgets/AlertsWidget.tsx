import React, { useEffect, useState } from 'react';
import { Paper, Typography, List, ListItem, Box, Chip } from '@mui/material';
import { AlertCircle } from 'lucide-react';

const AlertsWidget: React.FC = () => {
  const [alerts, setAlerts] = useState<any[]>([]);

  useEffect(() => {
    fetch('/api/v1/dashboard/widgets/alerts', {
      headers: { 'X-API-Key': localStorage.getItem('apiKey') || '' },
    })
      .then(r => r.json())
      .then(d => setAlerts(d.data.alerts || []))
      .catch(console.error);
  }, []);

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'critical':
        return 'error';
      case 'warning':
        return 'warning';
      default:
        return 'info';
    }
  };

  return (
    <Paper sx={{ p: 3, borderRadius: '12px', height: '100%' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
        <AlertCircle size={28} color="#FF9800" />
        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
          Active Alerts ({alerts.length})
        </Typography>
      </Box>

      {alerts.length === 0 ? (
        <Typography variant="body2" sx={{ color: '#999' }}>
          No active alerts
        </Typography>
      ) : (
        <List sx={{ p: 0 }}>
          {alerts.map((alert, idx) => (
            <ListItem
              key={idx}
              sx={{
                p: 1.5,
                mb: 1,
                background: '#f5f5f5',
                borderRadius: '8px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                gap: 1,
              }}
            >
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', width: '100%', justifyContent: 'space-between' }}>
                <Chip
                  label={alert.level.toUpperCase()}
                  size="small"
                  color={getLevelColor(alert.level)}
                  variant="outlined"
                />
                <Typography variant="caption" sx={{ color: '#999' }}>
                  {alert.timestamp}
                </Typography>
              </Box>
              <Typography variant="body2" sx={{ fontWeight: '500' }}>
                {alert.message}
              </Typography>
            </ListItem>
          ))}
        </List>
      )}
    </Paper>
  );
};

export default AlertsWidget;
