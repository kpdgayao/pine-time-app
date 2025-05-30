# Pine Time Admin Dashboard - Subdomain Deployment Guide

## Overview

This guide outlines the process of deploying the Pine Time Admin Dashboard to a dedicated subdomain (`admin.pinetimeapp.com`) instead of a subdirectory (`pinetimeapp.com/admin`). This approach provides several benefits:

- Eliminates complex routing issues associated with subdirectory deployments
- Provides a clean separation between the main application and admin dashboard
- Simplifies routing configuration in React Router
- Improves security by isolating admin functionality

## Prerequisites

- AWS Account with access to Amplify and Route 53
- Domain registered in Route 53 or with access to DNS settings
- GitHub repository with Pine Time Admin code

## Step 1: DNS Configuration

### In AWS Route 53 (or your DNS provider):

1. Navigate to your hosted zone for `pinetimeapp.com`
2. Create a new CNAME record:
   - **Name**: `admin`
   - **Type**: `CNAME`
   - **Value**: The Amplify domain (will be provided after Amplify setup)
   - **TTL**: 300 seconds

## Step 2: Create a New AWS Amplify App

1. Log in to the AWS Management Console
2. Navigate to AWS Amplify
3. Click "New app" → "Host web app"
4. Choose GitHub as your repository source
5. Select your repository and branch
6. Configure build settings:
   ```yaml
   # Use the amplify.yml from the pine-time-admin directory
   baseDirectory: dist
   ```
7. Deploy the application

## Step 3: Configure Custom Domain in Amplify

1. After deployment, go to "Domain management" in the left sidebar
2. Click "Add domain"
3. Enter `pinetimeapp.com` as your domain
4. Add a subdomain prefix: `admin`
5. Follow the verification steps
6. Once verified, update your CNAME record with the provided Amplify domain if needed

## Step 4: Authentication Configuration

### Cross-Domain Authentication

Since the admin dashboard will now be on a different domain, you need to handle authentication:

1. **Token Sharing**:
   ```javascript
   // When logging in from main application
   localStorage.setItem('admin_token', token);
   
   // In the admin app
   const token = localStorage.getItem('admin_token') || localStorage.getItem('access_token');
   ```

2. **API Configuration**:
   - Ensure CORS is properly configured on the backend to allow requests from:
     - `https://pinetimeapp.com` 
     - `https://admin.pinetimeapp.com`
   - Update the API configuration to use absolute URLs for cross-domain requests

## Step 5: Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Check backend CORS configuration in FastAPI
   - Ensure all origins are properly whitelisted
   - Update `app/main.py` with the new subdomain

2. **Authentication Failures**:
   - Verify token sharing mechanism
   - Check browser console for token-related errors
   - Test local storage access across domains

3. **Routing Issues**:
   - Confirm all routes use leading slashes (`/dashboard`, `/users`, etc.)
   - Verify that basename is empty string for root domain routing

## Step 6: Maintenance

### Updating the Admin Dashboard

When making updates to the admin dashboard:

1. Make code changes
2. Commit and push to your repository
3. Amplify will automatically build and deploy the changes

### Monitoring

Monitor the admin dashboard for:

1. Performance metrics in AWS CloudWatch
2. Error rates in AWS CloudWatch
3. API integration issues

## Next Steps

After deploying to the subdomain:

1. Update main application links to point to the new subdomain
2. Verify all functionality works as expected
3. Consider implementing shared authentication with secure cookies if needed
