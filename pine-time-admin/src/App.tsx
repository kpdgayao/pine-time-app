import { useEffect } from 'react'
import { ThemeProvider, CssBaseline, Typography, Box, Container, AppBar, Toolbar, Button } from '@mui/material'
import { lightTheme } from './theme/theme'
import './App.css'

/**
 * Simple Admin Dashboard
 * This is a minimal implementation to ensure the admin dashboard loads correctly
 */
function App() {
  // Log debugging information to help diagnose issues
  useEffect(() => {
    console.log('Pine Time Admin Dashboard loaded');
    console.log('URL:', window.location.href);
    console.log('Path:', window.location.pathname);
    console.log('Hash:', window.location.hash);
    
    // Check for authentication token
    const token = localStorage.getItem('access_token');
    console.log('Auth token exists:', !!token);
  }, []);

  return (
    <ThemeProvider theme={lightTheme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Pine Time Admin Dashboard
            </Typography>
            <Button color="inherit" onClick={() => window.location.href = '/'}>
              Return to Main App
            </Button>
          </Toolbar>
        </AppBar>
        
        <Container sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
          <Box sx={{ py: 4, textAlign: 'center' }}>
            <Typography variant="h4" gutterBottom>
              Welcome to Pine Time Admin Dashboard
            </Typography>
            <Typography variant="body1">
              This dashboard provides administration capabilities for the Pine Time application.
            </Typography>
            
            {/* Basic navigation buttons */}
            <Box sx={{ mt: 4, display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
              <Button variant="contained">Dashboard</Button>
              <Button variant="outlined">Users</Button>
              <Button variant="outlined">Events</Button>
              <Button variant="outlined">Badges</Button>
              <Button variant="outlined">Analytics</Button>
            </Box>
          </Box>
        </Container>
        
        <Box sx={{ bgcolor: 'primary.main', color: 'white', py: 2, textAlign: 'center' }}>
          <Typography variant="body2">
            Pine Time Admin Dashboard © {new Date().getFullYear()}
          </Typography>
        </Box>
      </Box>
    </ThemeProvider>
  )
}

export default App
