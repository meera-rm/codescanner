import { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Grid,
  TextField,
  Button,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Switch,
  FormControlLabel,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Paper,
} from '@mui/material';

interface AlertPreference {
  id: string;
  repository: string;
  alert_on_critical: boolean;
  alert_on_error: boolean;
  critical_threshold: number;
  error_threshold: number;
  email_enabled: boolean;
  email_address?: string;
  slack_enabled: boolean;
  slack_webhook?: string;
  alert_frequency: string;
  is_active: boolean;
}

export function AlertConfiguration() {
  const [preferences, setPreferences] = useState<AlertPreference[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingPref, setEditingPref] = useState<Partial<AlertPreference> | null>(null);
  const [testingRepo, setTestingRepo] = useState<string | null>(null);

  const fetchPreferences = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/alerts/preferences');
      const data = await response.json();
      setPreferences(data);
    } catch (err) {
      setError('Failed to load alert preferences');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPreferences();
  }, []);

  const handleOpenDialog = (pref?: AlertPreference) => {
    if (pref) {
      setEditingPref(pref);
    } else {
      setEditingPref({
        repository: 'all',
        alert_on_critical: true,
        alert_on_error: false,
        critical_threshold: 1,
        error_threshold: 5,
        email_enabled: true,
        slack_enabled: false,
        alert_frequency: 'immediate',
        is_active: true,
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingPref(null);
  };

  const handleSavePreference = async () => {
    if (!editingPref) return;

    try {
      const response = await fetch('http://localhost:8000/api/v1/alerts/preferences', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editingPref),
      });

      if (response.ok) {
        setSuccess('Alert preference saved successfully');
        setOpenDialog(false);
        fetchPreferences();
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError('Failed to save preference');
      }
    } catch (err) {
      setError('Error saving preference');
      console.error(err);
    }
  };

  const handleTestAlert = async (repo: string, channel: 'email' | 'slack') => {
    try {
      setTestingRepo(repo);
      const response = await fetch(`http://localhost:8000/api/v1/alerts/test/${repo}?channel=${channel}`, {
        method: 'POST',
      });

      if (response.ok) {
        setSuccess(`Test ${channel} alert sent to ${repo}`);
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(`Failed to send test ${channel} alert`);
      }
    } catch (err) {
      setError('Error sending test alert');
      console.error(err);
    } finally {
      setTestingRepo(null);
    }
  };

  const handleDeletePreference = async (repo: string) => {
    if (!window.confirm(`Delete alert preference for ${repo}?`)) return;

    try {
      await fetch(`http://localhost:8000/api/v1/alerts/preferences/${repo}`, {
        method: 'DELETE',
      });
      setSuccess('Alert preference deleted');
      fetchPreferences();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Failed to delete preference');
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

      <Box sx={{ mb: 3 }}>
        <Button variant="contained" color="primary" onClick={() => handleOpenDialog()}>
          + Add Alert Preference
        </Button>
      </Box>

      {preferences.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            No alert preferences configured. Click "Add Alert Preference" to create one.
          </CardContent>
        </Card>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
              <TableRow>
                <TableCell>Repository</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Slack</TableCell>
                <TableCell>Critical Threshold</TableCell>
                <TableCell>Error Threshold</TableCell>
                <TableCell>Active</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {preferences.map((pref) => (
                <TableRow key={pref.id}>
                  <TableCell>{pref.repository}</TableCell>
                  <TableCell>
                    {pref.email_enabled ? (
                      <span>✅ {pref.email_address}</span>
                    ) : (
                      <span>❌</span>
                    )}
                  </TableCell>
                  <TableCell>
                    {pref.slack_enabled ? '✅' : '❌'}
                  </TableCell>
                  <TableCell>{pref.critical_threshold}</TableCell>
                  <TableCell>{pref.error_threshold}</TableCell>
                  <TableCell>
                    {pref.is_active ? '✅' : '❌'}
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => handleOpenDialog(pref)}
                      >
                        Edit
                      </Button>
                      {pref.email_enabled && (
                        <Button
                          size="small"
                          variant="outlined"
                          disabled={testingRepo === pref.repository}
                          onClick={() => handleTestAlert(pref.repository, 'email')}
                        >
                          Test Email
                        </Button>
                      )}
                      {pref.slack_enabled && (
                        <Button
                          size="small"
                          variant="outlined"
                          disabled={testingRepo === pref.repository}
                          onClick={() => handleTestAlert(pref.repository, 'slack')}
                        >
                          Test Slack
                        </Button>
                      )}
                      <Button
                        size="small"
                        variant="outlined"
                        color="error"
                        onClick={() => handleDeletePreference(pref.repository)}
                      >
                        Delete
                      </Button>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Dialog for editing/creating preferences */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingPref?.id ? 'Edit Alert Preference' : 'Create Alert Preference'}
        </DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Repository"
                value={editingPref?.repository || ''}
                onChange={(e) => setEditingPref({ ...editingPref!, repository: e.target.value })}
                helperText="Use 'all' for global alerts"
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Critical Threshold"
                value={editingPref?.critical_threshold || 1}
                onChange={(e) => setEditingPref({ ...editingPref!, critical_threshold: parseInt(e.target.value) })}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Error Threshold"
                value={editingPref?.error_threshold || 5}
                onChange={(e) => setEditingPref({ ...editingPref!, error_threshold: parseInt(e.target.value) })}
              />
            </Grid>

            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={editingPref?.alert_on_critical || false}
                    onChange={(e) => setEditingPref({ ...editingPref!, alert_on_critical: e.target.checked })}
                  />
                }
                label="Alert on Critical Issues"
              />
            </Grid>

            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={editingPref?.alert_on_error || false}
                    onChange={(e) => setEditingPref({ ...editingPref!, alert_on_error: e.target.checked })}
                  />
                }
                label="Alert on Errors"
              />
            </Grid>

            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={editingPref?.email_enabled || false}
                    onChange={(e) => setEditingPref({ ...editingPref!, email_enabled: e.target.checked })}
                  />
                }
                label="Enable Email Alerts"
              />
            </Grid>

            {editingPref?.email_enabled && (
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Email Address"
                  type="email"
                  value={editingPref?.email_address || ''}
                  onChange={(e) => setEditingPref({ ...editingPref!, email_address: e.target.value })}
                />
              </Grid>
            )}

            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={editingPref?.slack_enabled || false}
                    onChange={(e) => setEditingPref({ ...editingPref!, slack_enabled: e.target.checked })}
                  />
                }
                label="Enable Slack Alerts"
              />
            </Grid>

            {editingPref?.slack_enabled && (
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Slack Webhook URL"
                  type="password"
                  value={editingPref?.slack_webhook || ''}
                  onChange={(e) => setEditingPref({ ...editingPref!, slack_webhook: e.target.value })}
                />
              </Grid>
            )}

            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={editingPref?.is_active || false}
                    onChange={(e) => setEditingPref({ ...editingPref!, is_active: e.target.checked })}
                  />
                }
                label="Active"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSavePreference} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default AlertConfiguration;
