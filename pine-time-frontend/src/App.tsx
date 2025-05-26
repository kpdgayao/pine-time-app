
import { lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { lightTheme } from './theme/theme';
import { AuthProvider } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';
import { LoadingProvider } from './contexts/LoadingContext';
import { PaymentProvider } from './contexts/PaymentContext';
import LoadingInitializer from './components/LoadingInitializer';
import Navbar from './components/Navbar';
import PrivateRoute from './components/PrivateRoute';
import LazyRoute from './components/LazyRoute';

// Lazy load pages to improve initial load performance
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const EventsPage = lazy(() => import('./pages/EventsPage'));
const EventDetailsPage = lazy(() => import('./pages/EventDetailsPage'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));
const BadgesPage = lazy(() => import('./pages/BadgesPage'));
const PointsPage = lazy(() => import('./pages/PointsPage'));
const LeaderboardPage = lazy(() => import('./pages/LeaderboardPage'));
const ForgotPasswordPage = lazy(() => import('./pages/ForgotPasswordPage'));
const ResetPasswordPage = lazy(() => import('./pages/ResetPasswordPage'));
// Admin dashboard is now in a separate application
// const AdminDashboardPage = lazy(() => import('./pages/AdminDashboardPage'));

function App() {
  return (
    <ThemeProvider theme={lightTheme}>
      <CssBaseline />
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <AuthProvider>
          <ToastProvider>
            <LoadingProvider>
              <PaymentProvider>
                <LoadingInitializer />
                <Router>
                <Navbar />
                <div style={{ width: '100vw', maxWidth: 'none', margin: 0, padding: 0 }}>
                  <Routes>
                  <Route path="/" element={<LazyRoute component={EventsPage} pageName="Events" />} />
                  <Route path="/login" element={<LazyRoute component={LoginPage} pageName="Login" />} />
                  <Route path="/register" element={<LazyRoute component={RegisterPage} pageName="Registration" />} />
                  <Route path="/events/:eventId" element={<LazyRoute component={EventDetailsPage} pageName="Event Details" />} />
                  <Route path="/profile" element={<PrivateRoute><LazyRoute component={ProfilePage} pageName="Profile" /></PrivateRoute>} />
                  <Route path="/badges" element={<PrivateRoute><LazyRoute component={BadgesPage} pageName="Badges" /></PrivateRoute>} />
                  <Route path="/points" element={<PrivateRoute><LazyRoute component={PointsPage} pageName="Points" /></PrivateRoute>} />
                  <Route path="/leaderboard" element={<PrivateRoute><LazyRoute component={LeaderboardPage} pageName="Leaderboard" /></PrivateRoute>} />
                  <Route path="/forgot-password" element={<LazyRoute component={ForgotPasswordPage} pageName="Password Recovery" />} />
                  <Route path="/reset-password" element={<LazyRoute component={ResetPasswordPage} pageName="Password Reset" />} />
                  {/* Admin route is now handled by adminAccess.ts utility */}
                  </Routes>
                </div>
              </Router>
              </PaymentProvider>
            </LoadingProvider>
          </ToastProvider>
        </AuthProvider>
      </LocalizationProvider>
    </ThemeProvider>
  );
}

export default App;
