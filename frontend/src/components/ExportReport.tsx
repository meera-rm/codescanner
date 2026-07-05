import React from 'react';
import { Button, Menu, MenuItem } from '@mui/material';
import { Download } from 'lucide-react';

interface ExportReportProps {
  data: any;
  filename?: string;
}

const ExportReport: React.FC<ExportReportProps> = ({ data, filename = 'dashboard-report' }) => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const exportJSON = () => {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    downloadFile(blob, `${filename}.json`);
    handleClose();
  };

  const exportCSV = () => {
    let csv = 'Dashboard Report\n';
    csv += `Generated: ${new Date().toISOString()}\n\n`;

    if (data.summary) {
      csv += 'Summary\n';
      csv += 'Key,Value\n';
      Object.entries(data.summary).forEach(([key, val]) => {
        if (typeof val === 'object') {
          Object.entries(val).forEach(([k, v]) => {
            csv += `${k},${v}\n`;
          });
        }
      });
    }

    const blob = new Blob([csv], { type: 'text/csv' });
    downloadFile(blob, `${filename}.csv`);
    handleClose();
  };

  const downloadFile = (blob: Blob, name: string) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  return (
    <>
      <Button
        startIcon={<Download size={20} />}
        onClick={handleClick}
        sx={{ textTransform: 'none', color: '#666' }}
      >
        Export
      </Button>
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleClose}>
        <MenuItem onClick={exportJSON}>Export as JSON</MenuItem>
        <MenuItem onClick={exportCSV}>Export as CSV</MenuItem>
      </Menu>
    </>
  );
};

export default ExportReport;
