import React, { createContext, useContext, useState, useEffect } from 'react';
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

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  checkAuth: () => boolean;
}

// Default context value
const defaultContext: AuthContextType = {
  user: null,
  isAuthenticated: false,
  isAdmin: false,
  login: async () => false,
  logout: () => {},
  checkAuth: () => false,
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
  const navigate = useNavigate();

  // Parse token and extract user information
  const parseToken = (token: string): User | null => {
    try {
      const decoded = jwtDecode<DecodedToken>(token);
      
      // Check if token is expired
      const currentTime = Date.now() / 1000;
      if (decoded.exp < currentTime) {
        console.warn('Token expired');
        return null;
      }
      
      // Extract user information from token
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
      return null;
    }
  };

  // Check authentication on initial load
  useEffect(() => {
    checkAuth();
  }, []);

  // Check if the user is authenticated
  const checkAuth = (): boolean => {
    const token = localStorage.getItem('admin_access_token');
    if (!token) {
      setIsAuthenticated(false);
      setUser(null);
      setIsAdmin(false);
      return false;
    }
    
    const userData = parseToken(token);
    if (!userData) {
      // Token invalid or expired
      localStorage.removeItem('admin_access_token');
      localStorage.removeItem('admin_refresh_token');
      setIsAuthenticated(false);
      setUser(null);
      setIsAdmin(false);
      return false;
    }
    
    // Valid token, update state
    setUser(userData);
    setIsAuthenticated(true);
    
    // Check admin status
    const isUserAdmin = userData.is_superuser || userData.role === 'admin';
    setIsAdmin(isUserAdmin);
    
    // If not admin, log them out from admin dashboard
    if (!isUserAdmin) {
      console.warn('User is not an admin');
      logout();
      return false;
    }
    
    return true;
  };

  // Login function
  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const response = await api.post('/login/access-token', 
        new URLSearchParams({
          username: email,
          password: password,
        }), 
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );
      
      const { access_token, refresh_token } = response.data;
      
      // Store tokens securely
      localStorage.setItem('admin_access_token', access_token);
      localStorage.setItem('admin_refresh_token', refresh_token);
      
      // Verify token and extract user data
      const userData = parseToken(access_token);
      if (!userData) {
        console.error('Invalid token received from server');
        return false;
      }
      
      // Check if user is admin
      if (!userData.is_superuser && userData.role !== 'admin') {
        console.error('User does not have admin privileges');
        localStorage.removeItem('admin_access_token');
        localStorage.removeItem('admin_refresh_token');
        return false;
      }
      
      // Set user data
      setUser(userData);
      setIsAuthenticated(true);
      setIsAdmin(true);
      
      return true;
    } catch (error: any) {
      console.error('Login failed:', error.response?.data || error);
      return false;
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('admin_access_token');
    localStorage.removeItem('admin_refresh_token');
    setUser(null);
    setIsAuthenticated(false);
    setIsAdmin(false);
    navigate('/login');
  };

  // Context value
  const contextValue: AuthContextType = {
    user,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
