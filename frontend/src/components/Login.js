import React, { useState } from 'react';
import {
  Box, Card, CardContent, TextField, Button, Typography, 
  ToggleButton, ToggleButtonGroup, InputAdornment, IconButton, Alert
} from '@mui/material';
import {
  School, AdminPanelSettings, Email, Lock, 
  Visibility, VisibilityOff, ArrowForward
} from '@mui/icons-material';

const Login = ({ onLogin, darkMode }) => {
  const [role, setRole] = useState('student');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');

  const handleRoleChange = (e, newRole) => {
    if (newRole) {
      setRole(newRole);
      // Auto-fill credentials based on role
      if (newRole === 'student') {
        setEmail('');
        setPassword('');
      } else {
        setEmail('admin@university.edu');
        setPassword('demo123');
      }
    }
  };

  const handleLogin = () => {
    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }
    
    // Allow any student to login, validate admin credentials
    if (role === 'student') {
      onLogin({
        role,
        email,
        name: email.split('@')[0] || 'Student'
      });
    } else {
      // Admin validation
      if (email === 'admin@university.edu' && password === 'demo123') {
        onLogin({
          role,
          email,
          name: 'Dr. Sarah Chen'
        });
      } else {
        setError('Invalid admin credentials');
      }
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
        p: 2,
      }}
    >
      <Box sx={{ width: '100%', maxWidth: 400 }}>
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <School sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
          <Typography variant="h3" gutterBottom sx={{ fontSize: '2rem' }}>
            DRAE Platform
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Sign in to your account
          </Typography>
        </Box>

        <Card>
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ mb: 3 }}>
              <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
                Account type
              </Typography>
              <ToggleButtonGroup
                value={role}
                exclusive
                onChange={handleRoleChange}
                fullWidth
                size="small"
              >
                <ToggleButton value="student">
                  <School sx={{ mr: 1, fontSize: 18 }} />
                  Student
                </ToggleButton>
                <ToggleButton value="admin">
                  <AdminPanelSettings sx={{ mr: 1, fontSize: 18 }} />
                  Admin
                </ToggleButton>
              </ToggleButtonGroup>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            <Box sx={{ mb: 3 }}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                sx={{ mb: 2 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Email sx={{ fontSize: 18, color: 'text.secondary' }} />
                    </InputAdornment>
                  ),
                }}
              />

              <TextField
                fullWidth
                label="Password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Lock sx={{ fontSize: 18, color: 'text.secondary' }} />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton 
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                        size="small"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
            </Box>

            <Button
              fullWidth
              variant="contained"
              onClick={handleLogin}
              endIcon={<ArrowForward />}
              sx={{ mb: 3, py: 1.5 }}
            >
              Sign in
            </Button>


          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

export default Login;
