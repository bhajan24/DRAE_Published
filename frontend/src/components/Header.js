import React from 'react';
import {
  AppBar, Toolbar, Typography, IconButton, Avatar, Box,
  Menu, MenuItem, Chip, Switch, FormControlLabel
} from '@mui/material';
import {
  DarkMode, LightMode, Logout, School, AdminPanelSettings,
  AccountCircle, Settings
} from '@mui/icons-material';

const Header = ({ user, darkMode, onToggleTheme, onLogout }) => {
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleClose();
    onLogout();
  };

  return (
    <AppBar 
      position="sticky" 
      elevation={1}
      sx={{
        bgcolor: darkMode ? 'rgba(18, 18, 18, 0.95)' : 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        borderBottom: 1,
        borderColor: darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
        color: darkMode ? 'white' : 'text.primary',
        top: 0,
        zIndex: 1100,
      }}
    >
      <Toolbar sx={{ minHeight: 48, px: 1.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
          <School sx={{ mr: 1, color: 'primary.main', fontSize: 18 }} />
          <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '0.9rem' }}>
            DRAE Platform
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          {/* Modern Theme Toggle */}
          <Box
            onClick={onToggleTheme}
            sx={{
              position: 'relative',
              width: 40,
              height: 20,
              borderRadius: 10,
              bgcolor: darkMode ? 'primary.main' : 'grey.300',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              px: 0.25,
            }}
          >
            <Box
              sx={{
                width: 16,
                height: 16,
                borderRadius: '50%',
                bgcolor: 'background.paper',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transform: darkMode ? 'translateX(20px)' : 'translateX(0px)',
                transition: 'transform 0.2s ease',
                boxShadow: 1,
              }}
            >
              {darkMode ? (
                <DarkMode sx={{ fontSize: 10, color: 'primary.main' }} />
              ) : (
                <LightMode sx={{ fontSize: 10, color: 'warning.main' }} />
              )}
            </Box>
          </Box>

          <Chip
            icon={user.role === 'student' ? <School sx={{ fontSize: 14 }} /> : <AdminPanelSettings sx={{ fontSize: 14 }} />}
            label={user.role === 'student' ? 'Student' : 'Admin'}
            size="small"
            variant="outlined"
            sx={{ fontSize: '0.7rem', height: 24 }}
          />

          <IconButton onClick={handleMenu} size="small">
            <Avatar
              sx={{
                width: 28,
                height: 28,
                bgcolor: 'primary.main',
                fontSize: '0.8rem',
                fontWeight: 600,
              }}
            >
              {user.name.charAt(0)}
            </Avatar>
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleClose}
            PaperProps={{
              sx: {
                mt: 1,
                minWidth: 180,
              }
            }}
          >
            <Box sx={{ px: 2, py: 1.5, borderBottom: 1, borderColor: 'divider' }}>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                {user.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {user.email}
              </Typography>
            </Box>
            <MenuItem onClick={handleClose}>
              <AccountCircle sx={{ mr: 2, fontSize: 18 }} />
              Profile
            </MenuItem>
            <MenuItem onClick={handleClose}>
              <Settings sx={{ mr: 2, fontSize: 18 }} />
              Settings
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <Logout sx={{ mr: 2, fontSize: 18 }} />
              Sign out
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
