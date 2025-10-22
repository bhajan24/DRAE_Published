import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Card, Grid, Chip, Button, CircularProgress,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Divider, Avatar, LinearProgress
} from '@mui/material';
import { ArrowBack, Person, School, Assignment, Description, Email, Phone } from '@mui/icons-material';
import { getApplication, getEvaluation } from '../services/admin/adminService';
import { getReportPresignedUrl } from '../services/admin/reportService';

const ApplicationDetails = ({ applicationId, applicationData, onBack }) => {
  const [application, setApplication] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingReport, setLoadingReport] = useState(false);

  useEffect(() => {
    fetchApplicationDetails();
  }, [applicationId, applicationData]);

  const fetchApplicationDetails = async () => {
    try {
      setLoading(true);
      
      // Use the data passed from AI Discovery Search or other sources
      if (applicationData) {
        console.log('Using provided application data:', applicationData);
        setApplication(applicationData);
      } else {
        console.log('No application data provided for ID:', applicationId);
        // Set empty application to avoid errors
        setApplication({
          application_id: applicationId,
          personal_information: {},
          academic_background: {},
          program_specific: {},
          documents: {}
        });
      }
      
    } catch (error) {
      console.error('Error in fetchApplicationDetails:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewReport = async () => {
    if (application?.report) {
      try {
        setLoadingReport(true);
        const result = await getReportPresignedUrl(application.report);
        if (result.success) {
          window.open(result.url, '_blank');
        }
      } catch (error) {
        console.error('Error opening report:', error);
      } finally {
        setLoadingReport(false);
      }
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ACCEPT': return 'success';
      case 'REJECT': return 'error';
      case 'WAITLIST': return 'warning';
      case 'New': return 'info';
      case 'Processing complete': return 'primary';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={onBack}
          sx={{ mr: 2, color: '#635bff' }}
        >
          Back to Dashboard
        </Button>
        <Typography variant="h5" sx={{ fontWeight: 600, color: '#0a2540' }}>
          Application Details
        </Typography>
      </Box>

      {!application ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" color="text.secondary">
            No application data found for ID: {applicationId}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Check the console for error details
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {/* Student Information Card */}
          <Grid item xs={12} md={6}>
            <Card sx={{ p: 3, borderRadius: 2, border: '1px solid #e3ebf0' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ backgroundColor: '#635bff', mr: 2 }}>
                  <Person />
                </Avatar>
                <Typography variant="h6" sx={{ fontWeight: 600, color: '#635bff' }}>
                  Student Information
                </Typography>
              </Box>
              
              <Box sx={{ '& > *': { mb: 2 } }}>
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Application ID
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 600, color: '#635bff' }}>
                    {application.application_id}
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Full Name
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 500 }}>
                    {application.personal_information?.full_name || application.name || 'Not provided'}
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Email Address
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Email sx={{ fontSize: 16, color: 'text.secondary' }} />
                    <Typography variant="body1">
                      {application.personal_information?.email || application.email || 'Not provided'}
                    </Typography>
                  </Box>
                </Box>
                
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Specialization
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 500 }}>
                    {application.program_specific?.specialization || application.field_of_study || application.query || 'Not specified'}
                  </Typography>
                </Box>
              </Box>
            </Card>
          </Grid>

          {/* Application Status Card */}
          <Grid item xs={12} md={6}>
            <Card sx={{ p: 3, borderRadius: 2, border: '1px solid #e3ebf0' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ backgroundColor: '#00d924', mr: 2 }}>
                  <Assignment />
                </Avatar>
                <Typography variant="h6" sx={{ fontWeight: 600, color: '#00d924' }}>
                  Application Status
                </Typography>
              </Box>
              
              <Box sx={{ '& > *': { mb: 2 } }}>
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Current Status
                  </Typography>
                  <Box sx={{ mt: 1 }}>
                    <Chip 
                      label={application.application_status} 
                      color={getStatusColor(application.application_status)}
                      sx={{ fontWeight: 600 }}
                    />
                  </Box>
                </Box>
                
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Final Decision
                  </Typography>
                  <Box sx={{ mt: 1 }}>
                    <Chip 
                      label={application.final_decision || 'Pending'} 
                      color={getStatusColor(application.final_decision)}
                      sx={{ fontWeight: 600 }}
                    />
                  </Box>
                </Box>
                
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Composite Score
                  </Typography>
                  <Typography variant="h5" sx={{ fontWeight: 700, color: '#635bff' }}>
                    {application.composite_score || 'N/A'}
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Confidence Level
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 500 }}>
                    {application.confidence_level || 'N/A'}
                  </Typography>
                </Box>
              </Box>
            </Card>
          </Grid>

          {/* Additional Student Information */}
          <Grid item xs={12} md={6}>
            <Card sx={{ p: 3, borderRadius: 2, border: '1px solid #e3ebf0' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, color: '#635bff' }}>
                Personal Details
              </Typography>
              
              <Box sx={{ '& > *': { mb: 2 } }}>
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Date of Birth
                  </Typography>
                  <Typography variant="body1">
                    {application.date_of_birth || 'Not provided'}
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Phone Number
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Phone sx={{ fontSize: 16, color: 'text.secondary' }} />
                    <Typography variant="body1">
                      {application.phone_number || 'Not provided'}
                    </Typography>
                  </Box>
                </Box>
                
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Address
                  </Typography>
                  <Typography variant="body1">
                    {application.address || 'Not provided'}
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Nationality
                  </Typography>
                  <Typography variant="body1">
                    {application.nationality || 'Not provided'}
                  </Typography>
                </Box>
              </Box>
            </Card>
          </Grid>

          {/* Academic Information */}
          <Grid item xs={12} md={6}>
            <Card sx={{ p: 3, borderRadius: 2, border: '1px solid #e3ebf0' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, color: '#635bff' }}>
                Academic Background
              </Typography>
              
              <Box sx={{ '& > *': { mb: 2 } }}>
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Previous Institution
                  </Typography>
                  <Typography variant="body1">
                    {application.previous_institution || 'Not provided'}
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    GPA / Percentage
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 600, color: '#635bff' }}>
                    {application.gpa || application.percentage || 'Not provided'}
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Graduation Year
                  </Typography>
                  <Typography variant="body1">
                    {application.graduation_year || 'Not provided'}
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Field of Study
                  </Typography>
                  <Typography variant="body1">
                    {application.field_of_study || application.previous_degree || 'Not provided'}
                  </Typography>
                </Box>
              </Box>
            </Card>
          </Grid>

          {/* Application Preferences */}
          <Grid item xs={12} md={6}>
            <Card sx={{ p: 3, borderRadius: 2, border: '1px solid #e3ebf0' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, color: '#635bff' }}>
                Application Preferences
              </Typography>
              
              <Box sx={{ '& > *': { mb: 2 } }}>
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Preferred Start Date
                  </Typography>
                  <Typography variant="body1">
                    {application.preferred_start_date || 'Not specified'}
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Study Mode
                  </Typography>
                  <Typography variant="body1">
                    {application.study_mode || 'Not specified'}
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Financial Aid Required
                  </Typography>
                  <Chip 
                    label={application.financial_aid_required ? 'Yes' : 'No'} 
                    color={application.financial_aid_required ? 'warning' : 'success'}
                    size="small"
                  />
                </Box>
                
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Emergency Contact
                  </Typography>
                  <Typography variant="body1">
                    {application.emergency_contact || 'Not provided'}
                  </Typography>
                </Box>
              </Box>
            </Card>
          </Grid>

          {/* Additional Information */}
          <Grid item xs={12} md={6}>
            <Card sx={{ p: 3, borderRadius: 2, border: '1px solid #e3ebf0' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, color: '#635bff' }}>
                Additional Information
              </Typography>
              
              <Box sx={{ '& > *': { mb: 2 } }}>
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Work Experience
                  </Typography>
                  <Typography variant="body1">
                    {application.work_experience || 'Not provided'}
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Research Interests
                  </Typography>
                  <Typography variant="body1">
                    {application.research_interests || 'Not provided'}
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Statement of Purpose
                  </Typography>
                  <Typography variant="body2" sx={{ 
                    backgroundColor: '#f6f9fc', 
                    p: 2, 
                    borderRadius: 1,
                    maxHeight: 100,
                    overflow: 'auto'
                  }}>
                    {application.statement_of_purpose || application.personal_statement || 'Not provided'}
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                    Application Submitted
                  </Typography>
                  <Typography variant="body1">
                    {application.submission_date || application.created_at || 'Not available'}
                  </Typography>
                </Box>
              </Box>
            </Card>
          </Grid>
          <Grid item xs={12}>
            <Card sx={{ p: 3, borderRadius: 2, border: '1px solid #e3ebf0' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, color: '#635bff' }}>
                Uploaded Documents ({Object.keys(application.documents || {}).length} files)
              </Typography>
              
              {Object.keys(application.documents || {}).length > 0 ? (
                <Grid container spacing={2}>
                  {Object.entries(application.documents || {}).map(([key, url]) => (
                    <Grid item xs={12} sm={6} md={4} key={key}>
                      <Card sx={{ 
                        p: 2, 
                        backgroundColor: '#f6f9fc',
                        border: '1px solid #e3ebf0',
                        '&:hover': { backgroundColor: '#e3ebf0' }
                      }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          <Box>
                            <Typography variant="body2" sx={{ fontWeight: 600, textTransform: 'capitalize' }}>
                              {key.replace(/_/g, ' ')}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              Document uploaded
                            </Typography>
                          </Box>
                          <Description sx={{ color: '#635bff' }} />
                        </Box>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No documents uploaded yet
                </Typography>
              )}
            </Card>
          </Grid>

          {/* Evaluation Details */}
          {evaluation && (
            <Grid item xs={12}>
              <Card sx={{ p: 3, borderRadius: 2, border: '1px solid #e3ebf0' }}>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, color: '#635bff' }}>
                  Evaluation Results
                </Typography>
                
                <Grid container spacing={2}>
                  {Object.entries(evaluation).map(([key, value]) => (
                    key !== 'application_id' && (
                      <Grid item xs={12} sm={6} md={4} key={key}>
                        <Box sx={{ p: 2, backgroundColor: '#f6f9fc', borderRadius: 1 }}>
                          <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 600 }}>
                            {key.replace(/_/g, ' ')}
                          </Typography>
                          <Typography variant="body1" sx={{ fontWeight: 500 }}>
                            {typeof value === 'object' ? JSON.stringify(value) : value || 'N/A'}
                          </Typography>
                        </Box>
                      </Grid>
                    )
                  ))}
                </Grid>
              </Card>
            </Grid>
          )}

          {/* Actions */}
          <Grid item xs={12}>
            <Card sx={{ p: 3, borderRadius: 2, border: '1px solid #e3ebf0' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, color: '#635bff' }}>
                Actions
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 2 }}>
                {application.report && (
                  <Button
                    variant="contained"
                    startIcon={loadingReport ? <CircularProgress size={16} sx={{ color: 'white' }} /> : <Description />}
                    onClick={handleViewReport}
                    disabled={loadingReport}
                    sx={{ 
                      backgroundColor: '#635bff',
                      '&:hover': { backgroundColor: '#4c44db' }
                    }}
                  >
                    {loadingReport ? 'Loading Report...' : 'View Full Report'}
                  </Button>
                )}
                
                <Button
                  variant="outlined"
                  onClick={onBack}
                  sx={{ 
                    borderColor: '#635bff',
                    color: '#635bff',
                    '&:hover': { borderColor: '#4c44db', backgroundColor: 'rgba(99,91,255,0.1)' }
                  }}
                >
                  Back to Dashboard
                </Button>
              </Box>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default ApplicationDetails;
