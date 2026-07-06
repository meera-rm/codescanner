import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Button,
  Box,
  Typography,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Switch,
  FormControlLabel,
} from '@mui/material';
import { Github, CheckCircle } from 'lucide-react';

interface Installation {
  id: string;
  installation_id: number;
  is_active: boolean;
  repositories: number;
  created_at: string;
}

interface Repository {
  id: string;
  name: string;
  repo_id: number;
  enabled: boolean;
  fail_on_critical: boolean;
  fail_on_error: boolean;
}

const GitHubConnect: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [installations, setInstallations] = useState<Installation[]>([]);
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [selectedRepo, setSelectedRepo] = useState<Repository | null>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);

  const apiKey = localStorage.getItem('apiKey') || '';
  const userId = localStorage.getItem('userId') || '';

  useEffect(() => {
    loadInstallations();
  }, []);

  const loadInstallations = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/github/installations/${userId}`, {
        headers: { 'X-API-Key': apiKey },
      });

      if (response.ok) {
        const data = await response.json();
        setInstallations(data.installations || []);
      }
    } catch (err) {
      setError('Failed to load installations');
    } finally {
      setLoading(false);
    }
  };

  const handleInstallApp = () => {
    // Redirect to GitHub App installation page
    window.location.href = 'https://github.com/apps/codepulse-ai/installations/new';
  };

  const handleSettingsOpen = (repo: Repository) => {
    setSelectedRepo(repo);
    setSettingsOpen(true);
  };

  const handleSettingsSave = async () => {
    if (!selectedRepo) return;

    try {
      setLoading(true);
      const response = await fetch(
        `/api/v1/github/repositories/${selectedRepo.id}`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': apiKey,
          },
          body: JSON.stringify({
            enabled: selectedRepo.enabled,
            fail_on_critical: selectedRepo.fail_on_critical,
            fail_on_error: selectedRepo.fail_on_error,
          }),
        }
      );

      if (response.ok) {
        setSuccess('Repository settings updated');
        setSettingsOpen(false);

        // Reload repositories
        loadRepositories(installations[0]?.installation_id);
      }
    } catch (err) {
      setError('Failed to save settings');
    } finally {
      setLoading(false);
    }
  };

  const loadRepositories = async (_installationId: number) => {
    try {
      setLoading(true);
      // In a real app, fetch repos from API
      // For now, show placeholder
      setRepositories([]);
    } catch (err) {
      setError('Failed to load repositories');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Github size={32} color="#0366d6" />
          <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
            GitHub Integration
          </Typography>
        </Box>
        <Typography variant="body1" sx={{ color: '#666' }}>
          Connect your GitHub repositories to enable automated PR scanning
        </Typography>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: 3 }}>
          {success}
        </Alert>
      )}

      {/* Setup Steps */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
          Setup Steps
        </Typography>

        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
          {/* Step 1: Install App */}
          <Paper
            sx={{
              p: 3,
              background: installations.length > 0 ? '#f0f9ff' : '#fff',
              border: '1px solid #e0e0e0',
              borderRadius: '8px',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <Box
                sx={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: installations.length > 0 ? '#4caf50' : '#2196f3',
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 'bold',
                }}
              >
                1
              </Box>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                Install GitHub App
              </Typography>
            </Box>

            <Typography variant="body2" sx={{ color: '#666', mb: 2 }}>
              Install the CodePulse AI GitHub App to your repositories
            </Typography>

            <Button
              variant="contained"
              onClick={handleInstallApp}
              startIcon={<Github size={20} />}
              fullWidth
              disabled={installations.length === 0}
            >
              Install App on GitHub
            </Button>

            {installations.length > 0 && (
              <Box sx={{ mt: 2, p: 2, background: '#e8f5e9', borderRadius: '4px' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: '#2e7d32' }}>
                  <CheckCircle size={20} />
                  <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                    App installed on {installations.length} account(s)
                  </Typography>
                </Box>
              </Box>
            )}
          </Paper>

          {/* Step 2: Configure Repositories */}
          <Paper
            sx={{
              p: 3,
              background: repositories.length > 0 ? '#f0f9ff' : '#fff',
              border: '1px solid #e0e0e0',
              borderRadius: '8px',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <Box
                sx={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: repositories.length > 0 ? '#4caf50' : '#2196f3',
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 'bold',
                }}
              >
                2
              </Box>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                Configure Repositories
              </Typography>
            </Box>

            <Typography variant="body2" sx={{ color: '#666', mb: 2 }}>
              Select which repositories to scan and configure quality gates
            </Typography>

            <Button
              variant="contained"
              onClick={() => loadRepositories(installations[0]?.installation_id || 0)}
              fullWidth
              disabled={installations.length === 0}
            >
              {loading ? <CircularProgress size={24} /> : 'Load Repositories'}
            </Button>
          </Paper>
        </Box>
      </Paper>

      {/* Repositories List */}
      {repositories.length > 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
            Connected Repositories ({repositories.length})
          </Typography>

          <List>
            {repositories.map((repo) => (
              <ListItem
                key={repo.id}
                sx={{
                  mb: 2,
                  p: 2,
                  background: '#f5f5f5',
                  borderRadius: '8px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Github size={18} />
                      {repo.name}
                    </Box>
                  }
                  secondary={
                    <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                      <Chip
                        label={repo.enabled ? 'Enabled' : 'Disabled'}
                        size="small"
                        color={repo.enabled ? 'success' : 'default'}
                      />
                      {repo.fail_on_critical && (
                        <Chip label="Block on Critical" size="small" variant="outlined" />
                      )}
                    </Box>
                  }
                />

                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => handleSettingsOpen(repo)}
                >
                  Settings
                </Button>
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      {/* Settings Dialog */}
      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Repository Settings</DialogTitle>
        <DialogContent sx={{ pt: 3 }}>
          {selectedRepo && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Typography variant="subtitle2" sx={{ color: '#666' }}>
                {selectedRepo.name}
              </Typography>

              <FormControlLabel
                control={
                  <Switch
                    checked={selectedRepo.enabled}
                    onChange={(e) =>
                      setSelectedRepo({ ...selectedRepo, enabled: e.target.checked })
                    }
                  />
                }
                label="Enable scanning for this repository"
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={selectedRepo.fail_on_critical}
                    onChange={(e) =>
                      setSelectedRepo({
                        ...selectedRepo,
                        fail_on_critical: e.target.checked,
                      })
                    }
                  />
                }
                label="Block PR merge on CRITICAL issues"
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={selectedRepo.fail_on_error}
                    onChange={(e) =>
                      setSelectedRepo({ ...selectedRepo, fail_on_error: e.target.checked })
                    }
                  />
                }
                label="Block PR merge on ERROR issues"
              />

              <Typography variant="caption" sx={{ color: '#999', mt: 1 }}>
                When enabled, PRs with issues at or above the selected severity will be blocked
                from merging.
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>Cancel</Button>
          <Button onClick={handleSettingsSave} variant="contained" disabled={loading}>
            {loading ? <CircularProgress size={20} /> : 'Save Settings'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Back Button */}
      <Box sx={{ mt: 4, pt: 2, borderTop: '1px solid #e0e0e0' }}>
        <Button
          variant="text"
          onClick={() => navigate('/dashboard')}
          sx={{ color: '#1976d2' }}
        >
          ← Back to Dashboard
        </Button>
      </Box>
    </Container>
  );
};

export default GitHubConnect;
