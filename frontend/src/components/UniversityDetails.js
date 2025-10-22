import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Button, Grid, Avatar, Chip,
  CircularProgress, Stack
} from '@mui/material';
import {
  LocationOn, AttachMoney, TrendingUp, Schedule, School, Assignment,
  CheckCircle, ArrowBack, ArrowForward
} from '@mui/icons-material';
import api from '../services/api';

const UniversityDetails = ({ university, studentData, onNext, onBack }) => {
  const [insights, setInsights] = useState(null);
  const [loadingInsights, setLoadingInsights] = useState(false);

  const fetchInsights = async () => {
    setLoadingInsights(true);
    
    try {
      const response = await api.getUniversityInsights(university.name, {
        name: studentData.name || 'Student',
        gpa: studentData.gpa,
        field_of_study: studentData.field_of_study,
        experience: studentData.experience,
        skills: studentData.skills
      });
      
      setInsights(response.university || response);
    } catch (error) {
      console.error('Failed to load insights:', error);
    } finally {
      setLoadingInsights(false);
    }
  };

  // Auto-fetch insights when component loads
  useEffect(() => {
    if (university && studentData) {
      fetchInsights();
    }
  }, [university, studentData]);

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 2 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          University Details
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Review university information and proceed with your application
        </Typography>
      </Box>

      {/* University Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <Avatar
              sx={{
                width: 60,
                height: 60,
                bgcolor: 'primary.main',
                fontSize: '1.5rem',
                fontWeight: 700
              }}
            >
              {university.name.charAt(0)}
            </Avatar>
            
            <Box sx={{ flex: 1 }}>
              <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
                {university.name}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 1, flexWrap: 'wrap' }}>
                <Chip 
                  icon={<LocationOn />} 
                  label={university.location} 
                  color="primary"
                  size="small"
                />
                <Chip 
                  label={university.ranking} 
                  variant="outlined"
                  size="small"
                />
                {university.matchScore && (
                  <Chip 
                    label={`${university.matchScore}% Match`} 
                    color="success"
                    size="small"
                  />
                )}
              </Box>
              <Typography variant="body2" sx={{ mb: 1 }}>
                {university.description}
              </Typography>
            </Box>
          </Box>
          
          <Grid container spacing={2}>
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center', p: 1.5, bgcolor: 'grey.50', borderRadius: 1 }}>
                <AttachMoney sx={{ fontSize: 24, color: 'success.main', mb: 0.5 }} />
                <Typography variant="subtitle2" sx={{ fontWeight: 600, fontSize: '0.9rem' }}>
                  {university.tuition}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Tuition
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center', p: 1.5, bgcolor: 'grey.50', borderRadius: 1 }}>
                <TrendingUp sx={{ fontSize: 24, color: 'warning.main', mb: 0.5 }} />
                <Typography variant="subtitle2" sx={{ fontWeight: 600, fontSize: '0.9rem' }}>
                  {university.gpa_requirement}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Min GPA
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center', p: 1.5, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Schedule sx={{ fontSize: 24, color: 'error.main', mb: 0.5 }} />
                <Typography variant="body2" sx={{ fontWeight: 600, fontSize: '0.8rem' }}>
                  {university.deadline}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Deadline
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center', p: 1.5, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, fontSize: '0.9rem' }}>
                  {university.acceptance_rate}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Acceptance Rate
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Programs */}
      <Card sx={{ mb: 4 }}>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <School color="primary" />
            Available Programs
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {university.programs?.map((program, idx) => (
              <Chip 
                key={idx} 
                label={program} 
                color="primary" 
                variant="outlined"
              />
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Detailed Insights */}
      {loadingInsights ? (
        <Card sx={{ mb: 4 }}>
          <CardContent sx={{ p: 4, textAlign: 'center' }}>
            <CircularProgress sx={{ mb: 2 }} />
            <Typography variant="body2">
              Loading detailed admission information...
            </Typography>
          </CardContent>
        </Card>
      ) : insights && insights.detailed_info ? (
        <Stack spacing={3} sx={{ mb: 4 }}>
          {/* Admission Requirements */}
          <Card>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Assignment color="primary" />
                Admission Requirements
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                    Required Documents:
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    {insights.detailed_info.admission_requirements.documents_needed?.map((doc, idx) => (
                      <Chip key={idx} label={doc} size="small" sx={{ mr: 1, mb: 1 }} />
                    ))}
                  </Box>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Typography variant="body2">
                      <strong>English Requirement:</strong> {insights.detailed_info.admission_requirements.english_requirement}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Entrance Exam:</strong> {insights.detailed_info.admission_requirements.entrance_exam}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Minimum GPA:</strong> {insights.detailed_info.admission_requirements.gpa_minimum}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Placement Statistics */}
          <Card>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingUp color="primary" />
                Placement Statistics
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'success.main', borderRadius: 2, color: 'white' }}>
                    <Typography variant="h4" sx={{ fontWeight: 700 }}>
                      {insights.detailed_info.placement_statistics.placement_rate}
                    </Typography>
                    <Typography variant="body2">Placement Rate</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'primary.main', borderRadius: 2, color: 'white' }}>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {insights.detailed_info.placement_statistics.average_package}
                    </Typography>
                    <Typography variant="body2">Average Package</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'warning.main', borderRadius: 2, color: 'white' }}>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {insights.detailed_info.placement_statistics.highest_package}
                    </Typography>
                    <Typography variant="body2">Highest Package</Typography>
                  </Box>
                </Grid>
              </Grid>
              <Grid container spacing={3} sx={{ mt: 2 }}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                    Popular Roles:
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {insights.detailed_info.placement_statistics.popular_roles?.map((role, idx) => (
                      <Chip key={idx} label={role} color="primary" size="small" />
                    ))}
                  </Box>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                    Top Recruiters:
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {insights.detailed_info.placement_statistics.top_recruiters?.map((recruiter, idx) => (
                      <Chip key={idx} label={recruiter} variant="outlined" size="small" />
                    ))}
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Match Analysis */}
          {insights.match_analysis && (
            <Card>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CheckCircle color="primary" />
                  Your Match Analysis
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={4}>
                    <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'info.main', borderRadius: 2, color: 'white' }}>
                      <Typography variant="h5" sx={{ fontWeight: 700 }}>
                        {insights.match_analysis.admission_probability}
                      </Typography>
                      <Typography variant="body2">Admission Probability</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                      Your Strengths:
                    </Typography>
                    <Box>
                      {insights.match_analysis.strengths?.map((strength, idx) => (
                        <Typography key={idx} variant="body2" sx={{ mb: 0.5 }}>
                          ✓ {strength}
                        </Typography>
                      ))}
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                      Recommendations:
                    </Typography>
                    <Box>
                      {insights.match_analysis.recommendations?.map((rec, idx) => (
                        <Typography key={idx} variant="body2" sx={{ mb: 0.5 }}>
                          • {rec}
                        </Typography>
                      ))}
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          )}
        </Stack>
      ) : (
        <Card sx={{ mb: 4 }}>
          <CardContent sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Click "Get Detailed Insights" to view admission requirements and placement statistics
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Action Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
        <Button
          variant="outlined"
          startIcon={<ArrowBack />}
          onClick={onBack}
          size="large"
        >
          Back to Results
        </Button>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            endIcon={<ArrowForward />}
            onClick={onNext}
            size="large"
            sx={{ 
              backgroundColor: '#635bff',
              '&:hover': { backgroundColor: '#4c44db' }
            }}
          >
            Apply Now
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default UniversityDetails;
