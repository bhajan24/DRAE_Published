import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Card, Grid, Chip, Button, CircularProgress,
  Collapse, IconButton, Drawer
} from '@mui/material';
import { 
  ArrowBack, Person, School, Description, Email, Phone, 
  ExpandMore, ExpandLess, Visibility, Close
} from '@mui/icons-material';
import { getApplication, getEvaluation } from '../services/admin/adminService';
import { getReportPresignedUrl } from '../services/admin/reportService';

const ApplicationDetailsView = ({ applicationId, applicationData, onBack }) => {
  const [application, setApplication] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingReport, setLoadingReport] = useState(false);
  const [loadingDoc, setLoadingDoc] = useState(null);
  const [expandedSections, setExpandedSections] = useState({
    personal: true,
    academic: true,
    documents: true,
    research: false,
    work: false
  });
  const [documentDrawer, setDocumentDrawer] = useState({ open: false, url: '', title: '' });

  useEffect(() => {
    fetchApplicationDetails();
  }, [applicationId]);

  const fetchApplicationDetails = async () => {
    try {
      setLoading(true);
      
      // Debug: Log all available fields
      console.log('Application ID:', applicationId);
      console.log('Application Data:', applicationData);
      console.log('Available fields:', Object.keys(applicationData || {}));
      console.log('Documents:', applicationData?.documents);
      
      if (applicationData) {
        setApplication(applicationData);
      }
      
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const handleViewDocument = async (docUrl, docTitle) => {
    try {
      setLoadingDoc(docTitle);
      const result = await getReportPresignedUrl(docUrl);
      if (result.success) {
        setDocumentDrawer({
          open: true,
          url: result.url,
          title: docTitle.replace(/_/g, ' ').toUpperCase()
        });
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoadingDoc(null);
    }
  };

  const handleViewReport = async () => {
    try {
      setLoadingReport(true);
      const result = await getReportPresignedUrl(application.report);
      if (result.success) {
        window.open(result.url, '_blank');
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoadingReport(false);
    }
  };

  const SectionHeader = ({ title, section, icon }) => (
    <Box 
      sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        cursor: 'pointer',
        p: 2,
        borderBottom: '1px solid #e3ebf0',
        '&:hover': { backgroundColor: '#f8f9fa' }
      }}
      onClick={() => toggleSection(section)}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {icon}
        <Typography variant="h6" sx={{ fontWeight: 600, color: '#635bff' }}>
          {title}
        </Typography>
      </Box>
      <IconButton size="small">
        {expandedSections[section] ? <ExpandLess /> : <ExpandMore />}
      </IconButton>
    </Box>
  );

  const InfoRow = ({ label, value }) => (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', py: 1, borderBottom: '1px solid #f0f0f0' }}>
      <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 600 }}>
        {label}
      </Typography>
      <Typography variant="body2" sx={{ fontWeight: 500, maxWidth: '60%', textAlign: 'right' }}>
        {value || 'Not provided'}
      </Typography>
    </Box>
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2, maxWidth: 1200, mx: 'auto' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, pb: 2, borderBottom: '2px solid #635bff' }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={onBack}
          sx={{ mr: 2, color: '#635bff', fontWeight: 600 }}
        >
          Back
        </Button>
        <Typography variant="h6" sx={{ fontWeight: 600, color: '#635bff', mr: 2 }}>
          Application Details
        </Typography>
        <Typography variant="body1" sx={{ fontWeight: 500, color: 'text.secondary', mr: 'auto' }}>
          {applicationId}
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Chip label={application?.application_status} color="primary" size="small" />
          <Chip label={application?.final_decision || 'Pending'} color="success" size="small" />
        </Box>
      </Box>

      <Grid container spacing={2}>
        {/* Personal Information */}
        <Grid item xs={12} md={6}>
          <Card sx={{ borderRadius: 2, overflow: 'hidden' }}>
            <SectionHeader 
              title="Personal Information" 
              section="personal" 
              icon={<Person sx={{ color: '#635bff' }} />} 
            />
            <Collapse in={expandedSections.personal}>
              <Box sx={{ p: 2 }}>
                {application?.full_name && <InfoRow label="Full Name" value={application.full_name} />}
                {application?.email && <InfoRow label="Email" value={application.email} />}
                {application?.phone && <InfoRow label="Phone" value={application.phone} />}
                {application?.specialization && <InfoRow label="Specialization" value={application.specialization} />}
                {application?.application_status && <InfoRow label="Status" value={application.application_status} />}
                {application?.final_decision && <InfoRow label="Decision" value={application.final_decision} />}
              </Box>
            </Collapse>
          </Card>
        </Grid>

        {/* Academic Information */}
        <Grid item xs={12} md={6}>
          <Card sx={{ borderRadius: 2, overflow: 'hidden' }}>
            <SectionHeader 
              title="Academic Background" 
              section="academic" 
              icon={<School sx={{ color: '#00d924' }} />} 
            />
            <Collapse in={expandedSections.academic}>
              <Box sx={{ p: 2 }}>
                {application?.composite_score && <InfoRow label="Composite Score" value={application.composite_score} />}
                {application?.confidence_level && <InfoRow label="Confidence Level" value={application.confidence_level} />}
                {application?.submitted_date && <InfoRow label="Submitted Date" value={application.submitted_date} />}
                {application?.last_updated && <InfoRow label="Last Updated" value={application.last_updated} />}
              </Box>
            </Collapse>
          </Card>
        </Grid>

        {/* Documents - Only show if documents exist */}
        {application?.documents && Object.keys(application.documents).length > 0 && (
          <Grid item xs={12}>
            <Card sx={{ borderRadius: 2, overflow: 'hidden' }}>
              <SectionHeader 
                title={`Documents (${Object.keys(application.documents).length})`}
                section="documents" 
                icon={<Description sx={{ color: '#f39c12' }} />} 
              />
              <Collapse in={expandedSections.documents}>
                <Box sx={{ p: 2 }}>
                  <Grid container spacing={1}>
                    {Object.entries(application.documents).map(([key, url]) => (
                      <Grid item xs={12} sm={6} md={4} key={key}>
                        <Box sx={{ 
                          p: 1.5, 
                          border: '1px solid #e3ebf0', 
                          borderRadius: 1,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          '&:hover': { backgroundColor: '#f8f9fa', borderColor: '#635bff' }
                        }}>
                          <Box>
                            <Typography variant="body2" sx={{ fontWeight: 600, textTransform: 'capitalize', fontSize: '0.85rem' }}>
                              {key.replace(/_/g, ' ')}
                            </Typography>
                            <Chip label="✓ Uploaded" color="success" size="small" sx={{ mt: 0.5, fontSize: '0.7rem', height: 20 }} />
                          </Box>
                          <Button
                            size="small"
                            variant="text"
                            disabled={loadingDoc === key}
                            onClick={() => handleViewDocument(url, key)}
                            startIcon={loadingDoc === key ? 
                              <CircularProgress size={14} sx={{ color: '#635bff' }} /> : 
                              <Visibility sx={{ fontSize: 16 }} />
                            }
                            sx={{ 
                              minWidth: 'auto',
                              px: 1.5,
                              py: 0.5,
                              color: '#635bff',
                              fontSize: '0.75rem',
                              fontWeight: 600,
                              '&:hover': { backgroundColor: 'rgba(99,91,255,0.1)' }
                            }}
                          >
                            {loadingDoc === key ? 'Loading' : 'View'}
                          </Button>
                        </Box>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              </Collapse>
            </Card>
          </Grid>
        )}

        {/* Actions */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', py: 3 }}>
            {application?.report && (
              <Button
                variant="contained"
                size="large"
                startIcon={loadingReport ? <CircularProgress size={18} sx={{ color: 'white' }} /> : <Description />}
                onClick={handleViewReport}
                disabled={loadingReport}
                sx={{ 
                  backgroundColor: '#635bff',
                  px: 3,
                  py: 1.2,
                  fontSize: '0.9rem',
                  fontWeight: 600,
                  borderRadius: 2,
                  textTransform: 'none',
                  '&:hover': { backgroundColor: '#4c44db' }
                }}
              >
                {loadingReport ? 'Loading Report...' : 'View Evaluation Report'}
              </Button>
            )}
          </Box>
        </Grid>
      </Grid>

      {/* Document Preview Drawer */}
      <Drawer
        anchor="right"
        open={documentDrawer.open}
        onClose={() => setDocumentDrawer({ open: false, url: '', title: '' })}
        PaperProps={{
          sx: {
            width: { xs: '100%', sm: '60%', md: '50%' },
            maxWidth: 800
          }
        }}
      >
        <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          {/* Header */}
          <Box sx={{ 
            p: 2, 
            backgroundColor: '#635bff', 
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              {documentDrawer.title}
            </Typography>
            <IconButton 
              onClick={() => setDocumentDrawer({ open: false, url: '', title: '' })}
              sx={{ color: 'white' }}
            >
              <Close />
            </IconButton>
          </Box>
          
          {/* Document Content */}
          <Box sx={{ flex: 1, overflow: 'hidden' }}>
            {documentDrawer.url && (
              <iframe
                src={`https://docs.google.com/gview?url=${encodeURIComponent(documentDrawer.url)}&embedded=true`}
                width="100%"
                height="100%"
                style={{ border: 'none' }}
                title={documentDrawer.title}
              />
            )}
          </Box>
        </Box>
      </Drawer>
    </Box>
  );
};

export default ApplicationDetailsView;
