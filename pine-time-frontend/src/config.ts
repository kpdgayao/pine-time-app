/**
 * Pine Time App configuration
 * Supports both local development and production environments
 *
 * IMPORTANT API CONFIGURATION NOTES:
 * - The backend FastAPI application already includes the '/api/v1' prefix in its routes
 * - This frontend configuration must NOT duplicate that prefix
 * - All API requests will automatically be routed to the correct endpoint
 * - Example: api.get('/events') will request http://localhost:8000/api/v1/events
 */

// Determine if in development mode
const isDevelopment = import.meta.env.DEV;

// Base URL for API requests - use environment variable for local development or fallback to production
export const API_BASE_URL = isDevelopment 
  ? import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  : 'https://api.pinetimeapp.com';

// Flag to determine if we're running on the main domain (pinetimeapp.com)
export const IS_MAIN_DOMAIN = !isDevelopment && 
  (typeof window !== 'undefined' && window.location.hostname === 'pinetimeapp.com');

// API version prefix
// Note: The backend already includes /api/v1 in its routes, so we keep this empty
export const API_PREFIX = '';

// Default request timeout in milliseconds
export const DEFAULT_TIMEOUT = 10000;

// Extended timeout for paginated endpoints
export const EXTENDED_TIMEOUT = 30000;

// Log environment mode
console.log(`Running in ${isDevelopment ? 'development' : 'production'} mode`);
console.log(`API URL: ${API_BASE_URL}/api/v1`);