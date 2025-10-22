import React, { useState, useEffect } from 'react';
import {
  Grid, Card, Typography, Box, Chip, Button,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  IconButton, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, InputAdornment, CircularProgress
} from '@mui/material';
import { 
  Visibility, CheckCircle, Cancel, Search, TrendingUp, People, School, Assignment, Settings, Description, Refresh
} from '@mui/icons-material';
import { listApplications, processApplication } from '../services/admin/adminService';
import { getReportPresignedUrl } from '../services/admin/reportService';
import ApplicationDetailsView from './ApplicationDetailsView';

const AdminDashboard = () => {
  const [applications, setApplications] = useState([]);
  const [filteredApps, setFilteredApps] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedApp, setSelectedApp] = useState(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(6);
  const [loading, setLoading] = useState(true);
  const [loadingReport, setLoadingReport] = useState(null);
  const [processingApp, setProcessingApp] = useState(null);
  const [selectedApplicationId, setSelectedApplicationId] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const mockApplications = [];

  // Dedicated sorting function to ensure consistency
  const sortApplications = (apps) => {
    return [...apps].sort((a, b) => {
      // Priority 1: New status always first
      if (a.application_status === 'New' && b.application_status !== 'New') return -1;
      if (a.application_status !== 'New' && b.application_status === 'New') return 1;
      
      // Priority 2: Processing started applications second (right after New)
      const aIsProcessing = a.application_status === 'Processing started' || a.application_status?.includes('processing');
      const bIsProcessing = b.application_status === 'Processing started' || b.application_status?.includes('processing');
      
      if (aIsProcessing && !bIsProcessing && b.application_status !== 'New') return -1;
      if (!aIsProcessing && bIsProcessing && a.application_status !== 'New') return 1;
      
      // Priority 3: Within same status, sort by date (newest first)
      const dateA = new Date(a.submitted_date || a.applied_on || 0);
      const dateB = new Date(b.submitted_date || b.applied_on || 0);
      return dateB - dateA;
    });
  };

  useEffect(() => {
    fetchApplications();
    
    // Auto-refresh every 30 seconds using silent refresh
    const interval = setInterval(() => {
      refreshApplicationsSilently();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const sortedApps = sortApplications(applications);
    
    if (searchTerm.trim() === '') {
      setFilteredApps(sortedApps);
    } else {
      const filtered = sortedApps.filter(app =>
        app.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        app.application_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        app.specialization?.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredApps(filtered);
    }
  }, [searchTerm, applications]);

  const fetchApplications = async () => {
    try {
      setLoading(true);
      const result = await listApplications();
      
      if (result.success) {
        const sortedApps = sortApplications(result.applications);
        setApplications(sortedApps);
        setFilteredApps(sortedApps);
      } else {
        const sortedMock = sortApplications(mockApplications);
        setApplications(sortedMock);
        setFilteredApps(sortedMock);
      }
    } catch (error) {
      const sortedMock = sortApplications(mockApplications);
      setApplications(sortedMock);
      setFilteredApps(sortedMock);
    } finally {
      setLoading(false);
    }
  };

  const refreshApplicationsSilently = async () => {
    try {
      setRefreshing(true);
      const result = await listApplications();
      
      if (result.success) {
        const sortedApps = sortApplications(result.applications);
        setApplications(sortedApps);
        setFilteredApps(sortedApps);
      }
    } catch (error) {
      console.error('Silent refresh failed:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      const result = await listApplications();
      
      if (result.success) {
        setApplications(result.applications);
        setFilteredApps(result.applications);
      }
    } catch (error) {
      console.error('Error refreshing applications:', error);
    } finally {
      setRefreshing(false);
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

  const handleProcessApplication = async (applicationId) => {
    try {
      setProcessingApp(applicationId);
      console.log(`🔄 Processing application: ${applicationId}`);
      
      const result = await processApplication(applicationId);
      console.log(`📥 Process result:`, result);
      
      if (result.success) {
        // Update the application status and re-sort immediately
        setApplications(prevApps => {
          const updatedApps = prevApps.map(app => 
            app.application_id === applicationId 
              ? { ...app, application_status: 'Processing started', final_decision: null }
              : app
          );
          return sortApplications(updatedApps);
        });
        
        console.log(`✅ Application ${applicationId} processing started`);
      } else {
        console.error('❌ Failed to process application:', result.error);
        alert(`Failed to process application: ${result.error}`);
      }
    } catch (error) {
      console.error('❌ Error processing application:', error);
      alert(`Error processing application: ${error.message}`);
    } finally {
      setProcessingApp(null);
    }
  };

  const handleViewReport = async (reportUrl, applicationId) => {
    if (reportUrl && reportUrl.startsWith('s3://')) {
      try {
        setLoadingReport(applicationId);
        const result = await getReportPresignedUrl(reportUrl);
        if (result.success) {
          window.open(result.url, '_blank');
        } else {
          console.error('Failed to get presigned URL:', result.error);
          alert('Unable to load report. Please try again.');
        }
      } catch (error) {
        console.error('Error getting presigned URL:', error);
        alert('Error loading report. Please try again.');
      } finally {
        setLoadingReport(null);
      }
    } else if (reportUrl) {
      window.open(reportUrl, '_blank');
    }
  };

  const stats = {
    total: applications.length,
    new: applications.filter(app => app.application_status === 'New').length,
    processing: applications.filter(app => app.application_status?.includes('Processing')).length,
    accepted: applications.filter(app => app.final_decision === 'ACCEPT').length
  };

  // Show application details if selected
  if (selectedApplicationId) {
    const selectedApp = applications.find(app => app.application_id === selectedApplicationId);
    return (
      <ApplicationDetailsView 
        applicationId={selectedApplicationId}
        applicationData={selectedApp}
        onBack={() => setSelectedApplicationId(null)}
      />
    );
  }

  return (
    <Box sx={{ p: 1.5 }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
        <School sx={{ mr: 1, fontSize: 20 }} />
        Admin Dashboard
      </Typography>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {/* Stats Cards */}
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ 
                p: 1.5, 
                borderRadius: 1.5,
                border: '1px solid #e3ebf0',
                boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
                '&:hover': { boxShadow: '0 2px 8px rgba(0,0,0,0.12)' }
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h5" sx={{ fontWeight: 700, color: '#635bff', mb: 0.3 }}>
                      {stats.total}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Total Applications
                    </Typography>
                  </Box>
                  <Assignment sx={{ fontSize: 28, color: '#635bff', opacity: 0.7 }} />
                </Box>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ 
                p: 1.5, 
                borderRadius: 1.5,
                border: '1px solid #e3ebf0',
                boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
                '&:hover': { boxShadow: '0 2px 8px rgba(0,0,0,0.12)' }
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h5" sx={{ fontWeight: 700, color: '#00d924', mb: 0.3 }}>
                      {stats.new}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      New Applications
                    </Typography>
                  </Box>
                  <TrendingUp sx={{ fontSize: 28, color: '#00d924', opacity: 0.7 }} />
                </Box>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ 
                p: 1.5, 
                borderRadius: 1.5,
                border: '1px solid #e3ebf0',
                boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
                '&:hover': { boxShadow: '0 2px 8px rgba(0,0,0,0.12)' }
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h5" sx={{ fontWeight: 700, color: '#635bff', mb: 0.3 }}>
                      {stats.accepted}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Accepted
                    </Typography>
                  </Box>
                  <CheckCircle sx={{ fontSize: 28, color: '#635bff', opacity: 0.7 }} />
                </Box>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ 
                p: 1.5, 
                borderRadius: 1.5,
                border: '1px solid #e3ebf0',
                boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
                '&:hover': { boxShadow: '0 2px 8px rgba(0,0,0,0.12)' }
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h5" sx={{ fontWeight: 700, color: '#425466', mb: 0.3 }}>
                      {stats.processing}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Processing
                    </Typography>
                  </Box>
                  <People sx={{ fontSize: 28, color: '#425466', opacity: 0.7 }} />
                </Box>
              </Card>
            </Grid>
          </Grid>

          {/* Applications Table */}
          <Card sx={{ borderRadius: 1.5, border: '1px solid #e3ebf0', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
            <Box sx={{ p: 2, borderBottom: '1px solid #e3ebf0' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#0a2540' }}>
                  Applications Management
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                  <TextField
                    size="small"
                    placeholder="Search applications..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    InputProps={{
                      startAdornment: <InputAdornment position="start"><Search sx={{ color: 'text.secondary', fontSize: 18 }} /></InputAdornment>,
                    }}
                    sx={{ 
                      width: 250,
                      '& .MuiOutlinedInput-root': {
                        borderRadius: 1.5,
                        backgroundColor: '#f6f9fc',
                        height: 36
                      }
                    }}
                  />
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={handleRefresh}
                    disabled={refreshing}
                    startIcon={refreshing ? <CircularProgress size={14} /> : <Refresh />}
                    sx={{
                      borderColor: '#635bff',
                      color: '#635bff',
                      fontSize: '0.75rem',
                      px: 1.5,
                      py: 0.5,
                      minWidth: 'auto',
                      height: 36,
                      '&:hover': { backgroundColor: 'rgba(99,91,255,0.1)' }
                    }}
                  >
                    {refreshing ? 'Refreshing...' : 'Refresh'}
                  </Button>
                </Box>
              </Box>
            </Box>
            
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow sx={{ backgroundColor: '#fafbfc' }}>
                    <TableCell sx={{ fontWeight: 600, color: '#425466', py: 1.5, fontSize: '0.875rem' }}>Application ID</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: '#425466', py: 1.5, fontSize: '0.875rem' }}>Student</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: '#425466', py: 1.5, fontSize: '0.875rem' }}>Specialization</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: '#425466', py: 1.5, fontSize: '0.875rem', textAlign: 'center' }}>Score</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: '#425466', py: 1.5, fontSize: '0.875rem', textAlign: 'center' }}>Status</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: '#425466', py: 1.5, fontSize: '0.875rem', textAlign: 'center' }}>Decision</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: '#425466', py: 1.5, fontSize: '0.875rem', textAlign: 'center' }}>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredApps
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    .map((app) => (
                    <TableRow 
                      key={app.application_id} 
                      sx={{ 
                        '&:hover': { backgroundColor: '#f6f9fc' },
                        borderBottom: '1px solid #e3ebf0'
                      }}
                    >
                      <TableCell sx={{ py: 1.5 }}>
                        <Button
                          variant="text"
                          onClick={() => setSelectedApplicationId(app.application_id)}
                          sx={{ 
                            fontWeight: 600, 
                            color: '#635bff', 
                            fontSize: '0.8rem',
                            textTransform: 'none',
                            '&:hover': { backgroundColor: 'rgba(99,91,255,0.1)' }
                          }}
                        >
                          {app.application_id}
                        </Button>
                      </TableCell>
                      <TableCell sx={{ py: 1.5 }}>
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 600, color: '#0a2540', mb: 0.2, fontSize: '0.85rem' }}>
                            {app.full_name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                            {app.email}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell sx={{ py: 1.5 }}>
                        <Typography variant="body2" color="text.primary" sx={{ fontSize: '0.85rem' }}>
                          {app.specialization}
                        </Typography>
                      </TableCell>
                      <TableCell sx={{ py: 1.5, textAlign: 'center' }}>
                        <Typography variant="body2" sx={{ fontWeight: 600, color: '#635bff', fontSize: '0.85rem' }}>
                          {app.composite_score || 'N/A'}
                        </Typography>
                      </TableCell>
                      <TableCell sx={{ py: 1.5, textAlign: 'center' }}>
                        <Chip 
                          label={app.application_status} 
                          color={getStatusColor(app.application_status)}
                          size="small"
                          sx={{ borderRadius: 1, fontWeight: 500, fontSize: '0.7rem', height: 20 }}
                        />
                      </TableCell>
                      <TableCell sx={{ py: 1.5, textAlign: 'center' }}>
                        <Chip 
                          label={app.final_decision || 'Pending'} 
                          color={getStatusColor(app.final_decision)}
                          size="small"
                          sx={{ borderRadius: 1, fontWeight: 500, fontSize: '0.7rem', height: 20 }}
                        />
                      </TableCell>
                      <TableCell sx={{ py: 1.5, textAlign: 'center' }}>
                        <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center', alignItems: 'center' }}>
                          {/* Process Button - Only for New applications */}
                          {app.application_status === 'New' && (
                            <Button
                              size="small"
                              variant="contained"
                              disabled={processingApp === app.application_id}
                              onClick={() => handleProcessApplication(app.application_id)}
                              startIcon={processingApp === app.application_id ? 
                                <CircularProgress size={14} sx={{ color: 'white' }} /> : 
                                <Settings sx={{ fontSize: 14 }} />
                              }
                              sx={{ 
                                backgroundColor: '#00d924',
                                color: 'white',
                                fontSize: '0.7rem',
                                px: 1.5,
                                py: 0.5,
                                minWidth: 'auto',
                                borderRadius: 1,
                                textTransform: 'none',
                                fontWeight: 600,
                                '&:hover': { backgroundColor: '#00b01f' },
                                '&:disabled': { backgroundColor: '#cccccc' }
                              }}
                            >
                              {processingApp === app.application_id ? 'Starting...' : 'Process'}
                            </Button>
                          )}
                          
                          {/* Processing Status Indicator */}
                          {app.application_status?.includes('processing') && (
                            <Box sx={{ 
                              display: 'flex', 
                              alignItems: 'center', 
                              gap: 0.5,
                              px: 1.5,
                              py: 0.5,
                              backgroundColor: '#fff3cd',
                              borderRadius: 1,
                              border: '1px solid #ffeaa7'
                            }}>
                              <CircularProgress size={14} sx={{ color: '#f39c12' }} />
                              <Typography variant="caption" sx={{ fontSize: '0.7rem', color: '#f39c12', fontWeight: 600 }}>
                                Processing...
                              </Typography>
                            </Box>
                          )}
                          
                          {/* View Report Button - Only when report exists */}
                          {app.report && (
                            <Button
                              size="small"
                              variant="contained"
                              disabled={loadingReport === app.application_id}
                              onClick={() => handleViewReport(app.report, app.application_id)}
                              startIcon={loadingReport === app.application_id ? 
                                <CircularProgress size={14} sx={{ color: 'white' }} /> : 
                                <Description sx={{ fontSize: 14 }} />
                              }
                              sx={{ 
                                backgroundColor: '#635bff',
                                color: 'white',
                                fontSize: '0.7rem',
                                px: 1.5,
                                py: 0.5,
                                minWidth: 'auto',
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
                          
                          {/* No Actions Available */}
                          {app.application_status !== 'New' && !app.application_status?.includes('processing') && !app.report && (
                            <Typography variant="caption" sx={{ 
                              color: 'text.secondary', 
                              fontSize: '0.7rem',
                              fontStyle: 'italic',
                              px: 1.5,
                              py: 0.5
                            }}>
                              No actions available
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            
            {/* Google-style Pagination */}
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', p: 2, borderTop: '1px solid #e3ebf0' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Button
                  size="small"
                  disabled={page === 0}
                  onClick={() => setPage(page - 1)}
                  sx={{ 
                    minWidth: 36, 
                    height: 36,
                    color: '#635bff',
                    '&:hover': { backgroundColor: '#f6f9fc' }
                  }}
                >
                  ‹
                </Button>
                
                {Array.from({ length: Math.ceil(filteredApps.length / rowsPerPage) }, (_, index) => (
                  <Button
                    key={index}
                    size="small"
                    onClick={() => setPage(index)}
                    sx={{
                      minWidth: 36,
                      height: 36,
                      backgroundColor: page === index ? '#635bff' : 'transparent',
                      color: page === index ? 'white' : '#635bff',
                      '&:hover': {
                        backgroundColor: page === index ? '#4c44db' : '#f6f9fc'
                      }
                    }}
                  >
                    {index + 1}
                  </Button>
                ))}
                
                <Button
                  size="small"
                  disabled={page >= Math.ceil(filteredApps.length / rowsPerPage) - 1}
                  onClick={() => setPage(page + 1)}
                  sx={{ 
                    minWidth: 36, 
                    height: 36,
                    color: '#635bff',
                    '&:hover': { backgroundColor: '#f6f9fc' }
                  }}
                >
                  ›
                </Button>
              </Box>
            </Box>
          </Card>
        </>
      )}
    </Box>
  );
};

export default AdminDashboard;
