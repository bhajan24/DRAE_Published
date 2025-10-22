import React, { useState, useEffect } from 'react';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { Container, Stepper, Step, StepLabel, Box, Fade } from '@mui/material';
import { lightTheme, darkTheme } from './theme';
import Header from './components/Header';
import Login from './components/Login';
import StudentInput from './components/StudentInput';
import UniversitySearch from './components/UniversitySearch';
import UniversityDetails from './components/UniversityDetails';
import DocumentUpload from './components/DocumentUpload';
import ApplicationForm from './components/ApplicationForm';
import AdminDashboard from './components/AdminDashboard';
import './App.css';

const steps = ['Discover', 'Recommend', 'Details', 'Apply', 'Enroll'];

function App() {
  const [user, setUser] = useState(null);
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });
  const [activeStep, setActiveStep] = useState(0);
  const [studentData, setStudentData] = useState({});
  const [selectedUniversity, setSelectedUniversity] = useState(null);
  const [uploadedDocs, setUploadedDocs] = useState([]);
  const [universitiesCache, setUniversitiesCache] = useState([]);
  const [searchMetadataCache, setSearchMetadataCache] = useState(null);

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
    setActiveStep(0);
    setStudentData({});
    setSelectedUniversity(null);
    setUploadedDocs([]);
    setUniversitiesCache([]);
    setSearchMetadataCache(null);
  };

  const handleToggleTheme = () => {
    setDarkMode(!darkMode);
  };

  const handleNext = () => setActiveStep(prev => prev + 1);
  const handleBack = () => setActiveStep(prev => prev - 1);

  const handleUniversitySelect = (university, universities, searchMetadata) => {
    setSelectedUniversity(university);
    if (universities) setUniversitiesCache(universities);
    if (searchMetadata) setSearchMetadataCache(searchMetadata);
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <StudentInput 
            data={studentData} 
            setData={setStudentData} 
            onNext={handleNext} 
          />
        );
      case 1:
        return (
          <UniversitySearch 
            studentData={studentData} 
            onSelect={handleUniversitySelect} 
            onNext={handleNext}
            onBack={handleBack}
            universities={universitiesCache}
            searchMetadata={searchMetadataCache}
          />
        );
      case 2:
        return (
          <UniversityDetails 
            university={selectedUniversity}
            studentData={studentData}
            onNext={handleNext}
            onBack={handleBack}
          />
        );
      case 3:
        return (
          <DocumentUpload 
            docs={uploadedDocs} 
            setDocs={setUploadedDocs} 
            onNext={handleNext} 
            onBack={handleBack}
            studentData={studentData}
          />
        );
      case 4:
        return (
          <ApplicationForm 
            university={selectedUniversity} 
            studentData={studentData} 
            docs={uploadedDocs} 
            onBack={handleBack} 
          />
        );
      default:
        return null;
    }
  };

  if (!user) {
    return (
      <ThemeProvider theme={darkMode ? darkTheme : lightTheme}>
        <CssBaseline />
        <Login onLogin={handleLogin} darkMode={darkMode} />
      </ThemeProvider>
    );
  }

  // Admin Dashboard
  if (user.role === 'admin') {
    return (
      <ThemeProvider theme={darkMode ? darkTheme : lightTheme}>
        <CssBaseline />
        <div className="App">
          <Header 
            user={user}
            darkMode={darkMode}
            onToggleTheme={handleToggleTheme}
            onLogout={handleLogout}
          />
          <Container maxWidth="xl" className="main-container" sx={{ flex: 1, py: 2 }}>
            <AdminDashboard />
          </Container>
        </div>
      </ThemeProvider>
    );
  }

  // Student Workflow
  return (
    <ThemeProvider theme={darkMode ? darkTheme : lightTheme}>
      <CssBaseline />
      <div className="App">
        <Header 
          user={user}
          darkMode={darkMode}
          onToggleTheme={handleToggleTheme}
          onLogout={handleLogout}
        />

        <Container maxWidth="xl" className="main-container" sx={{ flex: 1, py: 0.5 }}>
            <Stepper 
              activeStep={activeStep} 
              sx={{ 
                mb: 1,
                '& .MuiStepLabel-label': {
                  fontSize: '0.75rem',
                  fontWeight: 500,
                },
                '& .MuiStepIcon-root': {
                  fontSize: '1.1rem',
                }
              }}
            >
              {steps.map((label, index) => (
                <Step key={label}>
                  <StepLabel>
                    {label}
                  </StepLabel>
                </Step>
              ))}
            </Stepper>

          <Box sx={{ mt: 0.5 }}>
            {renderStepContent(activeStep)}
          </Box>
        </Container>
      </div>
    </ThemeProvider>
  );
}

export default App;
