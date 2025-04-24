import axios, { AxiosRequestConfig, AxiosResponse } from "axios";
import { useEffect } from "react";
import { useLoading } from "../contexts/LoadingContext";

// Create a loading state handler that can be used outside of React components
let setLoadingState: ((loading: boolean) => void) | null = null;
let setLoadingMessage: ((message: string | null) => void) | null = null;

// This function will be called by components to register the loading state handlers
export const registerLoadingHandlers = (
  setLoading: (loading: boolean) => void,
  setMessage: (message: string | null) => void
) => {
  setLoadingState = setLoading;
  setLoadingMessage = setMessage;
};

// Hook to register loading handlers automatically
export const useApiLoadingEffect = () => {
  const { setLoading, setLoadingMessage } = useLoading();
  
  useEffect(() => {
    registerLoadingHandlers(setLoading, setLoadingMessage);
    
    return () => {
      // Clear handlers when component unmounts - using function to avoid reassigning constants
      registerLoadingHandlers(
        () => {}, // Empty functions as placeholders
        () => {}
      );
    };
  }, [setLoading, setLoadingMessage]);
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // Default timeout of 10 seconds
  withCredentials: true, // Set to true if using cookies for auth, false for JWT in headers
});

// Create an instance with longer timeout for paginated endpoints
export const apiLongTimeout = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // Extended timeout of 30 seconds for paginated endpoints
  withCredentials: true,
});

// Attach JWT token to all API instances
const attachTokenInterceptor = (instance: any) => {
  instance.interceptors.request.use((config: any) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers = config.headers || {};
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  });
};

// Apply the interceptor to both API instances
attachTokenInterceptor(api);
attachTokenInterceptor(apiLongTimeout);

// Add request interceptor for loading states
api.interceptors.request.use(
  (config) => {
    // Start loading for all requests except those marked with skipLoading
    if (setLoadingState && !(config.headers?.skipLoading)) {
      setLoadingState(true);
      
      // Set a descriptive loading message based on the request
      if (setLoadingMessage) {
        const method = config.method?.toUpperCase() || 'GET';
        const url = config.url || '';
        // We can use the URL to create more specific messages if needed
        let message = `Loading data...`;
        
        if (method === 'GET') {
          message = `Fetching data...`;
        } else if (method === 'POST') {
          // Special handling for payment submissions
          if (url.includes('payments/register') || url.includes('payments/payments/register')) {
            message = `Processing payment...`;
          } else {
            message = `Saving data...`;
          }
        } else if (method === 'PUT' || method === 'PATCH') {
          message = `Updating data...`;
        } else if (method === 'DELETE') {
          message = `Deleting data...`;
        }
        
        setLoadingMessage(message);
      }
    }
    
    // Remove skipLoading from headers before sending
    if (config.headers?.skipLoading) {
      delete config.headers.skipLoading;
    }
    
    return config;
  },
  (error) => {
    // Stop loading on request error
    if (setLoadingState) {
      setLoadingState(false);
    }
    return Promise.reject(error);
  }
);

// Add response interceptor for loading states
api.interceptors.response.use(
  (response) => {
    // Stop loading on successful response
    if (setLoadingState) {
      setLoadingState(false);
      if (setLoadingMessage) {
        setLoadingMessage(null);
      }
    }
    return response;
  },
  (error) => {
    // Stop loading on response error
    if (setLoadingState) {
      setLoadingState(false);
      if (setLoadingMessage) {
        setLoadingMessage(null);
      }
    }
    return Promise.reject(error);
  }
);

// Helper function to create requests that don't trigger loading indicators
export const createSilentRequest = (config: AxiosRequestConfig) => {
  return {
    ...config,
    headers: {
      ...(config.headers || {}),
      skipLoading: true
    }
  };
};

// Helper function for safe API calls with better error handling
export const safeApiCall = async <T>(apiCall: Promise<AxiosResponse<T>>, fallbackValue: T): Promise<T> => {
  try {
    const response = await apiCall;
    return response.data;
  } catch (error: any) {
    console.error('API call failed:', error);
    
    // Enhanced error logging for debugging
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
      console.error('Response headers:', error.response.headers);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received:', error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Error message:', error.message);
    }
    
    return fallbackValue;
  }
};

// Helper function for retrying API calls that might timeout
export async function retryApiCall<T>(
  apiCallFn: () => Promise<AxiosResponse<T>>, 
  fallbackValue: T, 
  maxRetries: number = 2,
  retryDelay: number = 1000
): Promise<T> {
  let lastError;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      // Wait before retrying (except for first attempt)
      if (attempt > 0) {
        await new Promise(resolve => setTimeout(resolve, retryDelay * attempt));
        console.log(`Retry attempt ${attempt} for API call`);
      }
      
      const response = await apiCallFn();
      return response.data;
    } catch (error: any) {
      lastError = error;
      
      // Only retry on timeout or network errors
      if (
        error.code !== 'ECONNABORTED' && 
        !error.message?.includes('timeout') &&
        !error.message?.includes('Network Error')
      ) {
        break; // Don't retry other types of errors
      }
    }
  }
  
  console.error('API call failed after retries:', lastError);
  return fallbackValue;
};

export default api;
