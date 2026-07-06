import { useState, useEffect } from 'react';
import { Card, CardContent, Grid, Button, Box, CircularProgress, Alert, Typography, Chip } from '@mui/material';

interface RedisInfo {
  status: string;
  server: { version: string; process_id: number; uptime_seconds: number };
  clients: { connected: number; blocked: number };
  memory: { used_bytes: number; used_human: string; peak_bytes: number; peak_human: string };
  stats: { total_connections_received: number; total_commands_processed: number };
}

const CacheManagement = () => {
  const [info, setInfo] = useState<RedisInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const res = await fetch('http://localhost:8000/api/v1/cache/info');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setInfo(data);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const timer = setInterval(fetchData, 10000);
    return () => clearInterval(timer);
  }, []);

  const clearCache = async (scope: string) => {
    if (!window.confirm(`Clear ${scope} cache?`)) return;
    try {
      const res = await fetch(`http://localhost:8000/api/v1/cache/clear?scope=${scope}`, { method: 'POST' });
      if (res.ok) {
        setSuccess(`${scope} cleared`);
        setTimeout(() => setSuccess(null), 2000);
        fetchData();
      }
    } catch (e) {
      setError(String(e));
    }
  };

  const healthCheck = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/cache/health', { method: 'POST' });
      if (res.ok) {
        setSuccess('Cache is healthy');
        setTimeout(() => setSuccess(null), 2000);
      }
    } catch (e) {
      setError(String(e));
    }
  };

  if (loading) return <CircularProgress sx={{ m: 4 }} />;
  if (!info) return <Alert severity="warning">Failed to load cache info</Alert>;

  return (
    <Box sx={{ p: 2 }}>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <div>
              <Typography variant="h6">Redis Connection</Typography>
              <Typography variant="body2" color="textSecondary">Version {info.server.version} • PID {info.server.process_id}</Typography>
            </div>
            <Chip label={info.status === 'available' ? 'Connected' : 'Disconnected'} color={info.status === 'available' ? 'success' : 'error'} />
          </Box>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={3}>
              <Typography color="textSecondary" gutterBottom>Connected Clients</Typography>
              <Typography variant="h5">{info.clients.connected}</Typography>
            </Grid>
            <Grid item xs={12} sm={3}>
              <Typography color="textSecondary" gutterBottom>Uptime</Typography>
              <Typography variant="h5">{Math.round(info.server.uptime_seconds / 60)}m</Typography>
            </Grid>
            <Grid item xs={12} sm={3}>
              <Typography color="textSecondary" gutterBottom>Memory</Typography>
              <Typography variant="h5">{info.memory.used_human}</Typography>
            </Grid>
            <Grid item xs={12} sm={3}>
              <Typography color="textSecondary" gutterBottom>Commands</Typography>
              <Typography variant="h5">{info.stats.total_commands_processed}</Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Box sx={{ mb: 3, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
        <Button variant="outlined" onClick={fetchData}>🔄 Refresh</Button>
        <Button variant="outlined" onClick={healthCheck}>✓ Health Check</Button>
        <Button variant="outlined" color="warning" onClick={() => clearCache('dashboard')}>Clear Dashboard</Button>
        <Button variant="outlined" color="warning" onClick={() => clearCache('search')}>Clear Search</Button>
        <Button variant="contained" color="error" onClick={() => clearCache('all')}>Clear All</Button>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography color="textSecondary">Total Connections</Typography>
              <Typography variant="h4">{info.stats.total_connections_received}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography color="textSecondary">Memory Usage</Typography>
              <Typography variant="h4">{info.memory.used_human}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CacheManagement;
