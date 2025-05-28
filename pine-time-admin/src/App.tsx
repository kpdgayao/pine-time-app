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
  const { isAuthenticated, isAdmin, checkAuth } = useAuth();
  const { loading } = useLoading();
  const location = useLocation();
  const navigate = useNavigate();
  
  // Enhanced debugging to diagnose deployment and routing issues
  useEffect(() => {
    // Basic app diagnostics
    console.log('Pine Time Admin Dashboard loaded');
    
    // Enhanced routing diagnostics
    console.log('Navigation diagnostics:', {
      fullUrl: window.location.href,
      pathname: location.pathname,
      baseUrl: import.meta.env.BASE_URL,
      mode: import.meta.env.MODE,
      hash: window.location.hash,
      search: window.location.search,
      host: window.location.host
    });
    
    // Authentication diagnostics
    console.log('Auth state:', { isAuthenticated, isAdmin });
    const isAuth = checkAuth();
    console.log('Auth check result:', isAuth);
    
    // Asset path diagnostics
    console.log('Asset path resolution:', {
      relativePath: 'assets/logo.png',
      withBaseUrl: `${import.meta.env.BASE_URL}assets/logo.png`,
      withSlash: '/assets/logo.png',
      withoutSlash: 'assets/logo.png'
    });
    
    // Redirect to login if not authenticated and not already on login page
    if (!isAuth && !location.pathname.includes('login')) {
      console.log('Not authenticated, redirecting to login');
      navigate('login', { replace: true });
    }
  }, [location, isAuthenticated, isAdmin, checkAuth, navigate]);

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
        {/* Public routes */}
        <Route path="login" element={
          isAuthenticated ? <Navigate to="dashboard" replace /> : <LoginPage />
        } />
        
        {/* Special transition route for direct navigation from main app */}
        <Route path="transition" element={<TransitionPage />} />
        
        {/* Protected routes - require authentication */}
        {isAuthenticated ? (
          <Route element={<AdminLayout>
            {/* AdminLayout needs children prop */}
            <Outlet />
          </AdminLayout>}>
            <Route path="" element={<Navigate to="dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="users" element={<UsersPage />} />
            <Route path="events" element={<EventsPage />} />
            <Route path="badges" element={<BadgesPage />} />
            <Route path="points" element={<PointsPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            
            {/* Fallback route */}
            <Route path="*" element={<Navigate to="dashboard" replace />} />
          </Route>
        ) : (
          // Catch-all route when not authenticated
          <Route path="*" element={<Navigate to="login" replace />} />
        )}
      </Routes>
    </ThemeProvider>
  );
}

export default App
