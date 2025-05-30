import { useEffect } from 'react'
import { Routes, Route, Navigate, useLocation, useNavigate, Outlet } from 'react-router-dom'
import { ThemeProvider, CssBaseline, CircularProgress, Box } from '@mui/material'
import { lightTheme } from './theme/theme'
import { useAuth } from './contexts/AuthContext'
import { useLoading } from './contexts/LoadingContext'

// Layout components
import { AdminLayout } from './components/layout/AdminLayout'

// Page components
import DashboardPage from './pages/dashboard/DashboardPage'
import UsersPage from './pages/users/UsersPage'
import EventsPage from './pages/events/EventsPage'
import BadgesPage from './pages/badges/BadgesPage'
import PointsPage from './pages/points/PointsPage'
import AnalyticsPage from './pages/analytics/AnalyticsPage'
import LoginPage from './pages/login/LoginPage'
import TransitionPage from './pages/TransitionPage'

// Stylesheets
import './App.css'

/**
 * Main App component with routing configuration
 * Handles authentication state and protected routes
 */
function App() {
  const { isAuthenticated, isAdmin, authState, checkAuth } = useAuth();
  const { loading } = useLoading();
  const location = useLocation();
  const navigate = useNavigate();
  
  // Enhanced router debug and authentication management
  useEffect(() => {
    // Basic app diagnostics
    console.log('Pine Time Admin Dashboard loaded');
    
    // Router debug information to verify basename is working correctly
    console.log('Router Debug:', {
      basename: '', // This should match the basename we set in main.tsx
      currentPath: location.pathname, // This should be "/" when at root
      fullURL: window.location.pathname, // This should show the full path
      baseURL: import.meta.env.BASE_URL,
      mode: import.meta.env.MODE
    });
    
    // Authentication diagnostics
    console.log('Auth state:', { 
      isAuthenticated, 
      isAdmin, 
      authState: authState,
      path: location.pathname 
    });
    
    // Only handle redirects after authentication is initialized
    if (authState.isInitialized && !authState.isValidating) {
      // Redirect to login if not authenticated and not already on login or transition page
      const isLoginPage = location.pathname.includes('/login');
      const isTransitionPage = location.pathname.includes('/transition');
      
      if (!isAuthenticated && !isLoginPage && !isTransitionPage) {
        console.log('Not authenticated, redirecting to login');
        navigate('/login', { replace: true });
      }
    }
  }, [location, isAuthenticated, isAdmin, authState, navigate]);

  // Show loading indicator when authentication state is being determined
  if (loading) {
    return (
      <ThemeProvider theme={lightTheme}>
        <CssBaseline />
        <Box 
          sx={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            height: '100vh' 
          }}
        >
          <CircularProgress />
        </Box>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={lightTheme}>
      <CssBaseline />
      <Routes>
        {/* Public routes - with leading slashes for subdirectory deployment */}
        <Route path="/login" element={
          isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />
        } />
        
        {/* Special transition route for direct navigation from main app */}
        <Route path="/transition" element={<TransitionPage />} />
        
        {/* Root route - match exactly / after basename is applied */}
        <Route path="/" element={
          isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />
        } />

        {/* Protected routes - require authentication */}
        {isAuthenticated ? (
          <Route element={<AdminLayout>
            {/* AdminLayout needs children prop */}
            <Outlet />
          </AdminLayout>}>
            {/* All routes with leading slashes for subdirectory deployment */}
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/users" element={<UsersPage />} />
            <Route path="/events" element={<EventsPage />} />
            <Route path="/badges" element={<BadgesPage />} />
            <Route path="/points" element={<PointsPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            
            {/* Fallback route */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Route>
        ) : (
          // Catch-all route when not authenticated
          <Route path="*" element={<Navigate to="/login" replace />} />
        )}
      </Routes>
    </ThemeProvider>
  );
}

export default App
