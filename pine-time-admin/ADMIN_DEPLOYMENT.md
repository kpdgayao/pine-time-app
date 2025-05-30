# Pine Time Admin Dashboard Deployment Guide

## Updated Configuration for Subdirectory Deployment

This document provides instructions for deploying the Pine Time Admin Dashboard in the `/admin` subdirectory with proper routing.

## Critical Configuration Components

### 1. React Router Configuration

```typescript
// in main.tsx
import { BrowserRouter } from 'react-router-dom'

// CRITICAL: basename must be '/admin' for subdirectory deployment
const basename = '/admin';

<BrowserRouter basename={basename}>
  <App />
</BrowserRouter>
```

### 2. Route Structure

All routes must use leading slashes:

```typescript
// in App.tsx
<Routes>
  <Route path="/login" element={<LoginPage />} />
  <Route path="/" element={/* root content */} />
  <Route path="/dashboard" element={<DashboardPage />} />
  <Route path="/users" element={<UsersPage />} />
  {/* other routes */}
</Routes>
```

### 3. AWS Amplify Rewrites and Redirects

In AWS Amplify Console, the following rules MUST be added in this exact order:

```
1. Source: /admin
   Target: /admin/
   Type: 301 Redirect

2. Source: /admin/<*>
   Target: /admin/index.html
   Type: 200 Rewrite
```

## Deployment Process

### 1. Build Configuration

The build process is handled in `amplify.yml`:
- Build main frontend app
- Build admin dashboard with correct base path
- Copy admin dashboard build to `dist/admin/` directory

### 2. Verification Steps

After deployment, verify:

1. **Router Debug Information**:
   - Check console for: `basename: '/admin'`
   - When at `/admin/`, `currentPath` should show `/`

2. **URL Patterns**:
   - `/admin` should redirect to `/admin/` (with trailing slash)
   - `/admin/` should load the dashboard or login page
   - `/admin/dashboard` should load the dashboard page
   - Browser refresh should work on all routes

3. **Assets**:
   - All assets should load from `/admin/assets/...`

## Troubleshooting

### Common Issues

1. **Blank Page with "No routes matched location "/admin""**:
   - Check that basename is set to '/admin' in main.tsx
   - Verify AWS Amplify rewrite rules are in the correct order

2. **Assets Not Loading**:
   - Verify that vite.config.ts has `base: '/admin/'` for production

3. **AWS Amplify Cache Issues**:
   - Clear the AWS Amplify cache in the console
   - Trigger a new build and deploy

4. **Missing Trailing Slash Redirect**:
   - Ensure the first rewrite rule redirects `/admin` → `/admin/`

If issues persist after trying these solutions, consider deploying to a subdomain (admin.pinetimeapp.com) instead of a subdirectory for simpler routing.
