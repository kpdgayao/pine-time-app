# Pine Time Admin Dashboard Deployment Guide

This document provides detailed instructions for deploying the Pine Time Admin Dashboard in a subdirectory (`/admin`) of the main application.

## Deployment Architecture

The Pine Time Admin Dashboard is deployed as part of the main application, with these key components:

- **Main Application**: Served from the root path (`/`)
- **Admin Dashboard**: Served from a subdirectory (`/admin/`)
- **Single AWS Amplify Deployment**: Both applications are deployed together

## Deployment Steps

### 1. Build Configuration

The build process is handled automatically in `amplify.yml` with these steps:
- Build main frontend app
- Build admin dashboard with base path `/admin/`
- Copy admin dashboard build to `dist/admin/` directory
- Copy `_redirects` file for proper SPA routing

### 2. AWS Amplify Configuration

After deployment, configure the following in the AWS Amplify Console:

1. Navigate to **AWS Amplify Console** → **App settings** → **Rewrites and redirects**
2. Add the following rules (order is important):

```
Source pattern: /admin
Target address: /admin/
Type: Redirect (301)

Source pattern: /admin/*
Target address: /admin/index.html
Type: Rewrite (200)
```

3. Save the configuration

### 3. Verification Steps

After deployment, verify the following:

1. **Asset Path Resolution**:
   - Check browser console for path resolution diagnostics
   - All assets should load from `/admin/assets/...`

2. **Navigation**:
   - Direct navigation to `/admin/dashboard` should work
   - Direct navigation to `/admin/users` should work
   - Refreshing any admin page should not result in 404 errors

3. **API Integration**:
   - API requests should be made to the correct endpoints
   - Authentication should work correctly

## Troubleshooting

If issues persist after deployment, check the following:

1. **Browser Console**:
   - Look for the enhanced debugging information
   - Check for any asset loading errors
   - Verify base URL configuration

2. **AWS Amplify Console**:
   - Verify build logs for any errors
   - Confirm rewrites and redirects are configured correctly

3. **Network Requests**:
   - Inspect network requests for 404 errors
   - Verify API requests are correctly routed

4. **Common Issues**:
   - 404 errors for routes: Check the rewrites and redirects configuration
   - Missing assets: Check the base path configuration in `vite.config.ts`
   - API errors: Verify API configuration and path handling
