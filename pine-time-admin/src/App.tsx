import { lazy, Suspense, useEffect } from 'react'
import { Navigate, createHashRouter, RouterProvider } from 'react-router-dom'
import { ThemeProvider, CssBaseline, CircularProgress, Box } from '@mui/material'
import { lightTheme } from './theme/theme'
import { AuthProvider } from './contexts/AuthContext'
import { LoadingProvider } from './contexts/LoadingContext'
import { useAuth } from './contexts/AuthContext'
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
// Configuration for data router with authentication handling
const withAuth = (Component: React.ComponentType) => {
  const AuthWrapper = () => {
    const { isAuthenticated, isAdmin } = useAuth();
    
    // Debug authentication status
    console.log('Auth status:', { isAuthenticated, isAdmin });
    
    if (!isAuthenticated || !isAdmin) {
      console.log('Not authenticated, redirecting to login');
      return <Navigate to="/login" replace />;
    }
    
    return <Component />;
  };
  
  return <AuthWrapper />;
};

// Create the router configuration with data API
const createAppRouter = () => {
  // Debug router creation
  console.log('Creating hash router with full path handling');
  
  return createHashRouter([
    // Root route with fallback to dashboard
    {
      path: '/',
      element: <Navigate to="/dashboard" replace />
    },
    
    // Admin dashboard main routes
    {
      path: '/dashboard',
      element: withAuth(DashboardPage),
    },
    {
      path: '/users',
      element: withAuth(UsersPage),
    },
    {
      path: '/events',
      element: withAuth(EventsPage),
    },
    {
      path: '/badges',
      element: withAuth(BadgesPage),
    },
    {
      path: '/analytics',
      element: withAuth(AnalyticsPage),
    },
    
    // Auth routes
    {
      path: '/login',
      element: <LoginPage />
    },
    {
      path: '/transition',
      element: <TransitionPage />
    },
    
    // Catch-all route
    {
      path: '*',
      element: <Navigate to="/dashboard" replace />
    }
  ]);
};

function App() {
  // Enhanced comprehensive debugging for router configuration
  useEffect(() => {
    console.log('---- PINE TIME ADMIN DASHBOARD PATH DEBUGGING ----');
    console.log('Raw URL:', window.location.href);
    console.log('Protocol:', window.location.protocol);
    console.log('Host:', window.location.host);
    console.log('Pathname:', window.location.pathname);
    console.log('Hash:', window.location.hash);
    console.log('Search:', window.location.search);
    
    // Attempt to detect deployed environment
    const isAdminSubdirectory = window.location.pathname.includes('/admin');
    console.log('Is in /admin/ subdirectory:', isAdminSubdirectory);
    
    // Log detailed environment information
    console.log('Using Data Router API (createHashRouter)');
    console.log('---- END PATH DEBUGGING ----');
  }, []);
  
  // Create the router configuration
  const router = createAppRouter();

  return (
    <ThemeProvider theme={lightTheme}>
      <CssBaseline /> {/* Reset CSS */}
      <AuthProvider>
        <LoadingProvider>
          <Suspense fallback={<LoadingFallback />}>
            {/* Add the TokenSynchronizer at the top level */}
            <TokenSynchronizer />
            {/* Use RouterProvider instead of HashRouter+Routes */}
            <RouterProvider router={router} />
          </Suspense>
        </LoadingProvider>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
