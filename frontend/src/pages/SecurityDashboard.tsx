import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Grid, Paper, Typography, Box, Button, LinearProgress, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import { ArrowLeft, AlertTriangle, Lock } from 'lucide-react';

interface SecurityIssue {
  id: string;
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  message: string;
  file: string;
  line: number;
  count: number;
}

const SecurityDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [issues, setIssues] = useState<SecurityIssue[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSecurityData();
  }, []);

  const fetchSecurityData = async () => {
    try {
      const response = await fetch('/api/v1/dashboard/security', {
        headers: { 'X-API-Key': localStorage.getItem('apiKey') || '' },
      });
      const data = await response.json();
      setIssues(data.issues || []);
    } catch (err) {
      console.error('Failed to fetch security data:', err);
      setIssues(generateMockSecurityIssues());
    } finally {
      setLoading(false);
    }
  };

  const generateMockSecurityIssues = (): SecurityIssue[] => [
    { id: '1', type: 'SQL Injection', severity: 'critical', message: 'Unescaped SQL query detected', file: 'auth.py', line: 42, count: 2 },
    { id: '2', type: 'Hardcoded Secret', severity: 'high', message: 'API key hardcoded in source', file: 'config.js', line: 15, count: 1 },
    { id: '3', type: 'XSS Vulnerability', severity: 'high', message: 'Unsanitized user input in HTML', file: 'dashboard.tsx', line: 89, count: 3 },
    { id: '4', type: 'Command Injection', severity: 'medium', message: 'Shell command with user input', file: 'utils.py', line: 156, count: 1 },
    { id: '5', type: 'Weak Cryptography', severity: 'medium', message: 'MD5 hash detected', file: 'security.py', line: 78, count: 2 },
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#F44336';
      case 'high': return '#FF9800';
      case 'medium': return '#FFC107';
      default: return '#4CAF50';
    }
  };

  const criticalCount = issues.filter(i => i.severity === 'critical').length;
  const highCount = issues.filter(i => i.severity === 'high').length;
  const totalIssues = issues.reduce((sum, i) => sum + i.count, 0);

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 3 }}>
        <Button
          startIcon={<ArrowLeft size={20} />}
          onClick={() => navigate('/dashboard')}
          sx={{ textTransform: 'none', color: '#1976d2' }}
        >
          Back to Dashboard
        </Button>
      </Box>

      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Lock size={32} color="#F44336" />
        <div>
          <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
            Security Dashboard
          </Typography>
          <Typography variant="body2" sx={{ color: '#666' }}>
            Code security vulnerability scanning and tracking
          </Typography>
        </div>
      </Box>

      {loading && <LinearProgress sx={{ mb: 3 }} />}

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 3, textAlign: 'center', background: 'linear-gradient(135deg, #F44336 0%, #E91E63 100%)', color: 'white' }}>
            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
              {criticalCount}
            </Typography>
            <Typography variant="body2">Critical Issues</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 3, textAlign: 'center', background: 'linear-gradient(135deg, #FF9800 0%, #FFC107 100%)', color: 'white' }}>
            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
              {highCount}
            </Typography>
            <Typography variant="body2">High Issues</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 3, textAlign: 'center', background: 'linear-gradient(135deg, #2196F3 0%, #03A9F4 100%)', color: 'white' }}>
            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
              {totalIssues}
            </Typography>
            <Typography variant="body2">Total Findings</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 3, textAlign: 'center', background: 'linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%)', color: 'white' }}>
            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
              {Math.round((totalIssues > 0 ? (20 - Math.min(totalIssues, 20)) / 20 * 100 : 100))}%
            </Typography>
            <Typography variant="body2">Security Score</Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Issues Table */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
          Detected Issues
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ background: '#f5f5f5' }}>
                <TableCell>Type</TableCell>
                <TableCell>Severity</TableCell>
                <TableCell>Message</TableCell>
                <TableCell>File</TableCell>
                <TableCell align="center">Count</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {issues.map((issue) => (
                <TableRow key={issue.id} sx={{ '&:hover': { background: '#f9f9f9' } }}>
                  <TableCell sx={{ fontWeight: 'bold' }}>{issue.type}</TableCell>
                  <TableCell>
                    <Chip
                      label={issue.severity.toUpperCase()}
                      size="small"
                      sx={{
                        background: getSeverityColor(issue.severity),
                        color: 'white',
                        fontWeight: 'bold',
                      }}
                    />
                  </TableCell>
                  <TableCell>{issue.message}</TableCell>
                  <TableCell sx={{ color: '#666' }}>
                    {issue.file}:{issue.line}
                  </TableCell>
                  <TableCell align="center" sx={{ fontWeight: 'bold' }}>
                    {issue.count}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Recommendations */}
      <Paper sx={{ p: 3, mt: 3, background: '#FFF3E0' }}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <AlertTriangle size={24} color="#FF9800" />
          <div>
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
              Security Recommendations
            </Typography>
            <Typography variant="body2" sx={{ mt: 1, color: '#666' }}>
              • Prioritize fixing critical SQL injection vulnerabilities immediately
              • Remove hardcoded secrets and use environment variables
              • Implement input sanitization for all user-facing fields
              • Use parameterized queries to prevent injection attacks
              • Enable security headers in production deployment
            </Typography>
          </div>
        </Box>
      </Paper>
    </Container>
  );
};

export default SecurityDashboard;
