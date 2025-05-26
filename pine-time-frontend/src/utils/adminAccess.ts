/**
 * Admin Dashboard Access Utility
 * 
 * Provides functionality to seamlessly transfer authentication
 * from the main frontend to the admin dashboard.
 * 
 * This utility follows Pine Time's error handling guidelines with proper
 * validation, fallback mechanisms, and clear error messaging.
 */

import { jwtDecode, JwtPayload } from 'jwt-decode';

// Pine Time custom JWT payload type
interface PineTimeJwtPayload extends JwtPayload {
  is_superuser?: boolean;
  user_type?: string;
  sub: string;
  email?: string;
  username?: string;
  role?: string;
}

/**
 * Opens the admin dashboard and transfers the current authentication tokens
 * using the simplest possible approach to avoid token transfer issues
 * 
 * @returns {boolean} True if the transfer was successful, false otherwise
 */
export const openAdminDashboard = (): boolean => {
  try {
    // Get tokens from main frontend storage
    const token = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    
    // Validate tokens exist
    if (!token || !refreshToken) {
      console.log('No authentication tokens found, redirecting to login');
      // No tokens found, need to login via main app first
      const isDev = import.meta.env.DEV;
      const loginUrl = isDev 
        ? 'http://localhost:5173/login?admin=true' 
        : '/login?admin=true';
      
      window.location.href = loginUrl;
      return false;
    }
    
    // Validate we have the current user information and admin privileges
    try {
      // Try to decode the token
      const currentUser = jwtDecode<PineTimeJwtPayload>(token);
      
      // Check if user has admin privileges
      const isAdmin = currentUser.is_superuser || 
                      currentUser.user_type === 'admin' || 
                      currentUser.role === 'admin';
                      
      if (!isAdmin) {
        console.error('User does not have admin privileges');
        alert('Your account does not have admin privileges');
        return false;
      }
      
      console.log('User has admin privileges, proceeding with token transfer');
    } catch (e) {
      console.error('Failed to decode token:', e);
      return false;
    }
    
    // SIMPLIFIED APPROACH: Create a special one-time auth token that will be valid for 30 seconds
    const authTimestamp = Date.now();
    const oneTimeAuthKey = `pine_auth_${authTimestamp}`;
    
    // Store this special key in sessionStorage (more temporary than localStorage)
    sessionStorage.setItem(oneTimeAuthKey, JSON.stringify({
      accessToken: token,
      refreshToken: refreshToken,
      timestamp: authTimestamp,
      expires: authTimestamp + (30 * 1000) // 30 seconds
    }));
    
    // Determine admin dashboard URL based on environment and pass the auth key
    const isDev = import.meta.env.DEV;
    const adminUrl = isDev 
      ? `http://localhost:5174/transition?auth=${oneTimeAuthKey}` 
      : `/admin/transition?auth=${oneTimeAuthKey}`;
    
    console.log('Navigating to admin dashboard with one-time auth key');
    
    // Navigate to admin dashboard using the transition page with the auth key
    window.location.href = adminUrl;
    return true;
  } catch (error) {
    console.error('Failed to open admin dashboard:', error);
    return false;
  }
};

/**
 * Checks if the current user has admin privileges
 * 
 * @param {any} user The user object from auth context
 * @returns {boolean} True if the user has admin privileges
 */
export const hasAdminAccess = (user: any): boolean => {
  if (!user) return false;
  
  return Boolean(
    user.is_superuser || 
    user.user_type === 'admin' || 
    user.role === 'admin'
  );
};
