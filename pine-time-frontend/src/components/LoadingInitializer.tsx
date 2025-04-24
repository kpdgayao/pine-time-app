import React, { useEffect } from 'react';
import { useLoading } from '../contexts/LoadingContext';
import { registerLoadingHandlers } from '../utils/api';

/**
 * Component that initializes the loading state handlers for the API client.
 * This component should be rendered once at the application root.
 */
const LoadingInitializer: React.FC = () => {
  const { setLoading, setLoadingMessage } = useLoading();
  
  useEffect(() => {
    // Register the loading handlers with the API client
    registerLoadingHandlers(setLoading, setLoadingMessage);
    
    // Log that the loading handlers have been initialized
    console.log('Loading handlers initialized');
    
    return () => {
      // Clean up is handled in the registerLoadingHandlers function
    };
  }, [setLoading, setLoadingMessage]);
  
  // This component doesn't render anything
  return null;
};

export default LoadingInitializer;
