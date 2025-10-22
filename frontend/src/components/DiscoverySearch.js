import React, { useState } from 'react';
import { 
  Box, TextField, InputAdornment, Button, Chip, Stack, CircularProgress
} from '@mui/material';
import { AutoAwesome, TravelExplore } from '@mui/icons-material';

const DiscoverySearch = ({ onSearch, loading }) => {
  const [query, setQuery] = useState('');
  const [searching, setSearching] = useState(false);
  
  const suggestions = [
    "Architecture universities Italy top ranked",
    "Computer Science MIT Stanford", 
    "Engineering programs Germany affordable"
  ];

  const handleSearch = async () => {
    if (query.trim()) {
      setSearching(true);
      await onSearch(query);
      setSearching(false);
    }
  };

  return (
    <Box>
      <TextField
        fullWidth
        placeholder="Try: 'Architecture universities Italy top ranked'"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <TravelExplore color="primary" />
            </InputAdornment>
          ),
          endAdornment: (
            <InputAdornment position="end">
              <Button 
                variant="contained" 
                size="small"
                onClick={handleSearch}
                disabled={!query.trim() || loading || searching}
                startIcon={searching ? <CircularProgress size={12} color="inherit" /> : <AutoAwesome />}
                sx={{ minWidth: 80 }}
              >
                {searching ? 'Searching...' : 'Discover'}
              </Button>
            </InputAdornment>
          )
        }}
        sx={{ mb: 2 }}
      />
      
      <Stack direction="row" spacing={1} flexWrap="wrap">
        {suggestions.map((suggestion, index) => (
          <Chip
            key={index}
            label={suggestion}
            variant="outlined"
            size="small"
            onClick={() => setQuery(suggestion)}
            sx={{ mb: 1, cursor: 'pointer' }}
          />
        ))}
      </Stack>
    </Box>
  );
};

export default DiscoverySearch;
