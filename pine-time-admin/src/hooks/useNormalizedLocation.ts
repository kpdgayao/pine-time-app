import { useLocation } from 'react-router-dom';

/**
 * Custom hook that normalizes the location pathname for consistent path handling
 * across different environments (development and production).
 * 
 * This helps with route matching when the app is deployed to a subdirectory
 * like /admin/ but uses HashRouter for navigation.
 */
export function useNormalizedLocation() {
  const location = useLocation();
  
  // Remove any potential /admin/ prefix from the pathname
  // This handles cases where the app is deployed to a subdirectory
  const normalizedPathname = location.pathname.replace(/^\/admin\//, '/');
  
  // Log detailed path information for debugging purposes
  if (process.env.NODE_ENV === 'development') {
    console.log('Original location:', location);
    console.log('Normalized pathname:', normalizedPathname);
  }
  
  return {
    ...location,
    pathname: normalizedPathname,
  };
}

export default useNormalizedLocation;
