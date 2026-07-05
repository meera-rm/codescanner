import React, { useState, useEffect } from 'react';
import { Paper, Typography, Box, Slider, Switch, FormControlLabel, Button, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
import { Settings, Moon, Sun } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

interface DashboardConfig {
  refreshInterval: number;
  alertThreshold: number;
  darkMode: boolean;
  autoExport: boolean;
}

interface DashboardSettingsProps {
  config: DashboardConfig;
  onConfigChange: (config: DashboardConfig) => void;
}

const DashboardSettings: React.FC<DashboardSettingsProps> = ({ config, onConfigChange }) => {
  const { isDarkMode, toggleDarkMode } = useTheme();
  const [open, setOpen] = useState(false);
  const [localConfig, setLocalConfig] = useState(config);

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const handleSave = () => {
    onConfigChange(localConfig);
    localStorage.setItem('dashboardConfig', JSON.stringify(localConfig));
    handleClose();
  };

  const handleRefreshChange = (value: number | number[]) => {
    setLocalConfig({ ...localConfig, refreshInterval: value as number });
  };

  const handleThresholdChange = (value: number | number[]) => {
    setLocalConfig({ ...localConfig, alertThreshold: value as number });
  };

  return (
    <>
      <Button
        startIcon={<Settings size={20} />}
        onClick={handleOpen}
        sx={{ textTransform: 'none', color: '#666' }}
      >
        Settings
      </Button>

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>Dashboard Settings</DialogTitle>
        <DialogContent sx={{ pt: 3 }}>
          {/* Dark Mode */}
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              {isDarkMode ? <Moon size={20} /> : <Sun size={20} />}
              <Typography variant="subtitle1">Dark Mode</Typography>
            </Box>
            <Switch
              checked={isDarkMode}
              onChange={toggleDarkMode}
            />
          </Box>

          {/* Refresh Interval */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle1" sx={{ mb: 2 }}>
              Auto-Refresh Interval: {localConfig.refreshInterval}s
            </Typography>
            <Slider
              min={10}
              max={300}
              step={10}
              value={localConfig.refreshInterval}
              onChange={handleRefreshChange}
              marks={[
                { value: 10, label: '10s' },
                { value: 150, label: '2.5m' },
                { value: 300, label: '5m' },
              ]}
            />
          </Box>

          {/* Alert Threshold */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle1" sx={{ mb: 2 }}>
              Alert Threshold: {localConfig.alertThreshold}%
            </Typography>
            <Slider
              min={50}
              max={95}
              step={5}
              value={localConfig.alertThreshold}
              onChange={handleThresholdChange}
              marks={[
                { value: 50, label: 'Low' },
                { value: 75, label: 'Medium' },
                { value: 95, label: 'High' },
              ]}
            />
            <Typography variant="caption" sx={{ color: '#999' }}>
              Alerts trigger when health drops below this threshold
            </Typography>
          </Box>

          {/* Auto-Export */}
          <Box sx={{ mb: 3 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={localConfig.autoExport}
                  onChange={(e) =>
                    setLocalConfig({ ...localConfig, autoExport: e.target.checked })
                  }
                />
              }
              label="Auto-Export Daily Report"
            />
            <Typography variant="caption" sx={{ color: '#999', display: 'block', mt: 1 }}>
              Automatically export dashboard data daily at 9 AM
            </Typography>
          </Box>
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSave} variant="contained">
            Save Settings
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default DashboardSettings;
