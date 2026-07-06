import { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Grid,
  Button,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  LinearProgress,
  Typography,
  Chip,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import DeleteIcon from '@mui/icons-material/Delete';

interface CacheStats {
  name: string;
  keys_count: number;
  memory_usage_bytes: number;
  ttl_minutes: number;
  hit_rate_percent?: number;
  eviction_policy?: string;
}

interface CacheInfo {
  redis_connected: boolean;
  redis_host: string;
  redis_port: number;
  redis_db: number;
  connected_clients: number;
  used_memory_mb: number;
  total_memory_mb: number;
  cache_stats: CacheStats[];
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

  const memoryUsagePercent = cacheInfo
    ? (cacheInfo.used_memory_mb / cacheInfo.total_memory_mb) * 100
    : 0;

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
                        {cacheInfo.redis_host}:{cacheInfo.redis_port} (DB {cacheInfo.redis_db})
                      </Typography>
                    </Box>
                    <Chip
                      label={cacheInfo.redis_connected ? 'Connected' : 'Disconnected'}
                      color={cacheInfo.redis_connected ? 'success' : 'error'}
                      variant="outlined"
                    />
                  </Box>

                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={4}>
                      <Typography color="textSecondary" gutterBottom>
                        Connected Clients
                      </Typography>
                      <Typography variant="h5">{cacheInfo.connected_clients}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={8}>
                      <Typography color="textSecondary" gutterBottom>
                        Memory Usage ({cacheInfo.used_memory_mb}MB / {cacheInfo.total_memory_mb}MB)
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={Math.min(memoryUsagePercent, 100)}
                        sx={{ height: 10, borderRadius: 5 }}
                      />
                      <Typography variant="caption" sx={{ mt: 1 }}>
                        {memoryUsagePercent.toFixed(1)}% used
                      </Typography>
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

          {/* Cache Statistics */}
          {cacheInfo.cache_stats.length > 0 && (
            <Grid item xs={12}>
              <Card>
                <CardHeader title="Cache Statistics by Scope" />
                <TableContainer>
                  <Table>
                    <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
                      <TableRow>
                        <TableCell>Cache Scope</TableCell>
                        <TableCell align="right">Keys Count</TableCell>
                        <TableCell align="right">Memory Usage</TableCell>
                        <TableCell align="right">TTL (Minutes)</TableCell>
                        <TableCell align="right">Hit Rate</TableCell>
                        <TableCell align="right">Eviction Policy</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {cacheInfo.cache_stats.map((stat) => (
                        <TableRow key={stat.name}>
                          <TableCell>{stat.name}</TableCell>
                          <TableCell align="right">{stat.keys_count}</TableCell>
                          <TableCell align="right">
                            {(stat.memory_usage_bytes / 1024).toFixed(2)} KB
                          </TableCell>
                          <TableCell align="right">{stat.ttl_minutes}</TableCell>
                          <TableCell align="right">
                            {stat.hit_rate_percent ? `${stat.hit_rate_percent.toFixed(1)}%` : 'N/A'}
                          </TableCell>
                          <TableCell align="right">
                            {stat.eviction_policy || 'Default'}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Card>
            </Grid>
          )}

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
