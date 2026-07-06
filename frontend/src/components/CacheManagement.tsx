import { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Grid,
  Button,
  Box,
  CircularProgress,
  Alert,
  Typography,
  Chip,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import DeleteIcon from '@mui/icons-material/Delete';

interface CacheInfo {
  status: string;
  server: {
    version: string;
    process_id: number;
    uptime_seconds: number;
  };
  clients: {
    connected: number;
    blocked: number;
  };
  memory: {
    used_bytes: number;
    used_human: string;
    peak_bytes: number;
    peak_human: string;
  };
  stats: {
    total_connections_received: number;
    total_commands_processed: number;
  };
}

export function CacheManagement() {
  const [cacheInfo, setCacheInfo] = useState<CacheInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [clearing, setClearing] = useState(false);

  const fetchCacheInfo = async () => {
    try {
      setLoading(true);
      setError(null);

      const [statsRes, infoRes] = await Promise.all([
        fetch('http://localhost:8000/api/v1/cache/stats'),
        fetch('http://localhost:8000/api/v1/cache/info'),
      ]);

      if (!infoRes.ok) {
        setError(`Failed to load cache information: ${infoRes.status}`);
        setLoading(false);
        return;
      }

      const [_statsData, infoData] = await Promise.all([
        statsRes.ok ? statsRes.json() : {},
        infoRes.json(),
      ]);

      setCacheInfo(infoData);
    } catch (err) {
      setError('Failed to load cache information');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCacheInfo();
    const interval = setInterval(fetchCacheInfo, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const handleClearCache = async (scope: 'all' | 'dashboard' | 'search') => {
    if (!window.confirm(`Clear ${scope} cache? This cannot be undone.`)) return;

    try {
      setClearing(true);
      const response = await fetch(`http://localhost:8000/api/v1/cache/clear?scope=${scope}`, {
        method: 'POST',
      });

      if (response.ok) {
        setSuccess(`${scope} cache cleared successfully`);
        setTimeout(() => setSuccess(null), 3000);
        fetchCacheInfo();
      } else {
        setError(`Failed to clear ${scope} cache`);
      }
    } catch (err) {
      setError('Error clearing cache');
      console.error(err);
    } finally {
      setClearing(false);
    }
  };

  const handleHealthCheck = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/cache/health', {
        method: 'POST',
      });

      const data = await response.json();
      if (data.status === 'healthy') {
        setSuccess('Cache is healthy');
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError('Cache health check failed');
      }
    } catch (err) {
      setError('Error checking cache health');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

      {!cacheInfo ? (
        <Box sx={{ textAlign: 'center', py: 4, color: 'text.secondary' }}>
          No cache information available.
        </Box>
      ) : (
        <>
          {/* Connection Status */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Box>
                      <Typography variant="h6">Redis Connection</Typography>
                      <Typography variant="body2" color="textSecondary">
                        Version {cacheInfo.server.version} • PID {cacheInfo.server.process_id}
                      </Typography>
                    </Box>
                    <Chip
                      label={cacheInfo.status === 'available' ? 'Connected' : 'Disconnected'}
                      color={cacheInfo.status === 'available' ? 'success' : 'error'}
                      variant="outlined"
                    />
                  </Box>

                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={4}>
                      <Typography color="textSecondary" gutterBottom>
                        Connected Clients
                      </Typography>
                      <Typography variant="h5">{cacheInfo.clients.connected}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <Typography color="textSecondary" gutterBottom>
                        Uptime
                      </Typography>
                      <Typography variant="h5">{Math.round(cacheInfo.server.uptime_seconds / 60)}m</Typography>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <Typography color="textSecondary" gutterBottom>
                        Memory Usage
                      </Typography>
                      <Typography variant="h5">{cacheInfo.memory.used_human}</Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Control Buttons */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={fetchCacheInfo}
                disabled={loading}
              >
                Refresh Stats
              </Button>
            </Grid>
            <Grid item>
              <Button
                variant="outlined"
                onClick={handleHealthCheck}
              >
                Health Check
              </Button>
            </Grid>
            <Grid item>
              <Button
                variant="outlined"
                color="warning"
                onClick={() => handleClearCache('dashboard')}
                disabled={clearing}
              >
                Clear Dashboard Cache
              </Button>
            </Grid>
            <Grid item>
              <Button
                variant="outlined"
                color="warning"
                onClick={() => handleClearCache('search')}
                disabled={clearing}
              >
                Clear Search Cache
              </Button>
            </Grid>
            <Grid item>
              <Button
                variant="contained"
                color="error"
                startIcon={<DeleteIcon />}
                onClick={() => handleClearCache('all')}
                disabled={clearing}
              >
                Clear All Cache
              </Button>
            </Grid>
          </Grid>

          {/* Redis Stats */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography color="textSecondary" gutterBottom>
                    Total Commands Processed
                  </Typography>
                  <Typography variant="h4">{cacheInfo.stats.total_commands_processed}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography color="textSecondary" gutterBottom>
                    Total Connections
                  </Typography>
                  <Typography variant="h4">{cacheInfo.stats.total_connections_received}</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Cache Configuration Info */}
          <Grid container spacing={2} sx={{ mt: 2 }}>
            <Grid item xs={12}>
              <Card>
                <CardHeader title="Cache Configuration" />
                <CardContent>
                  <Typography variant="body2" paragraph>
                    <strong>Dashboard Cache (5 min TTL):</strong> Cached dashboard summary, scan history, and trend metrics
                  </Typography>
                  <Typography variant="body2" paragraph>
                    <strong>Search Cache (10 min TTL):</strong> Cached search results, filter options, and suggestions
                  </Typography>
                  <Typography variant="body2" paragraph>
                    <strong>Auto-invalidation:</strong> Cache is automatically cleared when new scans are recorded or search indices are updated
                  </Typography>
                  <Typography variant="body2">
                    <strong>Hit rates:</strong> Monitor hit rates to optimize TTL values. Low hit rates may indicate TTL is too short; high hit rates suggest data is effectively cached.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </>
      )}
    </Box>
  );
}

export default CacheManagement;
