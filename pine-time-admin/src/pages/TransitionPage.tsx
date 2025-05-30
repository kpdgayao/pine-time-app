import React, { useEffect, useState } from 'react';
import { Box, CircularProgress, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { jwtDecode } from 'jwt-decode';

/**
 * TransitionPage handles seamless authentication when coming from the main app
 * It checks for authentication tokens and redirects accordingly
 */
const TransitionPage: React.FC = () => {
  // Include enhanced auth state from context
  const { checkAuth, isAuthenticated, authState, login } = useAuth();
  const navigate = useNavigate();
  const [message, setMessage] = useState('Authenticating...');
  const [error, setError] = useState<string | null>(null);
  const [debug, setDebug] = useState<string[]>([]);
  const [authAttempting, setAuthAttempting] = useState(false);
  
  // Helper function to add debug messages with timestamp
  const addDebug = (msg: string) => {
    const timestamp = new Date().toISOString().split('T')[1].substring(0, 8);
    const debugMsg = `[${timestamp}] ${msg}`;
    console.log('TransitionPage Debug:', debugMsg);
    setDebug(prev => [...prev, debugMsg]);
  };

  // Add a timeout for authentication operations
  useEffect(() => {
    const authTimer = setTimeout(() => {
      if (!isAuthenticated && authAttempting) {
        setError('Authentication timed out. Please try again.');
        addDebug('Authentication operation timed out after 10 seconds');
      }
    }, 10000); // 10 seconds timeout

    return () => clearTimeout(authTimer);
  }, [isAuthenticated, authAttempting]);

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
    setAuthAttempting(true);
    
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
                setAuthAttempting(false);
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
                    setAuthAttempting(false);
                    return;
                  }
                  
                  // Transfer tokens to admin format
                  localStorage.setItem('admin_access_token', token);
                  localStorage.setItem('admin_refresh_token', refreshToken);
                  localStorage.setItem('pine_time_direct_auth', 'true');
                  setMessage('Access granted, redirecting to dashboard...');
                  
                  // Clean up the one-time auth key
                  sessionStorage.removeItem(oneTimeAuthKey);
                  
                  // Use the login method with existing token
                  addDebug('Logging in with existing token');
                  const loginSuccess = await login('', '', true);
                  addDebug(`Login with existing token result: ${loginSuccess}`);
                  
                  // Use auth state to track the authentication progress
                  // Updated timing with logging
                  await new Promise(resolve => setTimeout(resolve, 500));
                  
                  setAuthAttempting(false);
                  
                  // Go to dashboard
                  if (isAuthenticated) {
                    addDebug('Authentication confirmed, redirecting to dashboard');
                    navigate('/dashboard', { replace: true });
                  } else {
                    // Check auth state to provide better feedback
                    addDebug(`Authentication state: ${JSON.stringify({
                      isAuthenticated,
                      error: authState.error,
                      isInitialized: authState.isInitialized,
                      isValidating: authState.isValidating
                    })}`);
                    
                    if (authState.error) {
                      setError(`Authentication failed: ${authState.error}`);
                    } else {
                      setError('Authentication failed. Please try logging in directly.');
                    }
                  }
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
        
        addDebug(`Main token exists: ${!!mainToken}`);
        addDebug(`Admin token exists: ${!!adminToken}`);
        
        // Try to check current authentication first
        addDebug('Trying direct authentication check');
        const authResult = await checkAuth();
        addDebug(`Auth check result: ${authResult}`);
        
        if (authResult === true) {
          setMessage('Already authenticated, redirecting to dashboard...');
          navigate('/dashboard', { replace: true });
          return;
        }
        
        // Try with main app tokens as last resort
        if (mainToken && mainRefreshToken) {
          addDebug('Trying with main app tokens');
          
          // Transfer main tokens to admin format
          localStorage.setItem('admin_access_token', mainToken);
          localStorage.setItem('admin_refresh_token', mainRefreshToken);
          
          // Check authentication again
          const mainTokenResult = await checkAuth();
          addDebug(`Main token auth result: ${mainTokenResult}`);
          
          if (mainTokenResult === true) {
            navigate('/dashboard', { replace: true });
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
  }, [navigate, checkAuth, login, isAuthenticated, authState]);
  
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
            Debug Information
          </Typography>
          <ul className="debug-logs">
            {debug.map((msg, index) => (
              <li key={index}>{msg}</li>
            ))}
          </ul>
          <Box sx={{ mt: 2 }}>
            <Typography variant="caption">Auth Status: {isAuthenticated ? 'Authenticated' : 'Not Authenticated'}</Typography>
            <br />
            <Typography variant="caption">Auth State: {authState.isInitialized ? 'Initialized' : 'Not Initialized'}, 
                                          {authState.isValidating ? 'Validating' : 'Not Validating'}</Typography>
            {authState.error && (
              <Typography variant="caption" color="error">
                <br />Auth Error: {authState.error}
              </Typography>
            )}
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
              onClick={async () => {
                try {
                  setError(null);
                  setMessage('Attempting to login directly...');
                  const result = await checkAuth();
                  if (result === true) {
                    navigate('/dashboard');
                  } else {
                    navigate('/login');
                  }
                } catch (error) {
                  console.error('Authentication retry failed:', error);
                  setError(`Authentication retry failed: ${(error as Error).message}`);
                  navigate('/login');
                }
              }}
            >
              Try Again
            </Button>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default TransitionPage;
