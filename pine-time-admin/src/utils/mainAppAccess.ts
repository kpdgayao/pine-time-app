/**
 * Main App Access Utility
 * 
 * Provides functionality to navigate back to the main application
 * from the admin dashboard while preserving authentication.
 */

/**
 * Returns to the main frontend application
 * This preserves the authentication state by transferring tokens back if needed
 */
export const returnToMainApp = (): void => {
  try {
    // Get tokens from admin dashboard storage
    const token = localStorage.getItem('admin_access_token');
    const refreshToken = localStorage.getItem('admin_refresh_token');
    
    // Transfer tokens back to main app format if they exist
    if (token && refreshToken) {
      localStorage.setItem('access_token', token);
      localStorage.setItem('refresh_token', refreshToken);
    }
    
    // Determine main app URL based on environment with improved path handling
    const isDev = import.meta.env.DEV;
    const mainAppUrl = isDev 
      ? 'http://localhost:5173' 
      : '/';
      
    console.log('Returning to main app:', mainAppUrl);
    
    // Navigate to main app
    window.location.href = mainAppUrl;
  } catch (error) {
    console.error('Failed to return to main app:', error);
    // Fallback to base URL if there's an error
    window.location.href = '/';
  }
};
