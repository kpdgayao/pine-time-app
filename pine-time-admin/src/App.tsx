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
  // Enhanced debugging for HashRouter
  useEffect(() => {
    console.log('Current pathname:', window.location.pathname);
    console.log('Current hash:', window.location.hash);
    console.log('Full URL:', window.location.href);
    console.log('Dashboard route:', ADMIN_ROUTES.DASHBOARD);
    console.log('All admin routes:', JSON.stringify(ADMIN_ROUTES));
    
    // Parse the hash to help debug route matching issues
    const hash = window.location.hash;
    if (hash) {
      console.log('Hash path (without #):', hash.replace('#', ''));
      
      // Try to manually parse the hash path to determine what route should match
      let hashPath = hash.replace('#', '');
      if (hashPath === '/') {
        console.log('Hash path is root, should match dashboard route');
      } else {
        console.log('Hash path segments:', hashPath.split('/').filter(Boolean));
      }
    }
    
    // Handle potential URL path issues by dynamically checking
    if (window.location.pathname.includes('/admin') && window.location.hash === '#/') {
      console.log('Detected admin path with hash - applying fix for subdirectory routing');
    }
    
    // Log if we're using the base href approach
    const baseElement = document.querySelector('base');
    if (baseElement) {
      console.log('Using base href:', baseElement.getAttribute('href'));
    } else {
      console.log('No base href found in document');
    }
  }, []);

  return (
    <ThemeProvider theme={lightTheme}>
      <CssBaseline /> {/* Reset CSS */}
      <HashRouter>
        {/* Using HashRouter for more reliable routing in production */}
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
