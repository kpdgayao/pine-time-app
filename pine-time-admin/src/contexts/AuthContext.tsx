import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { jwtDecode } from 'jwt-decode';
import api from '../api/client';
import { useNavigate } from 'react-router-dom';

// TypeScript interfaces for enhanced type safety
interface User {
  id: string;
  username: string;
  email: string;
  is_superuser: boolean;
  role: string;
  full_name?: string;
}

interface DecodedToken {
  sub: string;
  exp: number;
  role: string;
  is_superuser: boolean;
  [key: string]: any;
}

// Enhanced auth state tracking
interface AuthState {
  isInitialized: boolean;
  isValidating: boolean;
  error: string | null;
  lastChecked: number | null;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  authState: AuthState;
  login: (email: string, password: string, useExistingToken?: boolean) => Promise<boolean>;
  logout: () => void;
  checkAuth: () => Promise<boolean>;
  refreshTokens: () => Promise<boolean>;
}

// Default context value
const defaultContext: AuthContextType = {
  user: null,
  isAuthenticated: false,
  isAdmin: false,
  authState: {
    isInitialized: false,
    isValidating: false,
    error: null,
    lastChecked: null
  },
  login: async () => false,
  logout: () => {},
  checkAuth: async () => false,
  refreshTokens: async () => false,
};

// Create context
const AuthContext = createContext<AuthContextType>(defaultContext);

// Custom hook for using auth context
export const useAuth = () => useContext(AuthContext);

