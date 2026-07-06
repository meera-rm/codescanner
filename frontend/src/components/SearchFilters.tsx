import React, { useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  Stack,
  Typography,
} from '@mui/material';

interface SearchFilter {
  q?: string;
  repository?: string;
  platform?: string;
  status?: string;
  branch?: string;
  min_critical?: number;
  max_critical?: number;
  min_errors?: number;
  max_errors?: number;
  days?: number;
  limit?: number;
}

interface SearchFiltersProps {
  onSearch: (filters: SearchFilter) => void;
  onClear?: () => void;
}

const SearchFilters: React.FC<SearchFiltersProps> = ({ onSearch, onClear }) => {
  const [filters, setFilters] = useState<SearchFilter>({
    q: '',
    days: 30,
    limit: 20,
  });
  const [expanded, setExpanded] = useState(false);

  const handleSearch = () => {
    onSearch(filters);
  };

  const handleClear = () => {
    setFilters({ q: '', days: 30, limit: 20 });
    onClear?.();
  };

  return (
    <Box sx={{ mb: 3 }}>
      <Paper
        sx={{
          p: 2,
          mb: 2,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
        }}
      >
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={8}>
            <TextField
              fullWidth
              placeholder="Search repositories, branches, platforms..."
              value={filters.q || ''}
              onChange={(e) => {
                setFilters(prev => ({ ...prev, q: e.target.value }));
              }}
              variant="outlined"
              size="small"
              sx={{
                '& .MuiOutlinedInput-root': {
                  color: 'white',
                  '& fieldset': { borderColor: 'rgba(255,255,255,0.3)' },
                  '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.5)' },
                  '&.Mui-focused fieldset': { borderColor: 'white' },
                },
                '& .MuiOutlinedInput-input::placeholder': {
                  color: 'rgba(255,255,255,0.7)',
                  opacity: 1,
                },
              }}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <Stack direction="row" spacing={1}>
              <Button
                variant="contained"
                color="inherit"
                onClick={handleSearch}
              >
                Search
              </Button>
              <Button
                variant="outlined"
                color="inherit"
                onClick={() => setExpanded(!expanded)}
              >
                Advanced
              </Button>
            </Stack>
          </Grid>
        </Grid>
      </Paper>

      {expanded && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="h6" gutterBottom>
            Advanced Filters Coming Soon
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Additional filtering options will be available in the next update.
          </Typography>
          <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
            <Button
              variant="contained"
              onClick={handleSearch}
            >
              Apply
            </Button>
            <Button
              variant="outlined"
              onClick={handleClear}
            >
              Clear
            </Button>
          </Stack>
        </Paper>
      )}
    </Box>
  );
};

export default SearchFilters;
