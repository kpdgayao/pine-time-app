# Pine Time API Configuration Guide

## Overview

This document explains the API configuration pattern used in the Pine Time application to prevent duplicate API prefixes and ensure consistent API requests across environments.

## Key Configuration Principles

### 1. Backend Configuration

- The FastAPI backend already includes the `/api/v1` prefix in its routes
- This is configured in `app/core/config.py` with `API_V1_STR: str = "/api/v1"`
- The API router is included with this prefix: `app.include_router(api_router, prefix=settings.API_V1_STR)`

### 2. Frontend Configuration

- The frontend configuration in `src/config.ts` sets `API_PREFIX = ''` (empty string)
- This prevents adding a duplicate prefix to API requests
- The `getApiPath` function in `src/utils/api.ts` handles path normalization

### 3. API URL Construction

- Base URL (e.g., `http://localhost:8000` for development, `https://api.pinetimeapp.com` for production)
- API paths in component requests should NOT include `/api/v1` as it's added by the backend
- Example correct usage: `api.get('/events/types')` → makes request to `/api/v1/events/types`

### 4. Environment-based Configuration

- Development environment uses `.env` files with `VITE_API_BASE_URL`
- Production environment uses the hardcoded values in `config.ts`
- The configuration automatically detects the environment using `import.meta.env.DEV`

## Common Issues to Avoid

- Never set `API_PREFIX = '/api/v1'` in the frontend config
- Don't include `/api/v1` in API request paths in components
- When adding new API endpoints, follow the existing pattern
- Avoid direct axios usage in components; always use the shared API instance with interceptors

## Path Handling Function

The `getApiPath` function in `src/utils/api.ts` handles path construction:

```typescript
const getApiPath = (path: string): string => {
  // Remove leading slash if present
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  
  // Check if path already includes the API prefix
  if (cleanPath.startsWith('api/v1/') || cleanPath.startsWith('api/v1')) {
    // Path already has API prefix - this is an error case we need to fix
    const fixedPath = cleanPath.replace(/^api\/v1\/?/, '');
    console.warn(`Path '${path}' contains API prefix which may cause duplicate prefixes. Fixed to '/${fixedPath}'`);
    return `/${fixedPath}`;
  } else {
    // Path needs API prefix added (which is empty string as per config)
    // Just return the path with a leading slash
    return `/${cleanPath}`;
  }
};
```

## API Instances

The application uses two API instances:

- Standard instance: `api` with `DEFAULT_TIMEOUT` (10000ms)
- Extended instance: `apiLongTimeout` with `EXTENDED_TIMEOUT` (30000ms)
- Both have `withCredentials: true` for proper authentication handling

## Common API Endpoints

- Authentication: `/login/access-token`, `/login/refresh-token`
- Users: `/users/me`
- Events: `/events/`, `/events/types`, `/events/price-range`, `/events/${eventId}/register`
- Registrations: `/registrations/users/me/registrations`, `/registrations/events/${eventId}/register`
- Payments: `/payments/payments/register`, `/payments/users/${userId}/payments`

## Troubleshooting

If API requests are failing with 404 errors, check:

1. That the API path does not include a duplicate `/api/v1` prefix
2. That the API base URL is correctly configured for the environment
3. That the API request is using the shared API instance with interceptors
4. That the API endpoint exists and is correctly spelled

## Production Deployment

For production deployment:

1. Ensure `config.ts` has the correct production API base URL (`https://api.pinetimeapp.com`)
2. Verify that `API_PREFIX = ''` to prevent duplicate prefixes
3. Test API connectivity with the production endpoint
4. Check console logs for any path warnings or errors