// Auth provider component
export const AuthProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  const [authState, setAuthState] = useState<AuthState>({
    isInitialized: false,
    isValidating: true,
    error: null,
    lastChecked: null
  });
  const navigate = useNavigate();

  // Parse token and extract user information with enhanced validation
  const parseToken = useCallback((token: string): User | null => {
    try {
      if (!token || typeof token !== 'string' || token.length < 10) {
        console.warn('Invalid token format');
        setAuthState(prev => ({...prev, error: 'Invalid token format'}));
        return null;
      }

      const decoded = jwtDecode<DecodedToken>(token);
      
      // Check if token is expired with more detailed logging
      const currentTime = Date.now() / 1000;
      if (!decoded.exp) {
        console.warn('Token missing expiration');
        setAuthState(prev => ({...prev, error: 'Token is missing expiration date'}));
        return null;
      }
      
      if (decoded.exp < currentTime) {
        const expiredAgo = Math.round(currentTime - decoded.exp);
        console.warn(`Token expired ${expiredAgo} seconds ago`);
        setAuthState(prev => ({...prev, error: `Token expired ${expiredAgo} seconds ago`}));
        return null;
      }
      
      // Validate required fields
      if (!decoded.sub) {
        console.warn('Token missing subject (user ID)');
        setAuthState(prev => ({...prev, error: 'Token missing user ID'}));
        return null;
      }
      
      // Extract user information from token with defaults for missing fields
      return {
        id: decoded.sub,
        username: decoded.username || '',
        email: decoded.email || '',
        is_superuser: decoded.is_superuser || false,
        role: decoded.role || 'user',
        full_name: decoded.full_name,
      };
    } catch (error) {
      console.error('Failed to parse token:', error);
      setAuthState(prev => ({...prev, error: `Token parsing error: ${(error as Error).message}`}));
      return null;
    }
  }, []);

  // Token refresh with retry logic and timeout
  const refreshTokens = useCallback(async (retry = 3): Promise<boolean> => {
    try {
      setAuthState(prev => ({ ...prev, isValidating: true, error: null }));
      console.log('Attempting to refresh tokens...');
      
      const refreshToken = localStorage.getItem('admin_refresh_token');
      if (!refreshToken) {
        console.warn('No refresh token available');
        setAuthState(prev => ({
          ...prev,
          isValidating: false,
          error: 'No refresh token available',
          lastChecked: Date.now()
        }));
        return false;
      }
      
      // Create a timeout promise to ensure we don't wait forever
      const timeoutPromise = new Promise<{data: null; timedOut: true; error?: any}>((resolve) => {
        setTimeout(() => resolve({data: null, timedOut: true}), 8000);
      });
      
      // Create the actual refresh request
      const refreshPromise = api.post('/login/refresh-token', { refresh_token: refreshToken })
        .then(response => ({data: response.data, timedOut: false, error: null}))
        .catch(error => {
          console.error('Token refresh request failed:', error.message);
          return {data: null, timedOut: false, error};
        });
      
      // Race the timeout against the actual request
      const result = await Promise.race([timeoutPromise, refreshPromise]);
      
      if (result.timedOut) {
        console.warn('Token refresh timed out');
        setAuthState(prev => ({
          ...prev,
          isValidating: false,
          error: 'Token refresh timed out',
          lastChecked: Date.now()
        }));
        
        // Retry if we have attempts left
        if (retry > 0) {
          console.log(`Retrying token refresh (${retry} attempts left)`);
          return refreshTokens(retry - 1);
        }
        
        return false;
      }
      
      if (!result.data) {
        console.warn('Token refresh failed');
        setAuthState(prev => ({
          ...prev,
          isValidating: false,
          error: result.error ? `Token refresh error: ${result.error.message}` : 'Token refresh failed',
          lastChecked: Date.now()
        }));
        
        // Retry if we have attempts left
        if (retry > 0 && result.error) {
          console.log(`Retrying token refresh (${retry} attempts left)`);
          return refreshTokens(retry - 1);
        }
        
        return false;
      }
      
      // Store the new tokens
      localStorage.setItem('admin_access_token', result.data.access_token);
      localStorage.setItem('admin_refresh_token', result.data.refresh_token);
      
      // Parse the new token and update user information
      const userInfo = parseToken(result.data.access_token);
      if (userInfo) {
        setUser(userInfo);
        setIsAuthenticated(true);
        setIsAdmin(userInfo.is_superuser || userInfo.role === 'admin');
        setAuthState({
          isInitialized: true,
          isValidating: false,
          error: null,
          lastChecked: Date.now()
        });
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Token refresh failed:', error);
      setAuthState(prev => ({
        ...prev,
        isValidating: false,
        error: `Token refresh error: ${(error as Error).message}`,
        lastChecked: Date.now()
      }));
      return false;
    }
  }, [parseToken]);

  // Enhanced authentication check with proper initialization and error handling
  const checkAuth = useCallback(async (): Promise<boolean> => {
    try {
      console.log('Checking authentication...');
      setAuthState(prev => ({ ...prev, isValidating: true }));
      
      const token = localStorage.getItem('admin_access_token');
      if (!token) {
        console.log('No admin token found');
        setIsAuthenticated(false);
        setUser(null);
        setIsAdmin(false);
        setAuthState({
          isInitialized: true,
          isValidating: false,
          error: 'No authentication token found',
          lastChecked: Date.now()
        });
        return false;
      }
      
      // Parse and validate the token
      try {
        const decoded = jwtDecode<DecodedToken>(token);
        const isExpired = decoded.exp ? decoded.exp * 1000 < Date.now() : true;
        
        if (isExpired) {
          console.log('Token expired, attempting refresh...');
          const refreshSuccessful = await refreshTokens();
          
          if (!refreshSuccessful) {
            console.warn('Token refresh failed');
            setIsAuthenticated(false);
            setUser(null);
            setIsAdmin(false);
            return false;
          }
          
          // If refresh was successful, we already updated the state
          return true;
        }
        
        // If the token is valid, extract user info
        const userInfo = parseToken(token);
        if (userInfo) {
          setUser(userInfo);
          setIsAuthenticated(true);
          setIsAdmin(userInfo.is_superuser || userInfo.role === 'admin');
          setAuthState({
            isInitialized: true,
            isValidating: false,
            error: null,
            lastChecked: Date.now()
          });
          return true;
        }
      } catch (error) {
        console.error('Error parsing token:', error);
        setAuthState(prev => ({
          ...prev,
          isInitialized: true,
          isValidating: false,
          error: `Error parsing token: ${(error as Error).message}`,
          lastChecked: Date.now()
        }));
      }
      
      // If we got here, authentication failed
      setIsAuthenticated(false);
      setUser(null);
      setIsAdmin(false);
      return false;
    } catch (error) {
      console.error('Authentication check failed:', error);
      setIsAuthenticated(false);
      setUser(null);
      setIsAdmin(false);
      setAuthState({
        isInitialized: true,
        isValidating: false,
        error: `Authentication error: ${(error as Error).message}`,
        lastChecked: Date.now()
      });
      return false;
    }
  }, [parseToken, refreshTokens]);

  // Login function with enhanced error handling
  const login = useCallback(async (email: string, password: string, useExistingToken = false): Promise<boolean> => {
    try {
      setAuthState(prev => ({ ...prev, isValidating: true, error: null }));
      
      if (useExistingToken) {
        console.log('Using existing token for login');
        return await checkAuth();
      }
      
      console.log('Logging in with credentials...');
      const response = await api.post('/login/access-token', 
        new URLSearchParams({
          username: email,
          password: password
        }), 
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          timeout: 10000 // 10 seconds timeout
        }
      );
      
      if (response.data && response.data.access_token) {
        // Store tokens
        localStorage.setItem('admin_access_token', response.data.access_token);
        localStorage.setItem('admin_refresh_token', response.data.refresh_token || '');
        
        // Process user info
        const userInfo = parseToken(response.data.access_token);
        if (userInfo) {
          // Check if user has admin privileges
          const isAdminUser = userInfo.is_superuser || userInfo.role === 'admin';
          if (!isAdminUser) {
            console.warn('User does not have admin privileges');
            setAuthState(prev => ({
              ...prev,
              isInitialized: true,
              isValidating: false,
              error: 'Your account does not have admin privileges',
              lastChecked: Date.now()
            }));
            return false;
          }
          
          setUser(userInfo);
          setIsAuthenticated(true);
          setIsAdmin(true);
          setAuthState({
            isInitialized: true,
            isValidating: false,
            error: null,
            lastChecked: Date.now()
          });
          return true;
        }
      }
      
      console.warn('Login failed - invalid response');
      setAuthState(prev => ({
        ...prev,
        isValidating: false,
        error: 'Login failed. Please check your credentials.',
        lastChecked: Date.now()
      }));
      return false;
    } catch (error: any) {
      console.error('Login error:', error);
      let errorMessage = 'Login failed';
      
      if (error.response) {
        // Server responded with an error
        if (error.response.status === 401) {
          errorMessage = 'Invalid credentials';
        } else if (error.response.status === 422) {
          errorMessage = 'Invalid email or password format';
        } else if (error.response.status >= 500) {
          errorMessage = 'Server error. Please try again later.';
        } else if (error.response.data && error.response.data.detail) {
          errorMessage = error.response.data.detail;
        }
      } else if (error.request) {
        // Request made but no response received
        errorMessage = 'No response from server. Please check your connection.';
      }
      
      setAuthState(prev => ({
        ...prev,
        isValidating: false,
        error: errorMessage,
        lastChecked: Date.now()
      }));
      return false;
    }
  }, [checkAuth, parseToken]);

  // Logout function
  const logout = useCallback(() => {
    // Clear tokens
    localStorage.removeItem('admin_access_token');
    localStorage.removeItem('admin_refresh_token');
    
    // Reset state
    setUser(null);
    setIsAuthenticated(false);
    setIsAdmin(false);
    setAuthState({
      isInitialized: true,
      isValidating: false,
      error: null,
      lastChecked: Date.now()
    });
    
    // Redirect to login
    navigate('/login');
    console.log('Logged out successfully');
  }, [navigate]);

  // Check authentication on initial load with comprehensive error handling
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        console.log('Initializing authentication state...');
        
        // First, check for tokens transferred from the main app
        const mainToken = localStorage.getItem('access_token');
        const mainRefreshToken = localStorage.getItem('refresh_token');
        const directAuthFlag = localStorage.getItem('pine_time_direct_auth');
        
        // Clear the direct auth flag if it exists
        if (directAuthFlag) {
          localStorage.removeItem('pine_time_direct_auth');
        }
        
        // If tokens from main app exist, transfer them
        if (mainToken && mainRefreshToken) {
          console.log('Tokens found from main app, transferring...');
          localStorage.setItem('admin_access_token', mainToken);
          localStorage.setItem('admin_refresh_token', mainRefreshToken);
          
          // Also log the token status
          const userInfo = parseToken(mainToken);
          console.log('Token from main app is valid:', !!userInfo);
        }
        
        // Now check authentication with the enhanced method
        await checkAuth();
      } catch (error) {
        console.error('Error during authentication initialization:', error);
        setAuthState({
          isInitialized: true,
          isValidating: false,
          error: `Initialization error: ${(error as Error).message}`,
          lastChecked: Date.now()
        });
      }
    };
    
    // Run the initialization
    initializeAuth();
    
    // Setup a periodic token validation (every 5 minutes)
    const tokenValidationInterval = setInterval(() => {
      // Only validate if we're authenticated
      if (isAuthenticated) {
        console.log('Performing periodic token validation');
        checkAuth();
      }
    }, 5 * 60 * 1000);
    
    // Cleanup on unmount
    return () => {
      clearInterval(tokenValidationInterval);
    };
  }, [checkAuth, isAuthenticated, parseToken]);

  // Context value to expose to consumers
  const contextValue: AuthContextType = {
    user,
    isAuthenticated,
    isAdmin,
    authState,
    login,
    logout,
    checkAuth,
    refreshTokens
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
