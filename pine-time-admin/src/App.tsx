import { lazy, Suspense, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
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
  return (
    <ThemeProvider theme={lightTheme}>
      <CssBaseline /> {/* Reset CSS */}
      <BrowserRouter>
        <AuthProvider>
          <LoadingProvider>
            <Suspense fallback={<LoadingFallback />}>
              {/* Add the TokenSynchronizer at the top level */}
              <TokenSynchronizer />
              <Routes>
                {/* Transition route to handle authentication from main app */}
                <Route path="/transition" element={<TransitionPage />} />
                
                {/* Login page - only for direct access or fallback */}
                <Route path="/login" element={<LoginPage />} />
                
                {/* Protected routes */}
                <Route 
                  path={ADMIN_ROUTES.DASHBOARD} 
                  element={
                    <ProtectedRoute>
                      <DashboardPage />
                    </ProtectedRoute>
                  } 
                />
                
                <Route 
                  path={ADMIN_ROUTES.USERS} 
                  element={
                    <ProtectedRoute>
                      <UsersPage />
                    </ProtectedRoute>
                  } 
                />
                
                <Route 
                  path={ADMIN_ROUTES.EVENTS} 
                  element={
                    <ProtectedRoute>
                      <EventsPage />
                    </ProtectedRoute>
                  } 
                />
                
                <Route 
                  path={ADMIN_ROUTES.BADGES} 
                  element={
                    <ProtectedRoute>
                      <BadgesPage />
                    </ProtectedRoute>
                  } 
                />
                
                <Route 
                  path={ADMIN_ROUTES.ANALYTICS} 
                  element={
                    <ProtectedRoute>
                      <AnalyticsPage />
                    </ProtectedRoute>
                  } 
                />
                
                {/* Redirect to dashboard by default */}
                <Route path="*" element={<Navigate to={ADMIN_ROUTES.DASHBOARD} replace />} />
              </Routes>
            </Suspense>
          </LoadingProvider>
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App
