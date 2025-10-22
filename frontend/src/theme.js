import { createTheme } from '@mui/material/styles';

const baseTheme = {
  spacing: 6, // Reduced from default 8
  shape: {
    borderRadius: 6, // Reduced from default 8
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          '&:hover': {
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
          },
        },
      },
    },
    MuiCardContent: {
      styleOverrides: {
        root: {
          padding: '16px',
          '&:last-child': {
            paddingBottom: '16px',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: 6,
        },
        sizeSmall: {
          padding: '4px 12px',
          fontSize: '0.8125rem',
        },
        sizeMedium: {
          padding: '6px 16px',
          fontSize: '0.875rem',
        },
      },
    },
    MuiTextField: {
      defaultProps: {
        size: 'small',
      },
    },
    MuiFormControl: {
      defaultProps: {
        size: 'small',
      },
    },
  },
};

export const lightTheme = createTheme({
  ...baseTheme,
  palette: {
    mode: 'light',
    primary: {
      main: '#635bff',
      light: '#7c75ff',
      dark: '#4c44db',
    },
    secondary: {
      main: '#00d924',
      light: '#33e047',
      dark: '#00a71c',
    },
    background: {
      default: '#fafbfc',
      paper: '#ffffff',
    },
    text: {
      primary: '#0a2540',
      secondary: '#425466',
    },
    grey: {
      50: '#f6f9fc',
      100: '#e3ebf0',
      200: '#c7d2dd',
      300: '#9daab7',
      400: '#68768a',
      500: '#425466',
      600: '#3c4257',
      700: '#293040',
      800: '#1a1f36',
      900: '#0a2540',
    },
    divider: '#e3ebf0',
  },
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
      lineHeight: 1.2,
      letterSpacing: '-0.025em',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      lineHeight: 1.3,
      letterSpacing: '-0.025em',
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h4: {
      fontSize: '1.25rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.125rem',
      fontWeight: 500,
      lineHeight: 1.4,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
      lineHeight: 1.4,
    },
    body1: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.8125rem',
      lineHeight: 1.4,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: '6px',
          fontWeight: 500,
          fontSize: '0.875rem',
          padding: '10px 16px',
          boxShadow: 'none',
          border: '1px solid transparent',
          transition: 'all 0.15s ease',
          '&:hover': {
            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
          },
        },
        contained: {
          backgroundColor: '#635bff',
          color: '#ffffff',
          '&:hover': {
            backgroundColor: '#4c44db',
            boxShadow: '0 2px 4px rgba(99, 91, 255, 0.4)',
          },
        },
        outlined: {
          borderColor: '#e3ebf0',
          color: '#425466',
          '&:hover': {
            borderColor: '#c7d2dd',
            backgroundColor: '#f6f9fc',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
          border: '1px solid #e3ebf0',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.12)',
          '&:hover': {
            boxShadow: '0 2px 6px rgba(0, 0, 0, 0.15)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: '6px',
            fontSize: '0.875rem',
            '& fieldset': {
              borderColor: '#e3ebf0',
            },
            '&:hover fieldset': {
              borderColor: '#c7d2dd',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#635bff',
              borderWidth: '1px',
            },
          },
          '& .MuiInputLabel-root': {
            fontSize: '0.875rem',
            color: '#425466',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: '4px',
          fontSize: '0.75rem',
          fontWeight: 500,
          height: '24px',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
  },
});

export const darkTheme = createTheme({
  ...baseTheme,
  palette: {
    mode: 'dark',
    primary: {
      main: '#7c75ff',
      light: '#9d97ff',
      dark: '#635bff',
    },
    secondary: {
      main: '#00d924',
      light: '#33e047',
      dark: '#00a71c',
    },
    background: {
      default: '#0a0e27',
      paper: '#1a1f36',
    },
    text: {
      primary: '#ffffff',
      secondary: '#9daab7',
    },
    grey: {
      50: '#1a1f36',
      100: '#293040',
      200: '#3c4257',
      300: '#425466',
      400: '#68768a',
      500: '#9daab7',
      600: '#c7d2dd',
      700: '#e3ebf0',
      800: '#f6f9fc',
      900: '#ffffff',
    },
    divider: '#3c4257',
  },
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
      lineHeight: 1.2,
      letterSpacing: '-0.025em',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      lineHeight: 1.3,
      letterSpacing: '-0.025em',
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h4: {
      fontSize: '1.25rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.125rem',
      fontWeight: 500,
      lineHeight: 1.4,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
      lineHeight: 1.4,
    },
    body1: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.8125rem',
      lineHeight: 1.4,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: '6px',
          fontWeight: 500,
          fontSize: '0.875rem',
          padding: '10px 16px',
          boxShadow: 'none',
          border: '1px solid transparent',
          transition: 'all 0.15s ease',
        },
        contained: {
          backgroundColor: '#7c75ff',
          color: '#ffffff',
          '&:hover': {
            backgroundColor: '#635bff',
            boxShadow: '0 2px 4px rgba(124, 117, 255, 0.4)',
          },
        },
        outlined: {
          borderColor: '#3c4257',
          color: '#9daab7',
          '&:hover': {
            borderColor: '#425466',
            backgroundColor: '#293040',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
          border: '1px solid #3c4257',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.3)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: '6px',
            fontSize: '0.875rem',
            '& fieldset': {
              borderColor: '#3c4257',
            },
            '&:hover fieldset': {
              borderColor: '#425466',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#7c75ff',
              borderWidth: '1px',
            },
          },
          '& .MuiInputLabel-root': {
            fontSize: '0.875rem',
            color: '#9daab7',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: '4px',
          fontSize: '0.75rem',
          fontWeight: 500,
          height: '24px',
        },
      },
    },
  },
});
