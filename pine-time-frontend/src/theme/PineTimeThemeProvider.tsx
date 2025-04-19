import * as React from 'react';
import { createTheme, ThemeProvider, CssBaseline } from '@mui/material';

// Pine Time green: #2E7D32
const pineTimeTheme = createTheme({
  palette: {
    primary: {
      main: '#2E7D32',
    },
    secondary: {
      main: '#FFC107', // Example accent color
    },
    background: {
      default: '#F9F9F9',
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
  },
});

interface PineTimeThemeProviderProps {
  children: React.ReactNode;
}

export default function PineTimeThemeProvider({ children }: PineTimeThemeProviderProps) {
  return (
    <ThemeProvider theme={pineTimeTheme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}
