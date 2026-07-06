import React, { useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  Stack,
  Typography,
  MenuItem,
} from '@mui/material';

interface SearchFiltersProps {
  onSearch: (filters: Record<string, any>) => void;
  onClear?: () => void;
}

export function SearchFilters({ onSearch, onClear }: SearchFiltersProps) {
  const [searchText, setSearchText] = useState('');
  const [repository, setRepository] = useState('');
  const [platform, setPlatform] = useState('');
  const [expanded, setExpanded] = useState(false);

  const handleSearch = () => {
    const filters: Record<string, any> = {};
    if (searchText) filters.q = searchText;
    if (repository) filters.repository = repository;
    if (platform) filters.platform = platform;
    onSearch(filters);
  };

  const handleClear = () => {
    setSearchText('');
    setRepository('');
    setPlatform('');
    onClear?.();
  };

  return (
    <Box sx={{ mb: 3 }}>
      {/* Quick Search Bar */}
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
              placeholder="Search repositories, branches..."
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
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
                fullWidth
              >
                Search
              </Button>
              <Button
                variant="outlined"
                color="inherit"
                onClick={() => setExpanded(!expanded)}
                fullWidth
              >
                Filter
              </Button>
            </Stack>
          </Grid>
        </Grid>
      </Paper>

      {/* Advanced Filters Panel */}
      {expanded && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="h6" gutterBottom>
            Advanced Filters
          </Typography>

          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                select
                label="Repository"
                value={repository}
                onChange={(e) => setRepository(e.target.value)}
                fullWidth
                size="small"
              >
                <MenuItem value="">All Repositories</MenuItem>
                <MenuItem value="my-repo">my-repo</MenuItem>
                <MenuItem value="backend">backend</MenuItem>
                <MenuItem value="frontend">frontend</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                select
                label="Platform"
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
                fullWidth
                size="small"
              >
                <MenuItem value="">All Platforms</MenuItem>
                <MenuItem value="github">GitHub</MenuItem>
                <MenuItem value="jenkins">Jenkins</MenuItem>
                <MenuItem value="gitlab">GitLab</MenuItem>
                <MenuItem value="circleci">CircleCI</MenuItem>
              </TextField>
            </Grid>
          </Grid>

          <Stack direction="row" spacing={1}>
            <Button variant="contained" onClick={handleSearch}>
              Apply Filters
            </Button>
            <Button variant="outlined" onClick={handleClear}>
              Clear All
            </Button>
          </Stack>
        </Paper>
      )}
    </Box>
  );
}

export default SearchFilters;
