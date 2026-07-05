import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Grid, Container, CircularProgress, Alert, Button, Box } from '@mui/material';
import { ArrowLeft } from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import DashboardSummary from '../components/DashboardSummary';
import AIInsightsWidget from '../components/widgets/AIInsightsWidget';
import SystemHealthWidget from '../components/widgets/SystemHealthWidget';
import AlertsWidget from '../components/widgets/AlertsWidget';
import ActivityWidget from '../components/widgets/ActivityWidget';
import UsageWidget from '../components/widgets/UsageWidget';
import AnalyticsPanel from '../components/AnalyticsPanel';

interface DashboardData {
  summary: any;
  widgets: any[];
  analytics: any;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'analytics' | 'health'>('overview');

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/v1/dashboard/summary', {
        headers: {
          'X-API-Key': localStorage.getItem('apiKey') || '',
        },
      });

      if (!response.ok) throw new Error('Failed to fetch dashboard data');

      const dashboardData = await response.json();
      setData(dashboardData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Back Button */}
      <Box sx={{ mb: 3 }}>
        <Button
          startIcon={<ArrowLeft size={20} />}
          onClick={() => navigate('/')}
          sx={{
            textTransform: 'none',
            color: '#1976d2',
            fontSize: '1rem',
            '&:hover': { background: '#f0f0f0' },
          }}
        >
          Back to Home
        </Button>
      </Box>

      {/* Header Summary */}
      {data?.summary && <DashboardSummary summary={data.summary} />}

      {/* Tabs */}
      <div style={{ marginTop: '2rem', borderBottom: '1px solid #e0e0e0' }}>
        <div style={{ display: 'flex', gap: '2rem' }}>
          {['overview', 'analytics', 'health'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              style={{
                padding: '1rem',
                border: 'none',
                background: 'none',
                cursor: 'pointer',
                fontWeight: activeTab === tab ? 'bold' : 'normal',
                borderBottom: activeTab === tab ? '2px solid #1976d2' : 'none',
                color: activeTab === tab ? '#1976d2' : '#666',
                textTransform: 'capitalize',
              }}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12} md={6}>
            <AIInsightsWidget />
          </Grid>
          <Grid item xs={12} md={6}>
            <SystemHealthWidget />
          </Grid>
          <Grid item xs={12} md={8}>
            <ActivityWidget />
          </Grid>
          <Grid item xs={12} md={4}>
            <AlertsWidget />
          </Grid>
          <Grid item xs={12}>
            <UsageWidget />
          </Grid>
        </Grid>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && (
        <div style={{ marginTop: '2rem' }}>
          <AnalyticsPanel />
        </div>
      )}

      {/* Health Tab */}
      {activeTab === 'health' && (
        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12}>
            <div style={{
              background: 'white',
              borderRadius: '8px',
              padding: '2rem',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            }}>
              <h2>Codebase Health</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data?.analytics?.health_timeline || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="health_score" stroke="#8884d8" />
                  <Line type="monotone" dataKey="complexity" stroke="#82ca9d" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Grid>
        </Grid>
      )}
    </Container>
  );
};

export default Dashboard;
