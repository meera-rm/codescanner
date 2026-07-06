import { Box, Alert } from '@mui/material';

const CacheManagement = () => {
  return (
    <Box sx={{ p: 2 }}>
      <Alert severity="info">
        Cache Management panel is being updated. In the meantime, you can manage Redis cache via the API endpoints or command line.
      </Alert>
    </Box>
  );
};

export default CacheManagement;
