import React, { useState } from 'react';
import { 
  Card, CardContent, Typography, TextField, Button, Grid, Box, 
  FormControl, InputLabel, Select, MenuItem, Chip, Snackbar, Alert
} from '@mui/material';
import { CircularProgress } from '@mui/material';
import { extractDocumentData } from '../services/documentExtractor';
import { submitApplication } from '../services/applicationSubmission';

const ApplicationForm = ({ university, studentData, uploadedDocs = [], onSubmit, onBack }) => {
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [autofillLoading, setAutofillLoading] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [extractedDocuments, setExtractedDocuments] = useState([]);
  const [autofillData, setAutofillData] = useState(null);
  
  // Generate application ID
  const generateApplicationId = () => {
    const year = new Date().getFullYear();
    const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    return `APP-${year}-${random}`;
  };

  const [formData, setFormData] = useState({
    application_id: generateApplicationId(),
    submitted_date: new Date().toISOString(),
    university_name: university?.name || 'University',
    program: studentData?.field_of_study || '',
    full_name: studentData?.name || '',
    email: studentData?.email || '',
    // Personal Information
    full_name: studentData?.name || '',
    date_of_birth: '',
    gender: '',
    nationality: '',
    email: studentData?.email || '',
    phone: studentData?.phone || '',
    hometown: '',
    passport_number: '',
    family_background: '',
    
    // Academic Background
    institution: '',
    degree: '',
    graduation_date: '',
    gpa: studentData?.gpa || '',
    gpa_4_scale: '',
    trend: '',
    rank: '',
    strengths: '',
    weaknesses: '',
    
    // Test Scores
    gre_verbal: '',
    gre_quantitative: '',
    gre_awa: '',
    english_test: '',
    english_score: '',
    
    // Program Specific
    specialization: '',
    research_interest: '',
    career_goal: ''
  });

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const extractDataFromDocuments = async () => {
    // Skip validation - allow autofill even without student name
    setAutofillLoading(true);
    const studentName = studentData?.name || formData.full_name || 'Student';
    
    try {
      // Call Lambda using same Cognito Identity Pool as upload
      const result = await extractDocumentData(studentName);
      
      if (result.success) {
        const extractedData = result.data;
        
        // Map nested AgentCore response to flat form fields
        const mappedData = {};
        
        if (extractedData.personal_information) {
          mappedData.full_name = extractedData.personal_information.full_name;
          mappedData.email = extractedData.personal_information.email;
          mappedData.phone = extractedData.personal_information.phone;
          mappedData.date_of_birth = extractedData.personal_information.date_of_birth;
          mappedData.gender = extractedData.personal_information.gender;
          mappedData.nationality = extractedData.personal_information.nationality;
          mappedData.hometown = extractedData.personal_information.hometown;
          mappedData.passport_number = extractedData.personal_information.passport_number;
          mappedData.family_background = extractedData.personal_information.family_background;
        }
        
        if (extractedData.academic_background) {
          mappedData.institution = extractedData.academic_background.institution;
          mappedData.degree = extractedData.academic_background.degree;
          mappedData.gpa = extractedData.academic_background.gpa;
          mappedData.gpa_4_scale = extractedData.academic_background.gpa_4_scale;
          mappedData.graduation_date = extractedData.academic_background.graduation_date;
          mappedData.rank = extractedData.academic_background.rank;
          mappedData.trend = extractedData.academic_background.trend;
          mappedData.strengths = extractedData.academic_background.strengths?.join(', ');
          mappedData.weaknesses = extractedData.academic_background.weaknesses?.join(', ');
        }
        
        if (extractedData.test_scores) {
          mappedData.gre_verbal = extractedData.test_scores.gre_verbal;
          mappedData.gre_quantitative = extractedData.test_scores.gre_quantitative;
          mappedData.gre_awa = extractedData.test_scores.gre_awa;
          mappedData.english_test = extractedData.test_scores.english_test;
          mappedData.english_score = extractedData.test_scores.english_score;
        }
        
        if (extractedData.program_specific) {
          mappedData.specialization = extractedData.program_specific.specialization;
          mappedData.research_interest = extractedData.program_specific.research_interest;
          mappedData.career_goal = extractedData.program_specific.career_goal;
        }
        
        if (extractedData.research_experience) {
          mappedData.research_count = extractedData.research_experience.count;
          mappedData.publications = extractedData.research_experience.publications;
          mappedData.conferences = extractedData.research_experience.conferences;
          mappedData.lab_skills = extractedData.research_experience.lab_skills?.join(', ');
        }
        
        if (extractedData.work_experience && extractedData.work_experience.length > 0) {
          const work = extractedData.work_experience[0]; // Take first work experience
          mappedData.work_organization = work.organization;
          mappedData.work_role = work.role;
          mappedData.work_duration = work.duration;
          mappedData.work_responsibilities = work.responsibilities;
        }
        
        if (extractedData.extracurricular) {
          mappedData.extracurricular = extractedData.extracurricular.join(', ');
        }
        
        if (extractedData.profile_analysis) {
          mappedData.profile_strengths = extractedData.profile_analysis.strengths;
          mappedData.profile_challenges = extractedData.profile_analysis.challenges;
          mappedData.profile_type = extractedData.profile_analysis.profile_type;
        }
        
        // Extract documents
        if (extractedData.document || extractedData.documents) {
          const docs = extractedData.document || extractedData.documents;
          const documentList = Object.entries(docs).map(([key, value]) => ({
            id: key,
            name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
            path: value
          }));
          setExtractedDocuments(documentList);
        }
        
        // Store autofill response in submit payload format
        setAutofillData(extractedData);
        
        // Update form with mapped data, keeping existing values for empty fields
        setFormData(prev => {
          const updatedData = { ...prev };
          
          // Only update fields that have values from autofill, keep existing for empty ones
          Object.keys(mappedData).forEach(key => {
            if (mappedData[key] && mappedData[key] !== '' && mappedData[key] !== null) {
              updatedData[key] = mappedData[key];
            }
            // Keep existing value if autofill field is empty
          });
          
          // Ensure essential fields are populated
          updatedData.full_name = mappedData.full_name || prev.full_name || studentData.name;
          updatedData.email = mappedData.email || prev.email || studentData.email;
          
          return updatedData;
        });
        
        const fieldsCount = Object.keys(mappedData).filter(key => mappedData[key]).length;
        setNotification({ 
          open: true, 
          message: `✅ Successfully extracted ${fieldsCount} fields from documents!`, 
          severity: 'success' 
        });
      } else {
        throw new Error(result.error);
      }
      
    } catch (error) {
      console.log('Extraction failed:', error);
      setNotification({ 
        open: true, 
        message: `❌ Could not extract document data: ${error.message}`, 
        severity: 'error' 
      });
    } finally {
      setAutofillLoading(false);
    }
  };

  const parseTranscript = (text) => {
    const data = {};
    
    // Extract GPA
    const gpaMatch = text.match(/GPA[:\s]*(\d+\.?\d*)/i);
    if (gpaMatch) data.gpa = gpaMatch[1];
    
    // Extract degree
    const degreeMatch = text.match(/Bachelor of Science in (\w+)|B\.S\.?\s+(\w+)|Degree[:\s]*([^\n]+)/i);
    if (degreeMatch) data.degree = degreeMatch[1] || degreeMatch[2] || degreeMatch[3];
    
    // Extract institution
    const institutionMatch = text.match(/University of (\w+)|(\w+)\s+University|College of (\w+)/i);
    if (institutionMatch) data.institution = institutionMatch[0];
    
    return data;
  };

  const parseResume = (text) => {
    const data = {};
    
    // Extract phone
    const phoneMatch = text.match(/[\+]?[\d\s\-\(\)]{10,}/);
    if (phoneMatch) data.phone = phoneMatch[0];
    
    return data;
  };

  const handleSubmit = async () => {
    try {
      setSubmitLoading(true);
      
      // Merge autofill data with manual form entries
      const applicationData = autofillData ? {
        ...autofillData,
        // Update personal_information with manual entries
        personal_information: {
          ...autofillData.personal_information,
          full_name: formData.full_name || autofillData.personal_information?.full_name || '',
          email: formData.email || autofillData.personal_information?.email || '',
          date_of_birth: formData.date_of_birth || autofillData.personal_information?.date_of_birth || '',
          passport_number: formData.passport_number || autofillData.personal_information?.passport_number || ''
        }
      } : {
        // Fallback if no autofill data
        personal_information: {
          full_name: formData.full_name || '',
          email: formData.email || '',
          date_of_birth: formData.date_of_birth || '',
          passport_number: formData.passport_number || ''
        },
        academic_background: {},
        documents: {}
      };
      
      // Add application metadata
      applicationData.application_id = formData.application_id;
      applicationData.submitted_date = new Date().toISOString();

      console.log('📤 Submitting complete application data:', applicationData);
      console.log('📋 All form fields included:', Object.keys(formData));

      const result = await submitApplication(applicationData);
    
      if (result.success) {
        // Also update wishlist with application data
        const { updateWishlist } = await import('../services/student/studentService');
        await updateWishlist({
          application_id: applicationData.application_id,
          university_name: formData.university_name || applicationData.university_details?.name || 'University',
          location_preference: formData.location_preference || applicationData.university_details?.location || formData.hometown || 'Not specified',
          program: formData.program || applicationData.academic_background?.field_of_study || formData.field_of_study || formData.specialization || 'Not specified',
          status: 'Open',
          report: 'Application submitted successfully',
          applied_on: new Date().toISOString()
        });

        setNotification({
          open: true,
          message: `✅ Application ${applicationData.application_id} submitted successfully!`,
          severity: 'success'
        });
    } else {
      throw new Error(result.error);
    }
    
  } catch (error) {
    setNotification({
      open: true,
      message: `❌ Submission failed: ${error.message}`,
      severity: 'error'
    });
  } finally {
    setSubmitLoading(false);
  }
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="body2" color="text.secondary">
            Application ID: {formData.application_id}
          </Typography>
          <Typography variant="body2" color="primary.main" sx={{ mt: 0.5 }}>
            Applying to: {formData.university_name}
          </Typography>
        </Box>
        <Button 
          variant="contained" 
          onClick={extractDataFromDocuments}
          size="medium"
          color="success"
          disabled={autofillLoading}
          startIcon={autofillLoading ? <CircularProgress size={16} color="inherit" /> : null}
        >
          {autofillLoading ? 'Extracting...' : 'Auto-Fill from Documents'}
        </Button>
      </Box>
      
      {/* University Information */}
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom color="primary" sx={{ fontSize: '1.1rem' }}>
            University Information
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                size="small"
                label="University Name"
                value={formData.university_name}
                onChange={(e) => handleInputChange('university_name', e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                size="small"
                label="Program"
                value={formData.program}
                onChange={(e) => handleInputChange('program', e.target.value)}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>
      
      {/* Personal Information */}
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom color="primary" sx={{ fontSize: '1.1rem' }}>
            Personal Information
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Full Name"
                value={formData.full_name}
                onChange={(e) => handleInputChange('full_name', e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Email"
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Phone"
                value={formData.phone}
                onChange={(e) => handleInputChange('phone', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Date of Birth"
                type="date"
                value={formData.date_of_birth}
                onChange={(e) => handleInputChange('date_of_birth', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Gender</InputLabel>
                <Select
                  value={formData.gender}
                  onChange={(e) => handleInputChange('gender', e.target.value)}
                  label="Gender"
                >
                  {formData.gender && <MenuItem value={formData.gender}>{formData.gender}</MenuItem>}
                  <MenuItem value="">Select Gender</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Nationality"
                value={formData.nationality}
                onChange={(e) => handleInputChange('nationality', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Hometown"
                value={formData.hometown}
                onChange={(e) => handleInputChange('hometown', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Passport Number"
                value={formData.passport_number}
                onChange={(e) => handleInputChange('passport_number', e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                size="small"
                label="Family Background"
                multiline
                rows={2}
                value={formData.family_background}
                onChange={(e) => handleInputChange('family_background', e.target.value)}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Academic Background */}
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom color="primary" sx={{ fontSize: '1.1rem' }}>
            Academic Background
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={4}>
              <TextField
                fullWidth
                size="small"
                label="Institution"
                value={formData.institution}
                onChange={(e) => handleInputChange('institution', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <TextField
                fullWidth
                size="small"
                label="Degree"
                value={formData.degree}
                onChange={(e) => handleInputChange('degree', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <TextField
                fullWidth
                size="small"
                label="Graduation Date"
                type="date"
                value={formData.graduation_date}
                onChange={(e) => handleInputChange('graduation_date', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="GPA"
                value={formData.gpa}
                onChange={(e) => handleInputChange('gpa', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="GPA (4.0)"
                type="number"
                value={formData.gpa_4_scale}
                onChange={(e) => handleInputChange('gpa_4_scale', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Rank"
                value={formData.rank}
                onChange={(e) => handleInputChange('rank', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Trend"
                value={formData.trend}
                onChange={(e) => handleInputChange('trend', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={6}>
              <TextField
                fullWidth
                size="small"
                label="Academic Strengths"
                value={formData.strengths}
                onChange={(e) => handleInputChange('strengths', e.target.value)}
                
              />
            </Grid>
            <Grid item xs={12} sm={6} md={6}>
              <TextField
                fullWidth
                size="small"
                label="Areas for Improvement"
                value={formData.weaknesses}
                onChange={(e) => handleInputChange('weaknesses', e.target.value)}
                
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Test Scores */}
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom color="primary" sx={{ fontSize: '1.1rem' }}>
            Test Scores
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                size="small"
                label="GRE Verbal"
                type="number"
                value={formData.gre_verbal}
                onChange={(e) => handleInputChange('gre_verbal', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                size="small"
                label="GRE Quant"
                type="number"
                value={formData.gre_quantitative}
                onChange={(e) => handleInputChange('gre_quantitative', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                size="small"
                label="GRE AWA"
                type="number"
                step="0.5"
                value={formData.gre_awa}
                onChange={(e) => handleInputChange('gre_awa', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>English Test</InputLabel>
                <Select
                  value={formData.english_test}
                  onChange={(e) => handleInputChange('english_test', e.target.value)}
                  label="English Test"
                >
                  {formData.english_test && <MenuItem value={formData.english_test}>{formData.english_test}</MenuItem>}
                  <MenuItem value="">Select Test</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="English Score"
                type="number"
                value={formData.english_score}
                onChange={(e) => handleInputChange('english_score', e.target.value)}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Program & Goals */}
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom color="primary" sx={{ fontSize: '1.1rem' }}>
            Program & Goals
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                size="small"
                label="Specialization"
                value={formData.specialization}
                onChange={(e) => handleInputChange('specialization', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                size="small"
                label="Research Interest"
                value={formData.research_interest}
                onChange={(e) => handleInputChange('research_interest', e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                size="small"
                label="Career Goal"
                multiline
                rows={2}
                value={formData.career_goal}
                onChange={(e) => handleInputChange('career_goal', e.target.value)}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Research Experience */}
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom color="primary" sx={{ fontSize: '1.1rem' }}>
            Research Experience
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Research Count"
                value={formData.research_count || ''}
                onChange={(e) => handleInputChange('research_count', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Publications"
                value={formData.publications || ''}
                onChange={(e) => handleInputChange('publications', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Conferences"
                value={formData.conferences || ''}
                onChange={(e) => handleInputChange('conferences', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Lab Skills"
                value={formData.lab_skills || ''}
                onChange={(e) => handleInputChange('lab_skills', e.target.value)}
                
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Work Experience */}
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom color="primary" sx={{ fontSize: '1.1rem' }}>
            Work Experience
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Organization"
                value={formData.work_organization || ''}
                onChange={(e) => handleInputChange('work_organization', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Role"
                value={formData.work_role || ''}
                onChange={(e) => handleInputChange('work_role', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Duration"
                value={formData.work_duration || ''}
                onChange={(e) => handleInputChange('work_duration', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Responsibilities"
                value={formData.work_responsibilities || ''}
                onChange={(e) => handleInputChange('work_responsibilities', e.target.value)}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Extracurricular Activities */}
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom color="primary" sx={{ fontSize: '1.1rem' }}>
            Extracurricular Activities
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                size="small"
                label="Activities"
                value={formData.extracurricular || ''}
                onChange={(e) => handleInputChange('extracurricular', e.target.value)}
                
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Profile Analysis */}
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom color="primary" sx={{ fontSize: '1.1rem' }}>
            Profile Analysis
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                size="small"
                label="Strengths"
                value={formData.profile_strengths || ''}
                onChange={(e) => handleInputChange('profile_strengths', e.target.value)}
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                size="small"
                label="Challenges"
                value={formData.profile_challenges || ''}
                onChange={(e) => handleInputChange('profile_challenges', e.target.value)}
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                size="small"
                label="Profile Type"
                value={formData.profile_type || ''}
                onChange={(e) => handleInputChange('profile_type', e.target.value)}
                multiline
                rows={2}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Documents */}
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom color="primary" sx={{ fontSize: '1.1rem' }}>
            Documents
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {(extractedDocuments.length > 0 || (uploadedDocs && uploadedDocs.length > 0)) ? (
              <>
                {extractedDocuments.map((doc) => (
                  <Chip key={doc.id} label={doc.name} color="primary" size="small" />
                ))}
                {uploadedDocs && uploadedDocs.map((doc) => (
                  <Chip key={doc.id} label={doc.name} color="success" size="small" />
                ))}
              </>
            ) : (
              <Typography variant="body2" color="text.secondary">No documents uploaded</Typography>
            )}
          </Box>
        </CardContent>
      </Card>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
        <Button onClick={onBack} size="medium">
          Back
        </Button>
        <Button 
          variant="contained" 
          onClick={handleSubmit}
          size="medium"
          disabled={!formData.full_name || !formData.email || submitLoading}
          startIcon={submitLoading ? <CircularProgress size={16} color="inherit" /> : null}
        >
          {submitLoading ? 'Submitting...' : 'Submit Application'}
        </Button>
      </Box>

      {/* Notification Snackbar */}
      <Snackbar 
        open={notification.open} 
        autoHideDuration={4000} 
        onClose={() => setNotification({ ...notification, open: false })}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert 
          onClose={() => setNotification({ ...notification, open: false })} 
          severity={notification.severity}
          variant="filled"
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ApplicationForm;
