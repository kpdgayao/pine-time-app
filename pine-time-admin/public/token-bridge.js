/**
 * Pine Time Admin Dashboard - Cross-Domain Token Bridge
 * Handles authentication token transfer between domains
 * Follows Pine Time error handling standards with proper validation and graceful degradation
 */

(function() {
  // Run this script as early as possible
  console.log('Token bridge initializing');
  
  // Check URL parameters for token
  const urlParams = new URLSearchParams(window.location.search);
  const tokenFromUrl = urlParams.get('token');
  
  // If token exists in URL, store it and clean URL
  if (tokenFromUrl) {
    try {
      console.log('Token received via URL parameter');
      localStorage.setItem('access_token', tokenFromUrl);
      
      // Remove token from URL to prevent security issues
      window.history.replaceState({}, document.title, window.location.pathname);
    } catch (err) {
      console.error('Error storing token from URL:', err);
    }
  }
  
  // Check if we were redirected without token but with a message to check localStorage
  const checkStorage = urlParams.get('check_storage');
  if (checkStorage === 'true') {
    const accessToken = localStorage.getItem('access_token');
    const adminToken = localStorage.getItem('admin_token');
    
    // If no tokens are available, we're truly unauthenticated
    if (!accessToken && !adminToken) {
      console.error('No authentication tokens found in storage');
      
      // Redirect to login if no authentication tokens are available
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    } else {
      console.log('Token found in localStorage, authentication should succeed');
    }
  }
})();
