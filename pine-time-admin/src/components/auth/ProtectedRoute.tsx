import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Box, CircularProgress, Typography } from '@mui/material';

interface ProtectedRouteProps {
  children: React.ReactElement;
}

/**
 * ProtectedRoute component that ensures only authenticated users can access routes
 * Enhanced with automatic token checking from both admin and main app storage
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isAdmin, checkAuth } = useAuth();
  const [isChecking, setIsChecking] = useState(true);
  
  // On initial render, try to automatically authenticate with available tokens
  useEffect(() => {
    const attemptAutoAuth = async () => {
      console.log('ProtectedRoute: Attempting automatic authentication...');
      
      // Check for main app tokens first
      const mainToken = localStorage.getItem('access_token');
      
      if (mainToken) {
        console.log('ProtectedRoute: Found main app token, trying to authenticate');
      }
      
      // Run auth check which will try both admin and main app tokens
      const result = checkAuth();
      console.log('ProtectedRoute: Auth check result:', result);
      
      // Short delay to ensure state updates properly
      await new Promise(resolve => setTimeout(resolve, 500));
      setIsChecking(false);
    };
    
    attemptAutoAuth();
  }, [checkAuth]);
  
  // Show loading state while checking authentication
  if (isChecking) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress size={40} />
          <Typography variant="body1" sx={{ mt: 2 }}>
            Verifying credentials...
          </Typography>
        </Box>
      </Box>
    );
  }

  // Check if user is authenticated and has admin privileges
  if (!isAuthenticated || !isAdmin) {
    console.log('ProtectedRoute: Not authenticated or not admin, redirecting to login');
    // Always use relative path for login to ensure correct redirect in both dev and prod
    return <Navigate to="/login" replace />;
  }

  // If authenticated, render the protected content
  console.log('ProtectedRoute: Authentication successful, rendering protected content');
  return children;
};

export default ProtectedRoute;
