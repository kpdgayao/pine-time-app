import { lazy, Suspense, useEffect } from 'react'
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, CssBaseline, CircularProgress, Box } from '@mui/material'
import { lightTheme } from './theme/theme'
import { AuthProvider } from './contexts/AuthContext'
import { LoadingProvider } from './contexts/LoadingContext'
import ProtectedRoute from './components/auth/ProtectedRoute'
import { useAuth } from './contexts/AuthContext'
import { ADMIN_ROUTES } from './config'
import './App.css'

// Lazy load pages for better performance
// Login page removed as we're using the main app for authentication
const DashboardPage = lazy(() => import('./pages/dashboard'))
const UsersPage = lazy(() => import('./pages/users'))
const EventsPage = lazy(() => import('./pages/events'))
const BadgesPage = lazy(() => import('./pages/badges'))
const AnalyticsPage = lazy(() => import('./pages/analytics'))

// Import TransitionPage for seamless authentication from main app
// This is a critical component to handle token transfers between apps
const TransitionPage = lazy(() => import('./pages/TransitionPage'))
const LoginPage = lazy(() => import('./pages/login/LoginPage'))

/**
 * Loading fallback component that displays while lazy-loaded components are being loaded
 */
const LoadingFallback = () => (
  <Box
    sx={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      bgcolor: 'background.default'
    }}
  >
    <CircularProgress color="primary" />
  </Box>
)

/**
 * Token Synchronizer component to handle automatic token checking
 */
const TokenSynchronizer = () => {
  // Only use checkAuth to avoid unused variable warnings
  const { checkAuth } = useAuth();
  
  useEffect(() => {
    console.log('TokenSynchronizer running initial auth check');
    // Check for tokens from main app and transfer if needed
    const mainToken = localStorage.getItem('access_token');
    
    if (mainToken) {
      console.log('Main app token found, syncing with admin dashboard');
      const success = checkAuth();
      console.log('Auth check result:', success);
    }
  }, [checkAuth]);
  
  return null; // This component doesn't render anything
};

/**
 * Main App component with routing, theming, and global context providers
 */
function App() {
  // Enhanced comprehensive debugging for HashRouter path resolution
  useEffect(() => {
    console.log('---- PINE TIME ADMIN DASHBOARD PATH DEBUGGING ----');
    console.log('Raw URL:', window.location.href);
    console.log('Protocol:', window.location.protocol);
    console.log('Host:', window.location.host);
    console.log('Pathname:', window.location.pathname);
    console.log('Hash:', window.location.hash);
    console.log('Search:', window.location.search);
    console.log('Routes config:', JSON.stringify(ADMIN_ROUTES));
    
    // Attempt to detect deployed environment
    const isAdminSubdirectory = window.location.pathname.includes('/admin');
    console.log('Is in /admin/ subdirectory:', isAdminSubdirectory);
    
    // Parse the hash to help debug route matching issues
    const hash = window.location.hash;
    if (hash) {
      // Extract the path from the hash
      const hashPath = hash.replace('#', '');
      console.log('Hash path (without #):', hashPath);
      
      // Expected route matching
      const expectedRoute = hashPath || '/';
      console.log('Expected route to match:', expectedRoute);
      
      // Detailed path segments analysis
      const segments = hashPath.split('/').filter(Boolean);
      console.log('Path segments:', segments);
      console.log('Number of segments:', segments.length);
      
      // Try to determine which route should match
      if (segments.length === 0) {
        console.log('Should match dashboard route (empty path)');
      } else {
        console.log('Should match route:', segments[0]);
      }
    }
    
    // Check for any base href element
    const baseElement = document.querySelector('base');
    if (baseElement) {
      console.log('Base href found:', baseElement.getAttribute('href'));
    } else {
      console.log('No base href element in document');
    }
    
    // Log HashRouter configuration
    console.log('HashRouter configured with empty basename');
    console.log('---- END PATH DEBUGGING ----');
  }, []);

  return (
    <ThemeProvider theme={lightTheme}>
      <CssBaseline /> {/* Reset CSS */}
      <HashRouter basename="">
        {/* Using HashRouter with empty basename to prevent path conflicts */}
        <AuthProvider>
          <LoadingProvider>
            <Suspense fallback={<LoadingFallback />}>
              {/* Add the TokenSynchronizer at the top level */}
              <TokenSynchronizer />
              <Routes>
                {/* Go back to using explicit routes for better reliability */}
                {/* Transition route to handle authentication from main app */}
                <Route path="transition" element={<TransitionPage />} />
                
                {/* Login page - only for direct access or fallback */}
                <Route path="login" element={<LoginPage />} />
                
                {/* Protected routes */}
                <Route 
                  path="" 
                  element={
                    <ProtectedRoute>
                      <DashboardPage />
                    </ProtectedRoute>
                  } 
                />
                
                <Route 
                  path="users" 
                  element={
                    <ProtectedRoute>
                      <UsersPage />
                    </ProtectedRoute>
                  } 
                />
                
                <Route 
                  path="events" 
                  element={
                    <ProtectedRoute>
                      <EventsPage />
                    </ProtectedRoute>
                  } 
                />
                
                <Route 
                  path="badges" 
                  element={
                    <ProtectedRoute>
                      <BadgesPage />
                    </ProtectedRoute>
                  } 
                />
                
                <Route 
                  path="analytics" 
                  element={
                    <ProtectedRoute>
                      <AnalyticsPage />
                    </ProtectedRoute>
                  } 
                />
                
                {/* Explicit route for empty path to handle /admin/ in production */}
                <Route path="/" element={<Navigate to="" replace />} />
                
                {/* Catch all other routes and redirect to dashboard */}
                <Route path="*" element={<Navigate to="" replace />} />
              </Routes>
            </Suspense>
          </LoadingProvider>
        </AuthProvider>
      </HashRouter>
    </ThemeProvider>
  )
}

export default App
