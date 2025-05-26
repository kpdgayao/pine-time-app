import React, { useEffect, useState } from 'react';
import { Box, CircularProgress, Typography, Button, Alert } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { jwtDecode } from 'jwt-decode';

/**
 * TransitionPage handles seamless authentication when coming from the main app
 * It checks for authentication tokens and redirects accordingly
 */
const TransitionPage: React.FC = () => {
  // Include isAuthenticated for token status display
  const { checkAuth, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [message, setMessage] = useState('Authenticating...');
  const [error, setError] = useState<string | null>(null);
  const [debug, setDebug] = useState<string[]>([]);
  
  // Helper function to add debug messages
  const addDebug = (msg: string) => {
    console.log('TransitionPage Debug:', msg);
    setDebug(prev => [...prev, msg]);
  };

  // Single useEffect with clear authentication logic
  // Using a ref to prevent multiple executions
  const authAttemptedRef = React.useRef(false);
  
  useEffect(() => {
    // Prevent multiple authentication attempts
    if (authAttemptedRef.current) {
      return;
    }
    
    // Mark that we've attempted authentication
    authAttemptedRef.current = true;
    
    const handleAuthentication = async () => {
      try {
        addDebug('Starting authentication check');
        
        // Check for one-time auth key in the URL parameters
        const searchParams = new URLSearchParams(window.location.search);
        const oneTimeAuthKey = searchParams.get('auth');
        
        if (oneTimeAuthKey) {
          addDebug(`Found one-time auth key: ${oneTimeAuthKey}`);
          
          // Try to get the auth data from sessionStorage
          const authDataString = sessionStorage.getItem(oneTimeAuthKey);
          
          if (authDataString) {
            try {
              const authData = JSON.parse(authDataString);
              addDebug('Successfully parsed auth data');
              
              // Check if the auth key has expired
              const now = Date.now();
              if (authData.expires < now) {
                addDebug('Auth key has expired');
                setError('Authentication expired. Please try again.');
                // Clean up expired key
                sessionStorage.removeItem(oneTimeAuthKey);
                return;
              }
              
              // Extract tokens
              const token = authData.accessToken;
              const refreshToken = authData.refreshToken;
              
              if (token && refreshToken) {
                addDebug('Extracted valid tokens from auth data');
                
                try {
                  // Validate token has admin privileges
                  const decoded = jwtDecode<any>(token);
                  const isAdmin = decoded.is_superuser || 
                                decoded.user_type === 'admin' || 
                                decoded.role === 'admin';
                                
                  addDebug(`Token has admin privileges: ${isAdmin}`);
                  
                  if (!isAdmin) {
                    setError('Your account does not have admin privileges');
                    return;
                  }
                  
                  // Transfer tokens to admin format
                  localStorage.setItem('admin_access_token', token);
                  localStorage.setItem('admin_refresh_token', refreshToken);
                  localStorage.setItem('pine_time_direct_auth', 'true');
                  setMessage('Access granted, redirecting to dashboard...');
                  
                  // Clean up the one-time auth key
                  sessionStorage.removeItem(oneTimeAuthKey);
                  
                  // Force authentication check
                  const authResult = checkAuth();
                  addDebug(`Auth check result: ${authResult}`);
                  
                  // Wait for a moment to allow token processing
                  await new Promise(resolve => setTimeout(resolve, 500));
                  
                  // Go to dashboard
                  navigate('/');
                  return;
                } catch (tokenError) {
                  addDebug(`Token decode error: ${tokenError}`);
                  setError('Invalid authentication token');
                  return;
                }
              }
            } catch (parseError) {
              addDebug(`Failed to parse auth data: ${parseError}`);
              setError('Authentication data is invalid');
              return;
            }
          } else {
            addDebug('Auth key not found in sessionStorage');
            setError('Authentication session not found or expired');
            return;
          }
        }
        
        // Fall back to checking regular token locations
        const mainToken = localStorage.getItem('access_token');
        const mainRefreshToken = localStorage.getItem('refresh_token');
        const adminToken = localStorage.getItem('admin_access_token');
        const adminRefreshToken = localStorage.getItem('admin_refresh_token');
        
        addDebug(`Main token exists: ${!!mainToken}`);
        addDebug(`Admin token exists: ${!!adminToken}`);
        
        // Check for valid tokens in admin storage
        if (adminToken && adminRefreshToken) {
          addDebug('Using existing admin tokens');
          const authResult = checkAuth();
          addDebug(`Auth check result: ${authResult}`);
          
          if (authResult) {
            setMessage('Already authenticated, redirecting to dashboard...');
            navigate('/');
            return;
          }
        }
        
        // Try with main app tokens as last resort
        if (mainToken && mainRefreshToken) {
          addDebug('Trying with main app tokens');
          
          // Transfer tokens to admin format
          localStorage.setItem('admin_access_token', mainToken);
          localStorage.setItem('admin_refresh_token', mainRefreshToken);
          
          // Force authentication check
          const authResult = checkAuth();
          addDebug(`Auth check result: ${authResult}`);
          
          if (authResult) {
            navigate('/');
            return;
          }
        }
        
        // If no valid tokens found, redirect to login with clear error
        addDebug('No valid tokens found, redirecting to login');
        setMessage('Authentication required');
        setTimeout(() => navigate('/login'), 800);
      } catch (err) {
        console.error('Authentication error:', err);
        addDebug(`Error: ${err}`);
        setError('Authentication failed. Please try again.');
      }
    };
    
    handleAuthentication();
  }, [navigate, checkAuth]);
  
  // This was causing an infinite loop - we need to prevent multiple redirects
  // We'll combine all authentication logic into a single useEffect

  return (
    <Box 
      sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        alignItems: 'center', 
        justifyContent: 'center', 
        height: '100vh',
        bgcolor: 'background.default',
        p: 3
      }}
    >
      <Box sx={{ textAlign: 'center', maxWidth: '600px', width: '100%' }}>
        <Typography variant="h5" color="primary" gutterBottom>
          Pine Time Admin
        </Typography>
        <CircularProgress color="primary" sx={{ my: 3 }} />
        <Typography variant="body1" color="text.secondary" gutterBottom>
          {error || message}
        </Typography>
        
        {/* Debug information section */}
        <Box sx={{ mt: 4, mb: 2, textAlign: 'left', border: '1px solid #eee', p: 2, borderRadius: 1 }}>
          <Typography variant="subtitle2" color="primary" gutterBottom>
            Authentication Debug Information
          </Typography>
          <Box component="pre" sx={{ 
            backgroundColor: '#f5f5f5', 
            p: 2, 
            borderRadius: 1, 
            fontSize: '0.75rem',
            overflowX: 'auto',
            maxHeight: '200px',
            overflowY: 'auto'
          }}>
            {debug.map((msg, index) => (
              <Box key={index} component="div">
                {index + 1}. {msg}
              </Box>
            ))}
          </Box>
          
          {/* Token information */}
          <Typography variant="subtitle2" color="primary" sx={{ mt: 2 }} gutterBottom>
            Current Token State
          </Typography>
          <Box component="pre" sx={{ 
            backgroundColor: '#f5f5f5', 
            p: 2, 
            borderRadius: 1, 
            fontSize: '0.75rem',
            overflowX: 'auto'
          }}>
            Main Access Token: {localStorage.getItem('access_token') ? '✅ Present' : '❌ Missing'}
            Admin Access Token: {localStorage.getItem('admin_access_token') ? '✅ Present' : '❌ Missing'}
            Direct Auth Flag: {localStorage.getItem('pine_time_direct_auth') ? '✅ Present' : '❌ Missing'}
            Return to Admin Flag: {localStorage.getItem('return_to_admin') ? '✅ Present' : '❌ Missing'}
            User Status: {isAuthenticated ? '✅ Authenticated' : '❌ Not Authenticated'}
          </Box>
        </Box>
        
        <Box sx={{ mt: 3 }}>
          {error ? (
            <>
              <Button 
                variant="contained" 
                color="primary"
                onClick={() => navigate('/login')}
              >
                Go to Login
              </Button>
              <Button 
                variant="outlined" 
                color="secondary"
                onClick={() => window.location.href = import.meta.env.DEV ? 'http://localhost:5173' : '/'}
                sx={{ ml: 2 }}
              >
                Return to Main App
              </Button>
            </>
          ) : (
            <Button 
              variant="contained" 
              color="primary"
              onClick={() => {
                // Force check auth and redirect
                const result = checkAuth();
                addDebug(`Manual auth check: ${result}`);
                if (result) {
                  navigate('/');
                } else {
                  navigate('/login');
                }
              }}
            >
              Try Authentication Again
            </Button>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default TransitionPage;
