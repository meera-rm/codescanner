import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Tabs, Tab, Paper, Typography, Button } from '@mui/material';
import PerformanceMonitoring from '../components/PerformanceMonitoring';
import AlertConfiguration from '../components/AlertConfiguration';
import CacheManagement from '../components/CacheManagement';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`monitoring-tabpanel-${index}`}
      aria-labelledby={`monitoring-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `monitoring-tab-${index}`,
    'aria-controls': `monitoring-tabpanel-${index}`,
  };
}

export function MonitoringDashboard() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Paper sx={{ mb: 3 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', p: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h5">
              System Monitoring & Management
            </Typography>
            <Button variant="outlined" onClick={() => navigate('/ci-dashboard')}>
              ← Back to CI Dashboard
            </Button>
          </Box>
          <Tabs value={activeTab} onChange={handleTabChange} aria-label="monitoring tabs">
            <Tab label="Performance Monitoring" {...a11yProps(0)} />
            <Tab label="Alert Configuration" {...a11yProps(1)} />
            <Tab label="Cache Management" {...a11yProps(2)} />
          </Tabs>
        </Box>
      </Paper>

      <TabPanel value={activeTab} index={0}>
        <PerformanceMonitoring />
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <AlertConfiguration />
      </TabPanel>

      <TabPanel value={activeTab} index={2}>
        <CacheManagement />
      </TabPanel>
    </Box>
  );
}

export default MonitoringDashboard;
