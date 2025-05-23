import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, CssBaseline, CircularProgress, Box } from '@mui/material'
import { lightTheme } from './theme/theme'
import { AuthProvider } from './contexts/AuthContext'
import { LoadingProvider } from './contexts/LoadingContext'
import ProtectedRoute from './components/auth/ProtectedRoute'
import { ADMIN_ROUTES } from './config'
import './App.css'

// Lazy load pages for better performance
const LoginPage = lazy(() => import('./pages/login'))
const DashboardPage = lazy(() => import('./pages/dashboard'))
const UsersPage = lazy(() => import('./pages/users'))
const EventsPage = lazy(() => import('./pages/events'))
const BadgesPage = lazy(() => import('./pages/badges'))
const AnalyticsPage = lazy(() => import('./pages/analytics'))

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
              <Routes>
                {/* Public routes */}
                <Route path={ADMIN_ROUTES.LOGIN} element={<LoginPage />} />
                
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
