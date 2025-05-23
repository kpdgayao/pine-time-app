import axios from "axios";
import type { AxiosRequestConfig, AxiosResponse } from "axios";
import { API_BASE_URL, DEFAULT_TIMEOUT, EXTENDED_TIMEOUT } from "../config";

// Helper to ensure consistent API path handling
const getApiPath = (path: string): string => {
  const isDev = import.meta.env.DEV;
  
  // For development with Vite proxy, we need to keep the /api/v1 prefix
  if (isDev) {
    // Ensure path starts with / for dev server proxy
    if (!path.startsWith('/')) {
      path = '/' + path;
    }
    
    // For login endpoints, ensure they're prefixed correctly
    if (path.includes('login') && !path.startsWith('/api/v1')) {
      return `/api/v1${path}`;
    }
    
    // Return the path as is (with leading slash) for dev mode
    return path;
  }
  
  // For production
  // Remove leading slash if present
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  
  // Check if path already includes the API prefix
  if (cleanPath.startsWith('api/v1/') || cleanPath.startsWith('api/v1')) {
    return `/${cleanPath}`; // Keep the prefix in production
  } else {
    // Add the API prefix in production
    return `/api/v1/${cleanPath}`;
  }
};

// Create API instance with default timeout
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: DEFAULT_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: true
});

// Create an Axios instance with extended timeout for operations that may take longer
const apiLongTimeout = axios.create({
  baseURL: API_BASE_URL,
  timeout: EXTENDED_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: true
});


const attachInterceptors = (instance: any) => {
  // Path handling interceptor
  instance.interceptors.request.use((config: AxiosRequestConfig) => {
    if (config.url) {
      config.url = getApiPath(config.url);
    }
    return config;
  });

  // JWT token interceptor
  instance.interceptors.request.use((config: any) => {
    const token = localStorage.getItem("admin_access_token");
    if (token) {
      config.headers = config.headers || {};
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  });
};

// Apply the interceptors to both API instances
attachInterceptors(api);
attachInterceptors(apiLongTimeout);

// Helper function for safe API calls with better error handling
export const safeApiCall = async <T>(apiCall: Promise<any> | null, fallbackValue: T): Promise<T> => {
  if (!apiCall) return fallbackValue;
  try {
    const response = await apiCall;
    // Handle case where response might not have data property
    return response?.data || fallbackValue;
  } catch (error: any) {
    console.error('API call failed:', error);
    
    // Enhanced error logging for debugging
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
      console.error('Response headers:', error.response.headers);
      
      // Add user-friendly error messages based on status code
      if (error.response.status === 401) {
        console.error('Authentication error: Please log in again');
      } else if (error.response.status === 403) {
        console.error('Permission denied: You do not have access to this resource');
      } else if (error.response.status === 404) {
        console.error('Resource not found: The requested data does not exist');
      } else if (error.response.status === 422) {
        console.error('Validation error: Please check your input data');
      } else if (error.response.status >= 500) {
        console.error('Server error: The server encountered an issue');
      }
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
        break; // Don't retry for other types of errors
      }
    }
  }
  
  // If we get here, all retries failed
  console.error('All API retry attempts failed:', lastError);
  return fallbackValue;
}

// Helper function to check if response is paginated
export const isPaginatedResponse = (data: any): boolean => {
  return data && typeof data === 'object' && 'items' in data && Array.isArray(data.items);
};

// Helper function to safely handle both paginated and non-paginated responses
export const extractItems = <T>(data: any, defaultValue: T[] = []): T[] => {
  if (!data) return defaultValue;
  
  if (isPaginatedResponse(data)) {
    // Handle paginated response with 'items' key
    return data.items || defaultValue;
  } else if (Array.isArray(data)) {
    // Handle direct array response
    return data;
  } else if (data && typeof data === 'object') {
    // Try to find other common container keys
    const possibleKeys = ['data', 'results', 'records', 'content'];
    for (const key of possibleKeys) {
      if (key in data && Array.isArray(data[key])) {
        return data[key];
      }
    }
  }
  
  // If we can't determine the structure, return the default
  return defaultValue;
};

// Export as a single module
export default api;
export { apiLongTimeout };
