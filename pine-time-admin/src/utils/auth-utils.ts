/**
 * Authentication utilities for Pine Time Admin Dashboard
 * Handles token management and cross-domain authentication
 */

import { API_BASE_URL } from '../config';

/**
 * Get authentication token from various storage locations
 * Supports cross-domain token sharing
 * 
 * @returns {string|null} Authentication token or null if not found
 */
export const getAuthToken = (): string | null => {
  // Try multiple token locations to support cross-domain authentication
  const possibleTokens = [
    localStorage.getItem('access_token'),
    localStorage.getItem('admin_token'),
    sessionStorage.getItem('access_token')
  ];
  
  // Return the first valid token found
  return possibleTokens.find(token => token !== null) || null;
};

/**
 * Set authentication token in all relevant storage locations
 * 
 * @param {string} token - JWT authentication token
 */
export const setAuthToken = (token: string): void => {
  localStorage.setItem('access_token', token);
  localStorage.setItem('admin_token', token);
};

/**
 * Clear all authentication tokens
 */
export const clearAuthTokens = (): void => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('admin_token');
  sessionStorage.removeItem('access_token');
};

/**
 * Validate if token is still valid
 * 
 * @param {string} token - JWT token to validate
 * @returns {Promise<boolean>} True if token is valid
 */
export const validateToken = async (token: string): Promise<boolean> => {
  try {
    // Create AbortController for timeout functionality
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout per Pine Time standards
    
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/validate`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    return response.status === 200;
  } catch (error) {
    // Comprehensive error handling per Pine Time standards
    if (error instanceof DOMException && error.name === 'AbortError') {
      console.error('Token validation timeout - server not responding within time limit');
    } else {
      console.error('Token validation error:', error);
    }
    
    // Implement graceful degradation when services are unavailable
    // For auth checks, we should fail safely by treating as unauthenticated
    return false;
  }
};

/**
 * Check if user is authenticated
 * 
 * @returns {boolean} True if user has valid authentication token
 */
export const isAuthenticated = (): boolean => {
  const token = getAuthToken();
  return token !== null;
};

/**
 * Set up token refresh mechanism
 * Should be called once when application initializes
 */
export const setupTokenRefresh = (): void => {
  // Check token validity every 5 minutes
  setInterval(async () => {
    const token = getAuthToken();
    
    if (token) {
      const isValid = await validateToken(token);
      
      if (!isValid) {
        // Token is invalid, redirect to login
        window.location.href = '/login';
      }
    }
  }, 5 * 60 * 1000); // 5 minutes
};
