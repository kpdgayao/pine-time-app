/**
 * Error handling utilities for the Pine Time admin dashboard.
 * Follows Pine Time's error handling guidelines with comprehensive approach.
 */

import { ApiError } from '../types/api';

/**
 * Create a standardized error object from API responses
 * @param error The error response from API
 * @returns Standardized ApiError object
 */
export const formatApiError = (error: any): ApiError => {
  if (error?.response?.data) {
    // Backend API error with standard structure
    const { status_code, detail, type, code } = error.response.data;
    return {
      status_code: status_code || error.response.status || 500,
      detail: detail || 'An unknown error occurred',
      type: type || 'api_error',
      code: code
    };
  } else if (error?.response) {
    // Error with response but non-standard structure
    return {
      status_code: error.response.status || 500,
      detail: error.response.statusText || 'An unknown error occurred',
      type: 'api_error'
    };
  } else if (error?.request) {
    // Error with no response (network error)
    return {
      status_code: 0,
      detail: 'Network error: Unable to reach the server',
      type: 'network_error'
    };
  } else if (error?.message) {
    // General JS error
    return {
      status_code: 500,
      detail: error.message,
      type: 'js_error'
    };
  }
  
  // Fallback for unknown errors
  return {
    status_code: 500,
    detail: 'An unknown error occurred',
    type: 'unknown_error'
  };
};

/**
 * Generate user-friendly error messages based on error type and status code
 * @param error ApiError object
 * @returns User-friendly error message
 */
export const getUserFriendlyErrorMessage = (error: ApiError): string => {
  // Handle specific status codes
  switch (error.status_code) {
    case 400:
      return 'Invalid request: Please check your input and try again';
    case 401:
      return 'Authentication required: Please log in to continue';
    case 403:
      return 'Permission denied: You do not have access to this resource';
    case 404:
      return 'Resource not found: The requested item does not exist';
    case 409:
      return 'Conflict: This operation conflicts with the current state';
    case 422:
      return 'Validation error: Please check your input data';
    case 429:
      return 'Too many requests: Please try again later';
    case 0:
      return 'Network error: Please check your internet connection';
    default:
      if (error.status_code >= 500) {
        return 'Server error: Please try again later or contact support';
      }
      return error.detail || 'An unknown error occurred';
  }
};

/**
 * Log API errors with consistent format and severity levels
 * @param error The error to log
 * @param context Additional context information
 */
export const logApiError = (error: ApiError, context?: string): void => {
  const timestamp = new Date().toISOString();
  const contextMessage = context ? ` - Context: ${context}` : '';
  
  // Determine log level based on status code
  if (error.status_code >= 500) {
    console.error(`[${timestamp}] API ERROR (${error.status_code})${contextMessage}: ${error.detail}`);
  } else if (error.status_code >= 400) {
    console.warn(`[${timestamp}] API WARNING (${error.status_code})${contextMessage}: ${error.detail}`);
  } else {
    console.info(`[${timestamp}] API INFO (${error.status_code})${contextMessage}: ${error.detail}`);
  }
  
  // Log additional error details if available
  if (error.type || error.code) {
    console.debug(`[${timestamp}] API ERROR DETAILS - Type: ${error.type || 'unspecified'}, Code: ${error.code || 'unspecified'}`);
  }
};

/**
 * Create sample data for graceful degradation when API fails
 * @param type Type of sample data to generate
 * @param count Number of sample items to generate
 * @returns Sample data of the specified type
 */
export const generateSampleData = (type: string, count: number = 5): any[] => {
  switch (type) {
    case 'users':
      return Array(count).fill(0).map((_, i) => ({
        id: `sample-${i}`,
        username: `user${i}`,
        email: `user${i}@example.com`,
        full_name: `Sample User ${i}`,
        is_active: true,
        is_superuser: i === 0,
        created_at: new Date().toISOString(),
        role: i === 0 ? 'admin' : 'user',
        points: Math.floor(Math.random() * 1000)
      }));
    
    case 'events':
      return Array(count).fill(0).map((_, i) => ({
        id: `sample-${i}`,
        title: `Sample Event ${i}`,
        description: 'This is a sample event description for graceful degradation.',
        event_type: ['Workshop', 'Seminar', 'Game Night', 'Trivia Night', 'Conference'][i % 5],
        location: 'Baguio City',
        start_time: new Date(Date.now() + 86400000 * (i + 1)).toISOString(),
        end_time: new Date(Date.now() + 86400000 * (i + 1) + 7200000).toISOString(),
        max_participants: 50,
        current_participants: Math.floor(Math.random() * 30),
        points_reward: 100,
        status: ['active', 'draft', 'completed', 'cancelled'][i % 4],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }));
    
    case 'badges':
      return Array(count).fill(0).map((_, i) => ({
        id: `sample-${i}`,
        name: `Sample Badge ${i}`,
        description: 'This is a sample badge description.',
        category: ['events', 'social', 'achievements', 'special'][i % 4],
        level: (i % 5) + 1,
        requirements: 'Sample requirements for earning this badge.',
        points_reward: (i + 1) * 50,
        icon_url: null
      }));
    
    default:
      return Array(count).fill(0).map((_, i) => ({
        id: `sample-${i}`,
        name: `Sample Item ${i}`
      }));
  }
};

/**
 * Detect and determine if a response contains pagination
 * @param response The API response to check
 * @returns Whether the response is paginated
 */
export const isPaginatedResponse = (response: any): boolean => {
  return (
    response &&
    typeof response === 'object' &&
    'items' in response &&
    Array.isArray(response.items) &&
    'total' in response &&
    typeof response.total === 'number'
  );
};
