import React, { useState, useEffect } from 'react';
import { 
  Card, CardContent, Typography, Button, Grid, CircularProgress,
  Chip, Box, Alert, Avatar, TextField, InputAdornment
} from '@mui/material';
import { 
  Search, LocationOn, ArrowBack, ArrowForward, AutoAwesome
} from '@mui/icons-material';
import api from '../services/api';

const UniversitySearch = ({ studentData, onSelect, onNext, onBack, universities: cachedUniversities, searchMetadata: cachedMetadata }) => {
  const [loading, setLoading] = useState(false);
  const [universities, setUniversities] = useState(cachedUniversities || []);
  const [searchMetadata, setSearchMetadata] = useState(cachedMetadata || null);
  const [searchQuery, setSearchQuery] = useState('');
  const [nlpSearchActive, setNlpSearchActive] = useState(false);

  const handleNLPSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    try {
      const response = await api.searchUniversities({
        query: searchQuery
      });
      
      setUniversities(response.data.universities || []);
      setSearchMetadata(response.data.search_metadata);
    } catch (error) {
      console.error('NLP Search failed:', error);
    }
    setLoading(false);
  };

  const searchUniversities = async () => {
    if (cachedUniversities && cachedUniversities.length > 0) {
      return;
    }

    setLoading(true);
    
    try {
      // Check if this is a Discovery/NLP search (only has query)
      if (studentData.query && !studentData.field_of_study) {
        const response = await api.searchUniversities({
          query: studentData.query
        });
        
        setUniversities(response.data.universities || []);
        setSearchMetadata(response.data.search_metadata);
      } else {
        // Regular structured search
        const response = await api.searchUniversities({
          field_of_study: studentData.field_of_study,
          location_preference: studentData.location_preference,
          gpa: studentData.gpa,
          research_interests: studentData.research_interests
        });
        
        setUniversities(response.data.universities || []);
        setSearchMetadata(response.data.search_metadata);
      }
      
    } catch (error) {
      console.error('Search failed:', error);
      setUniversities([]);
      setSearchMetadata(null);
    }
    
    setLoading(false);
  };

  useEffect(() => {
    searchUniversities();
  }, []);

  const handleApplyToUniversity = (university) => {
    onSelect(university, universities, searchMetadata);
    onNext();
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 200 }}>
        <CircularProgress size={24} sx={{ mr: 2 }} />
        <Typography variant="h6" sx={{ fontSize: '1rem' }}>
          Finding matching universities...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: '100%', width: '100%', p: 3 }}>
      {/* NLP Search Input */}
      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          placeholder="Try: 'Architecture universities Italy top ranked' or 'Computer Science MIT Stanford'"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleNLPSearch()}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <AutoAwesome color="primary" />
              </InputAdornment>
            ),
            endAdornment: (
              <InputAdornment position="end">
                <Button 
                  variant="contained" 
                  size="small"
                  onClick={handleNLPSearch}
                  disabled={!searchQuery.trim() || loading}
                >
                  Search
                </Button>
              </InputAdornment>
            )
          }}
          sx={{ mb: 2 }}
        />
      </Box>

      <Typography variant="h4" className="section-heading">
        University Recommendations
      </Typography>
      
      {searchMetadata && (
        <Alert severity="info" sx={{ mb: 3 }}>
          Found {universities.length} universities matching your profile
        </Alert>
      )}

      <Grid container spacing={3} className="university-grid">
        {universities.map((university, index) => (
          <Grid item xs={12} md={6} lg={4} key={university.id || index}>
            <Card 
              sx={{ 
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                borderRadius: 2,
                border: '1px solid',
                borderColor: 'divider',
                transition: 'all 0.2s ease',
                '&:hover': { 
                  transform: 'translateY(-2px)',
                  boxShadow: 2,
                  borderColor: 'primary.light',
                },
              }}
            >
              <CardContent sx={{ p: 2, flex: 1, display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
                  <Avatar
                    sx={{
                      width: 32,
                      height: 32,
                      bgcolor: 'primary.main',
                      fontSize: '0.8rem',
                      fontWeight: 600
                    }}
                  >
                    {university.name.charAt(0)}
                  </Avatar>
                  
                  <Box sx={{ flex: 1, minWidth: 0 }}>
                    <Typography variant="h6" sx={{ 
                      fontWeight: 600, 
                      mb: 0.5,
                      fontSize: '0.9rem',
                      lineHeight: 1.2
                    }}>
                      {university.name}
                    </Typography>
                    
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                      <Chip 
                        icon={<LocationOn sx={{ fontSize: '12px !important' }} />}
                        label={university.location} 
                        size="small" 
                        variant="outlined"
                        sx={{ fontSize: '0.65rem', height: 18 }}
                      />
                      {university.matchScore && (
                        <Chip 
                          label={`${university.matchScore}% Match`} 
                          color="primary"
                          size="small"
                          sx={{ fontSize: '0.65rem', height: 18 }}
                        />
                      )}
                    </Box>
                  </Box>
                </Box>

                <Typography variant="body2" sx={{ 
                  mb: 1.5, 
                  lineHeight: 1.3,
                  fontSize: '0.75rem',
                  color: 'text.secondary',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden'
                }}>
                  {university.description}
                </Typography>

                <Grid container spacing={1} sx={{ mb: 1.5 }}>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary" sx={{
                      fontSize: '0.6rem',
                      fontWeight: 500,
                      textTransform: 'uppercase'
                    }}>
                      Tuition
                    </Typography>
                    <Typography variant="body2" sx={{ 
                      fontWeight: 600,
                      fontSize: '0.7rem'
                    }}>
                      {university.tuition}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary" sx={{
                      fontSize: '0.6rem',
                      fontWeight: 500,
                      textTransform: 'uppercase'
                    }}>
                      Acceptance
                    </Typography>
                    <Typography variant="body2" sx={{ 
                      fontWeight: 600,
                      fontSize: '0.7rem'
                    }}>
                      {university.acceptance_rate}
                    </Typography>
                  </Grid>
                </Grid>

                <Button
                  variant="contained"
                  fullWidth
                  size="small"
                  onClick={() => handleApplyToUniversity(university)}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={10} color="inherit" /> : null}
                  sx={{ 
                    mt: 'auto',
                    fontSize: '0.7rem',
                    py: 0.75,
                    fontWeight: 600,
                    minHeight: 28
                  }}
                >
                  {loading ? 'Loading...' : 'View Details'}
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-start' }}>
        <Button onClick={onBack} startIcon={<ArrowBack />}>
          Back to Profile
        </Button>
      </Box>
    </Box>
  );
};

export default UniversitySearch;
