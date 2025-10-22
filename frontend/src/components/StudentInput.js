import React, { useState } from 'react';
import { 
  Card, CardContent, Typography, TextField, Button, Grid, 
  FormControl, InputLabel, Select, MenuItem, Chip, Box,
  LinearProgress, Stack, CircularProgress, Tabs, Tab, Avatar,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper
} from '@mui/material';
import {
  Person, Email, School, LocationOn, Grade,
  Add, Delete, ArrowForward, AutoAwesome, Dashboard, Search, Visibility
} from '@mui/icons-material';
import DiscoverySearch from './DiscoverySearch';

const StudentInput = ({ data, setData, onNext }) => {
  const [formData, setFormData] = useState({
    name: data.name || '',
    email: data.email || '',
    field_of_study: data.field_of_study || '',
    location_preference: data.location_preference || '',
    gpa: data.gpa || '',
    gre_score: data.gre_score || '',
    toefl_score: data.toefl_score || '',
    research_interests: data.research_interests || [],
    budget_range: data.budget_range || '',
    program_level: data.program_level || '',
    language_preference: data.language_preference || ''
  });

  const [newInterest, setNewInterest] = useState('');
  const [profileStrength, setProfileStrength] = useState(0);
  const [loading, setLoading] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [dashboardData, setDashboardData] = useState(null);
  const [loadingDashboard, setLoadingDashboard] = useState(false);
  const [loadingReport, setLoadingReport] = useState(null); // Changed to track specific application ID

  const handleChange = (e) => {
    const newFormData = { ...formData, [e.target.name]: e.target.value };
    setFormData(newFormData);
    calculateProfileStrength(newFormData);
  };

  const calculateProfileStrength = (data) => {
    let strength = 0;
    if (data.name) strength += 15;
    if (data.email) strength += 15;
    if (data.field_of_study) strength += 20;
    if (data.location_preference) strength += 15;
    if (data.gpa) strength += 20;
    if (data.gre_score) strength += 10;
    if (data.toefl_score) strength += 5;
    setProfileStrength(Math.min(strength, 100));
  };

  React.useEffect(() => {
    calculateProfileStrength(formData);
  }, [formData]);

  const addInterest = () => {
    if (newInterest.trim() && !formData.research_interests.includes(newInterest.trim())) {
      const newFormData = {
        ...formData,
        research_interests: [...formData.research_interests, newInterest.trim()]
      };
      setFormData(newFormData);
      setNewInterest('');
    }
  };

  const removeInterest = (interest) => {
    const newFormData = {
      ...formData,
      research_interests: formData.research_interests.filter(i => i !== interest)
    };
    setFormData(newFormData);
  };

  const handleSubmit = async () => {
    setLoading(true);
    setData(formData);
    setTimeout(() => {
      setLoading(false);
      onNext();
    }, 1000);
  };

  const isFormValid = () => {
    return true; // Allow submission without validation
  };

  const handleDiscoverySearch = async (query) => {
    // Save only the query for NLP search, don't auto-fill form
    setData({ query: query });
    onNext();
  };

  const fetchDashboardData = async () => {
    setLoadingDashboard(true);
    try {
      // Import the student service function
      const { getStudentApplications } = await import('../services/student/studentService');
      const data = await getStudentApplications();
      setDashboardData(data || []);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setDashboardData([]);
    } finally {
      setLoadingDashboard(false);
    }
  };

  React.useEffect(() => {
    if (tabValue === 1) {
      fetchDashboardData();
    }
  }, [tabValue]);

  const handleViewReport = async (reportUrl, applicationId) => {
    if (!reportUrl) {
      alert('No report available for this application');
      return;
    }
    
    try {
      setLoadingReport(applicationId);
      console.log(`📄 Opening report for application: ${applicationId}`);
      
      // Import the report service function
      const { getReportPresignedUrl } = await import('../services/admin/reportService');
      const result = await getReportPresignedUrl(reportUrl);
      
      if (result.success) {
        window.open(result.url, '_blank');
        console.log(`✅ Report opened successfully`);
      } else {
        console.error('❌ Failed to get report URL:', result.error);
        alert(`Failed to open report: ${result.error}`);
      }
    } catch (error) {
      console.error('❌ Error opening report:', error);
      alert(`Error opening report: ${error.message}`);
    } finally {
      setLoadingReport(null);
    }
  };

  const fields = [
    'Computer Science', 'Engineering', 'Business Administration', 'Medicine', 'Law',
    'Liberal Arts', 'Natural Sciences', 'Psychology', 'Economics', 'Mathematics',
    'Physics', 'Chemistry', 'Biology', 'Environmental Science', 'Architecture',
    'Fine Arts', 'Music', 'Literature', 'Philosophy', 'Political Science',
    'International Relations', 'Journalism', 'Marketing', 'Finance', 'Accounting', 'Agriculture'
  ];

  const locations = [
    'United States', 'Canada', 'United Kingdom', 'Germany', 'Australia', 
    'Netherlands', 'Sweden', 'Switzerland', 'Singapore', 'Japan',
    'France', 'Italy', 'Spain', 'Norway', 'Denmark', 'Finland',
    'New Zealand', 'South Korea', 'China', 'India', 'Brazil', 'Mexico'
  ];

  const budgetRanges = [
    'Under $10,000', '$10,000 - $25,000', '$25,000 - $50,000', 
    '$50,000 - $75,000', '$75,000+', 'No preference'
  ];

  const programLevels = [
    'Bachelor\'s Degree', 'Master\'s Degree', 'PhD/Doctorate', 'Certificate Program'
  ];

  const languages = [
    'English', 'German', 'French', 'Spanish', 'Dutch', 'Swedish', 
    'Italian', 'Japanese', 'Korean', 'Mandarin'
  ];

  const commonInterests = [
    'Artificial Intelligence', 'Machine Learning', 'Data Science', 'Cybersecurity',
    'Software Engineering', 'Robotics', 'Blockchain', 'Cloud Computing'
  ];

  return (
    <Box className="card-container">
      <Box sx={{ mb: 2, textAlign: 'center' }}>
        <Typography variant="h6" sx={{ fontWeight: 600, color: '#635bff', mb: 0.5 }}>
          Find Your Perfect University
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Use AI-powered search or build your academic profile
        </Typography>
      </Box>

      {/* Tabs */}
      <Tabs 
        value={tabValue} 
        onChange={(e, newValue) => setTabValue(newValue)} 
        sx={{ 
          mb: 2, 
          borderBottom: 1, 
          borderColor: 'divider',
          '& .MuiTab-root': { 
            fontSize: '0.875rem',
            minHeight: 40,
            textTransform: 'none'
          }
        }}
      >
        <Tab 
          icon={<Search sx={{ fontSize: 18 }} />} 
          label="AI Search" 
          sx={{ fontWeight: 500 }}
        />
        <Tab 
          icon={<Dashboard sx={{ fontSize: 18 }} />} 
          label="Student Dashboard" 
          sx={{ fontWeight: 500 }}
        />
      </Tabs>

      {/* Tab Content */}
      {tabValue === 0 && (
        <Box>
          {/* AI Discovery Search Tab */}
          <Card sx={{ mb: 2, p: 2, maxWidth: 1200, mx: 'auto' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <AutoAwesome color="primary" sx={{ fontSize: 20 }} />
              <Typography variant="h6" sx={{ fontSize: '1rem' }}>
                AI Discovery Search
              </Typography>
            </Box>
            <DiscoverySearch onSearch={handleDiscoverySearch} />
          </Card>

          <Typography variant="caption" color="text.secondary" sx={{ textAlign: 'center', display: 'block', my: 2 }}>
            OR fill your detailed profile below
          </Typography>

          {/* Existing Form Content */}

      <Card sx={{ maxWidth: 1200, mx: 'auto' }}>
        <CardContent sx={{ p: 3 }}>
          {profileStrength > 0 && (
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Profile completion
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  {profileStrength}%
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={profileStrength} 
                sx={{ height: 3, borderRadius: 2 }}
              />
            </Box>
          )}

          <Stack spacing={2}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  size="small"
                  label="Full name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  size="small"
                  label="Email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                />
              </Grid>
            </Grid>

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth size="small">
                  <InputLabel>Field of study</InputLabel>
                  <Select
                    name="field_of_study"
                    value={formData.field_of_study}
                    onChange={handleChange}
                    label="Field of study"
                  >
                    {fields.map((field) => (
                      <MenuItem key={field} value={field}>
                        {field}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth size="small">
                  <InputLabel>Program level</InputLabel>
                  <Select
                    name="program_level"
                    value={formData.program_level}
                    onChange={handleChange}
                    label="Program level"
                  >
                    {programLevels.map((level) => (
                      <MenuItem key={level} value={level}>
                        {level}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth size="small">
                  <InputLabel>Preferred country</InputLabel>
                  <Select
                    name="location_preference"
                    value={formData.location_preference}
                    onChange={handleChange}
                    label="Preferred country"
                  >
                    {locations.map((location) => (
                      <MenuItem key={location} value={location}>
                        {location}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth size="small">
                  <InputLabel>Budget range</InputLabel>
                  <Select
                    name="budget_range"
                    value={formData.budget_range}
                    onChange={handleChange}
                    label="Budget range"
                  >
                    {budgetRanges.map((range) => (
                      <MenuItem key={range} value={range}>
                        {range}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth size="small">
                  <InputLabel>Language preference</InputLabel>
                  <Select
                    name="language_preference"
                    value={formData.language_preference}
                    onChange={handleChange}
                    label="Language preference"
                  >
                    {languages.map((lang) => (
                      <MenuItem key={lang} value={lang}>
                        {lang}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  size="small"
                  label="GPA"
                  name="gpa"
                  value={formData.gpa}
                  onChange={handleChange}
                  helperText="On a 4.0 scale"
                />
              </Grid>
            </Grid>

            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  size="small"
                  label="GRE score"
                  name="gre_score"
                  value={formData.gre_score}
                  onChange={handleChange}
                  helperText="Optional"
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  size="small"
                  label="TOEFL/IELTS"
                  name="toefl_score"
                  value={formData.toefl_score}
                  onChange={handleChange}
                  helperText="If applicable"
                />
              </Grid>
            </Grid>

            <Box>
              <Typography variant="h6" gutterBottom>
                Research interests
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <TextField
                  placeholder="Add interest"
                  value={newInterest}
                  onChange={(e) => setNewInterest(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addInterest()}
                  sx={{ flexGrow: 1 }}
                  size="small"
                />
                <Button
                  variant="outlined"
                  onClick={addInterest}
                  disabled={!newInterest.trim()}
                  startIcon={<Add />}
                  size="small"
                >
                  Add
                </Button>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Popular:
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {commonInterests.map((interest) => (
                    <Chip
                      key={interest}
                      label={interest}
                      size="small"
                      variant="outlined"
                      onClick={() => {
                        if (!formData.research_interests.includes(interest)) {
                          setFormData({
                            ...formData,
                            research_interests: [...formData.research_interests, interest]
                          });
                        }
                      }}
                      sx={{ cursor: 'pointer' }}
                    />
                  ))}
                </Box>
              </Box>

              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', minHeight: 32 }}>
                {formData.research_interests.map((interest) => (
                  <Chip
                    key={interest}
                    label={interest}
                    onDelete={() => removeInterest(interest)}
                    color="primary"
                    size="small"
                  />
                ))}
              </Box>
            </Box>

            <Button
              variant="contained"
              size="medium"
              onClick={handleSubmit}
              disabled={!isFormValid() || loading}
              startIcon={loading ? <CircularProgress size={12} color="inherit" /> : null}
              endIcon={!loading ? <ArrowForward /> : null}
              sx={{ 
                alignSelf: 'flex-start', 
                mt: 2,
                minWidth: 140,
                minHeight: 36
              }}
            >
              {loading ? 'Processing...' : 'Find universities'}
            </Button>
          </Stack>
        </CardContent>
      </Card>
        </Box>
      )}

      {/* Dashboard Tab */}
      {tabValue === 1 && (
        <Box>
          {/* Applications Table */}
          <Card sx={{ mb: 2 }}>
            <CardContent sx={{ p: 0 }}>
              {loadingDashboard ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : dashboardData && dashboardData.length > 0 ? (
                <TableContainer>
                  <Table size="small" sx={{ minWidth: 800 }}>
                    <TableHead>
                      <TableRow sx={{ backgroundColor: '#f8f9fa' }}>
                        <TableCell sx={{ fontWeight: 600, fontSize: '0.75rem', py: 1, width: '15%' }}>Application ID</TableCell>
                        <TableCell sx={{ fontWeight: 600, fontSize: '0.75rem', py: 1, width: '20%' }}>University</TableCell>
                        <TableCell sx={{ fontWeight: 600, fontSize: '0.75rem', py: 1, width: '15%' }}>Program</TableCell>
                        <TableCell sx={{ fontWeight: 600, fontSize: '0.75rem', py: 1, width: '15%' }}>Location</TableCell>
                        <TableCell sx={{ fontWeight: 600, fontSize: '0.75rem', py: 1, width: '10%' }}>Status</TableCell>
                        <TableCell sx={{ fontWeight: 600, fontSize: '0.75rem', py: 1, width: '12%' }}>Applied On</TableCell>
                        <TableCell sx={{ fontWeight: 600, fontSize: '0.75rem', py: 1, width: '13%', textAlign: 'center' }}>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {dashboardData.map((app, index) => (
                        <TableRow key={index} sx={{ 
                          '&:hover': { backgroundColor: '#f8f9fa' },
                          '&:nth-of-type(even)': { backgroundColor: '#fafbfc' }
                        }}>
                          <TableCell sx={{ fontSize: '0.75rem', py: 1.5, fontWeight: 500 }}>
                            {app.application_id}
                          </TableCell>
                          <TableCell sx={{ fontSize: '0.75rem', py: 1.5 }}>
                            {app.university_name}
                          </TableCell>
                          <TableCell sx={{ fontSize: '0.75rem', py: 1.5 }}>
                            {app.program}
                          </TableCell>
                          <TableCell sx={{ fontSize: '0.75rem', py: 1.5 }}>
                            {app.location_preference}
                          </TableCell>
                          <TableCell sx={{ py: 1.5 }}>
                            <Chip 
                              label={app.status} 
                              color={app.status === 'ACCEPT' ? 'success' : app.status === 'REJECT' ? 'error' : 'warning'}
                              size="small"
                              sx={{ 
                                fontSize: '0.65rem',
                                height: 20,
                                fontWeight: 600
                              }}
                            />
                          </TableCell>
                          <TableCell sx={{ fontSize: '0.75rem', py: 1.5 }}>
                            {app.applied_on ? new Date(app.applied_on).toLocaleDateString() : 'N/A'}
                          </TableCell>
                          <TableCell sx={{ py: 1.5, textAlign: 'center' }}>
                            <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center', alignItems: 'center' }}>
                              {app.report && (
                                <Button
                                  size="small"
                                  variant="contained"
                                  disabled={loadingReport === app.application_id}
                                  onClick={() => handleViewReport(app.report, app.application_id)}
                                  startIcon={loadingReport === app.application_id ? 
                                    <CircularProgress size={12} sx={{ color: 'white' }} /> : 
                                    <Visibility sx={{ fontSize: 12 }} />
                                  }
                                  sx={{ 
                                    backgroundColor: '#635bff',
                                    color: 'white',
                                    fontSize: '0.65rem',
                                    px: 1,
                                    py: 0.25,
                                    minWidth: 'auto',
                                    minHeight: 24,
                                    borderRadius: 1,
                                    textTransform: 'none',
                                    fontWeight: 600,
                                    '&:hover': { backgroundColor: '#4c44db' },
                                    '&:disabled': { backgroundColor: '#cccccc' }
                                  }}
                                >
                                  {loadingReport === app.application_id ? 'Loading...' : 'View Report'}
                                </Button>
                              )}
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 3 }}>
                  No applications found. Start by using AI Search to find universities.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Box>
      )}
    </Box>
  );
};

export default StudentInput;
