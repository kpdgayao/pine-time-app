import { createTheme } from '@mui/material/styles';

// Pine Time brand colors - keeping consistent with the user frontend
const pineGreen = '#2E7D32';  // Primary brand color
const lightGreen = '#4CAF50';
const darkGreen = '#1B5E20';
const accentOrange = '#FF9800';
const lightGray = '#F5F5F5';
const darkGray = '#424242';

// Create a theme instance that matches the Pine Time application standards
export const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: pineGreen,
      light: lightGreen,
      dark: darkGreen,
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: accentOrange,
      contrastText: '#000000',
    },
    background: {
      default: lightGray,
      paper: '#FFFFFF',
    },
    text: {
      primary: darkGray,
      secondary: '#757575',
    },
    error: {
      main: '#D32F2F',
    },
    warning: {
      main: '#FFC107',
    },
    info: {
      main: '#2196F3',
    },
    success: {
      main: pineGreen,
    },
  },
  typography: {
    fontFamily: "'Roboto', 'Helvetica', 'Arial', sans-serif",
    h1: {
      fontWeight: 500,
      fontSize: '2.5rem',
      color: pineGreen,
    },
    h2: {
      fontWeight: 500,
      fontSize: '2rem',
      color: pineGreen,
    },
    h3: {
      fontWeight: 500,
      fontSize: '1.75rem',
    },
    h4: {
      fontWeight: 500,
      fontSize: '1.5rem',
    },
    h5: {
      fontWeight: 500,
      fontSize: '1.25rem',
    },
    h6: {
      fontWeight: 500,
      fontSize: '1rem',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
        },
        containedPrimary: {
          backgroundColor: pineGreen,
          '&:hover': {
            backgroundColor: darkGreen,
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: pineGreen,
        },
      },
    },
    MuiTableHead: {
      styleOverrides: {
        root: {
          backgroundColor: lightGray,
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: {
          fontWeight: 700,
        },
      },
    },
    // Material UI v7 Grid system requires different styling
    MuiGrid: {
      styleOverrides: {
        root: {
          // Add any global grid styles here
        },
      },
    },
  },
});

// Also export the dark theme for future use if needed
export const darkTheme = createTheme({
  ...lightTheme,
  palette: {
    ...lightTheme.palette,
    mode: 'dark',
    primary: {
      main: lightGreen,
      light: pineGreen,
      dark: '#1B5E20',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#121212',
      paper: '#1E1E1E',
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#B0B0B0',
    },
  },
});
