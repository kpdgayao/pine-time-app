# Pine Time Experience Baguio

> **Migration Note (May 2025):**
>
> The Pine Time application now features modern React frontends (Vite + TypeScript) for both end users and administrators. The legacy Streamlit admin dashboard has been replaced with a React-based implementation for improved performance and maintainability. All Streamlit files have been archived in `archive_old_dashboard/`. See below for updated setup instructions and project structure.

A web application for Pine Time Experience Baguio, a community that hosts trivia nights, murder mysteries, and game nights in Baguio City. The app connects locals with local businesses and artisans.

## Features

- **User Authentication**: Registration, login/logout with JWT token management
- **Event Management**: Create, discover, and register for events
- **Robust Payment System**: Database-driven payment tracking with step-based payment flow and comprehensive error handling
- **Enhanced Gamification System**: Comprehensive badge and points system with visual celebrations
- **Multi-level Badge System**: Bronze, silver, and gold badges across different categories with progress tracking
- **Points & Rewards**: Track points, view leaderboards, and earn rewards with detailed transaction history
- **Streak Tracking**: Rewards for consistent weekly attendance with visual indicators
- **Achievement Celebrations**: Visual celebrations when users earn new badges
- **Admin Dashboard**: Comprehensive tools for managing users, events, and analytics with seamless authentication from the main app
- **User Interface**: Mobile-friendly design with intuitive navigation
- **Demo Mode**: Test the application without backend connection
- **Enhanced Error Handling**: Robust error handling with graceful degradation
- **API Integration**: Resilient API client with response format handling
- **PostgreSQL Support**: Optimized for PostgreSQL with connection pooling

## Project Structure

```text
pine-time-app/
├── archive_old_dashboard/ # Archived Streamlit admin dashboard (legacy)
│   ├── pages/             # Dashboard page components (Streamlit)
│   ├── utils/             # Utility modules (auth, API, DB, connection)
│   ├── app.py             # Legacy admin dashboard entry point
│   └── user_app_postgres.py # Legacy user interface entry point
├── pine-time-admin/       # React-based admin dashboard (current)
│   ├── src/               # React source code for admin dashboard
│   │   ├── api/           # API clients and services
│   │   ├── components/    # Reusable UI components
│   │   ├── contexts/      # React contexts (Auth, Loading, etc.)
│   │   ├── pages/         # Page components organized by feature
│   │   ├── types/         # TypeScript interfaces and type definitions
│   │   ├── utils/         # Utility functions and helpers
│   │   ├── App.tsx        # Main application component
│   │   └── main.tsx       # Application entry point
│   └── vite.config.ts     # Vite configuration with proxy settings
├── app/                   # FastAPI backend
│   ├── api/               # API endpoints (all backend routes are prefixed with /api)
│   │   └── endpoints/     # API endpoint modules (events, users, gamification, etc.)
│   ├── core/              # Core functionality
│   ├── db/                # Database setup
│   ├── models/            # SQLAlchemy models (User, Event, UserBadge, EventAttendee, etc.)
│   ├── schemas/           # Pydantic schemas (request/response models)
│   ├── services/          # Business logic
│   │   ├── badge_manager.py  # Badge management service
│   │   └── points_manager.py # Points management service
│   └── main.py            # Backend entry point
├── pine-time-frontend/    # React frontend for users (Vite + TypeScript)
│   ├── src/               # React source code
│   │   ├── components/    # Reusable UI components
│   │   │   └── dashboard/ # Dashboard-specific components
│   │   ├── contexts/      # React contexts (Theme, Toast, etc.)
│   │   ├── pages/         # Page components
│   │   ├── theme/         # Theming system with light/dark mode
│   │   └── types/         # TypeScript type definitions
├── pine-time-proxy/       # Vercel proxy configuration for frontend-backend integration
│   └── vercel.json        # Proxy and CORS rules for API requests
```

---

## Vercel Proxy Configuration

The project uses a Vercel proxy (see `pine-time-proxy/vercel.json`) to securely connect the React frontend with the FastAPI backend, handling authentication and CORS headers correctly. **This is critical for production deployments and local development using Vercel.**

**Sample vercel.json:**

```json
{
  "version": 2,
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "http://pine-time-app-env-v2.eba-keu6sc2y.us-east-1.elasticbeanstalk.com/$1"
    }
  ],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Access-Control-Allow-Credentials", "value": "true" },
        { "key": "Access-Control-Allow-Origin", "value": "*" },
        { "key": "Access-Control-Allow-Methods", "value": "GET,OPTIONS,PATCH,DELETE,POST,PUT" },
        { "key": "Access-Control-Allow-Headers", "value": "X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization" }
      ]
    }
  ]
}
```

**Key Points:**

- The `destination` must match your backend route structure (do not add or omit `/api` unless your backend expects it).
- Explicit CORS headers are required to support JWT authentication and cross-origin requests.
- All frontend API calls should use `/api/...` as the base path.
- If you change your backend URL or route prefix, update `vercel.json` accordingly.

---

## Development Environment

- The `.venv/` directory is used for your local Python virtual environment. It should **never** be committed to Git and is now included in `.gitignore` by default.
- Always use `requirements.txt` (or `pyproject.toml`) to share dependencies, not the full environment.
- To set up a new environment, run:

```bash
python -m venv .venv
pip install -r requirements.txt
```

## Admin Dashboard Migration

The Pine Time Admin Dashboard has been completely migrated from Streamlit to React for improved performance, better user experience, and enhanced maintainability.

### Key Improvements

- **Performance**: Significantly faster page loads and transitions
- **User Experience**: More responsive UI with better navigation
- **Code Organization**: Feature-based directory structure
- **Type Safety**: Full TypeScript implementation with comprehensive interfaces
- **Error Handling**: Following Pine Time's established robust error handling patterns

### Admin Dashboard Setup

1. Navigate to the admin dashboard directory:

   ```bash
   cd pine-time-admin
   ```

2. Install dependencies:

   ```bash
   npm install --legacy-peer-deps
   ```

3. Start the development server:

   ```bash
   npm run dev
   ```

   The admin dashboard will be available at `http://localhost:5174`

4. Login with admin credentials to access the dashboard

### API Integration

The admin dashboard communicates with the backend API using a development proxy configuration in `vite.config.ts`, which handles CORS issues and properly routes API requests. The dashboard adheres to the Pine Time API path handling pattern, ensuring consistent communication with the backend.

## Production Deployment

The Pine Time application is deployed using AWS services with a custom domain (pinetimeapp.com) managed through Route 53.

### Frontend Deployment

- The React frontend is deployed on AWS Amplify with the custom domain pinetimeapp.com
- The frontend uses hardcoded production values in `src/config.ts` for production deployment
- SSL is managed through AWS Certificate Manager with a wildcard certificate (*.pinetimeapp.com)
- No environment variables are needed in production, simplifying deployment
- The API base URL is automatically set to `https://api.pinetimeapp.com` in production
- API prefix is intentionally set to an empty string to prevent duplicate prefixes

### Backend Deployment

- The FastAPI backend is deployed on AWS Elastic Beanstalk with the custom domain api.pinetimeapp.com
- The deployment package is created using the `create_deployment_zip.ps1` script
- Only essential files are included: `app/`, `.ebextensions/`, `.platform/`, `Procfile`, `requirements.txt`
- The resulting ZIP file is suitable for AWS Elastic Beanstalk and other Linux-based deployments
- Database connection to Neon PostgreSQL is configured via environment variables in `.ebextensions/04_environment.config`
- HTTPS is enabled through the Elastic Beanstalk load balancer with an AWS Certificate Manager certificate
- HTTP to HTTPS redirection is configured for security
- Ensure all paths in the ZIP file use forward slashes (/) for cross-platform compatibility

### Deployment Checklist

1. Update API configuration if needed (see API Configuration section)
2. Run comprehensive tests with `python run_comprehensive_tests.py`
3. Create deployment package with `./create_deployment_zip.ps1`
4. Deploy to production environment
5. Verify API connectivity and authentication
6. Check logs for any errors (`logs/app.log`)

## Tech Stack

- **Backend**: FastAPI (with all routes under `/api`) and SQLAlchemy ORM
- **Database**: PostgreSQL 17.4 (production), SQLite (development/testing)
- **Frontend**: React (Vite + TypeScript) for both user interface and admin dashboard
- **Proxy**: Vercel proxy for frontend-backend integration and CORS handling
- **React User Frontend**: Uses axios (with JWT auth), react-router-dom, jwt-decode, custom hooks, Material UI
- **React Admin Dashboard**: Uses Material UI v7, Recharts for visualization, and context-based state management
- **Authentication**: JWT-based auth system with refresh token logic and role-based access control
- **Payment System**: Context-based payment management with database integration and step-based payment flow
- **Error Handling**: Comprehensive error handling with graceful degradation across all components
- **Styling**: Custom theme system with light/dark mode support and Pine Time green theme (#2E7D32)
- **Gamification**: Badge and points system with progress tracking and visual celebrations
- **UI Components**: Custom-designed reusable components (PineTimeButton, PineTimeCard, etc.)
- **Testing**: Pytest (backend), React Testing Library/Jest (frontend), demo mode support

## Setup Instructions

### Backend Setup

1. Clone the repository:

```bash
git clone https://github.com/kpdgayao/pine-time-app.git
cd pine-time-app
```

1. Create a virtual environment:

```bash
python -m venv venv
```

1. Activate the virtual environment:

- Windows: `venv\Scripts\activate`
- Unix/MacOS: `source venv/bin/activate`

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

1. Run the FastAPI backend:

```bash
uvicorn app.main:app --reload
```

### Frontend Setup

#### React Frontend (Recommended)

1. Navigate to the React frontend directory:

```bash
cd pine-time-frontend
```

1. Install dependencies:

```bash
npm install
```

1. Create a `.env` file based on `.env.example` for development:

```bash
cp .env.example .env
```

1. Start the development server:

```bash
npm run dev
```

1. Open [http://localhost:5173](http://localhost:5173) in your browser.

#### Frontend Production Deployment

For production deployment, the frontend uses a dedicated configuration file at `src/config.ts` that contains hardcoded production values:

```typescript
// Base URL for API requests
export const API_BASE_URL = 'https://api.pinetimeapp.com';

// API version prefix - empty because backend already includes /api/v1
export const API_PREFIX = '';

// Default request timeout in milliseconds
export const DEFAULT_TIMEOUT = 10000;

// Extended timeout for paginated endpoints
export const EXTENDED_TIMEOUT = 30000;
```

This approach separates development configuration (via `.env` files) from production settings, eliminating the need for environment variables in the production environment.

#### Streamlit Admin Dashboard (Legacy/Admin)

1. Navigate to the admin_dashboard directory:

```bash
cd ../admin_dashboard
```

1. Run the admin dashboard:

```bash
streamlit run app.py
```

1. Run the user interface with PostgreSQL support:

```bash
streamlit run user_app_postgres.py
```

## Environment Variables

Create a `.env` file with the following variables:

```bash
# Database Configuration
# Local Development
DATABASE_TYPE=postgresql
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=pine_time
POSTGRES_PORT=5432
POSTGRES_SSL_MODE=prefer

# Production (Neon PostgreSQL)
# DATABASE_TYPE=postgresql
# POSTGRES_SERVER=ep-black-sound-a13jwznd-pooler.ap-southeast-1.aws.neon.tech
# POSTGRES_USER=neondb_owner
# POSTGRES_PASSWORD=your_neon_password
# POSTGRES_DB=neondb
# POSTGRES_PORT=5432
# POSTGRES_SSL_MODE=require

# Connection Pooling
POOL_SIZE=5
MAX_OVERFLOW=10
POOL_TIMEOUT=30
POOL_RECYCLE=1800
POOL_PRE_PING=True

# JWT Authentication
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
API_BASE_URL=[http://localhost:8000](http://localhost:8000)

# Demo Mode (set to "true" to enable)
DEMO_MODE=false
```

## Demo Mode

The application includes an enhanced demo mode for testing without backend connection:

1. Set `DEMO_MODE=true` in your `.env` file or run:

```bash
python run_admin_dashboard_demo.py
```

1. Use the demo credentials:

- Username: `demo@pinetimeexperience.com`
- Password: `demo`

## Error Handling and Resilience

The application implements a robust error handling system with multiple layers:

- **API Client Layer**: Centralized error handling for all API requests (see `safe_api_call` and axios interceptors)
- **Token Management**: Secure JWT storage, token refresh logic, and session expiry warnings
- **Connection Utility Layer**: Connection verification with caching and fallback mechanisms
- **User Interface Layer**: Graceful degradation with informative error messages
- **Custom Exceptions**: Specialized exception classes for different error types (APIError, PostgreSQLError)
- **User Points & Badges**: Endpoints and logic for awarding points, redeeming points, managing user badges, and providing detailed statistics, all with admin and user role checks
- **Response Format Handling**: Support for both list and dictionary response formats from API endpoints

## Admin Dashboard Integration

The admin dashboard is fully integrated with the main application, providing a seamless experience:

- **Unified Authentication**: Automatic token sharing between main app and admin dashboard
- **Seamless Navigation**: Single-tab experience with preserved authentication state
- **Role-Based Access**: Only users with admin privileges can access the dashboard
- **Comprehensive Error Handling**: Clear feedback during authentication issues
- **Debugging Tools**: Built-in debugging panels for troubleshooting authentication flows

## AWS Amplify Deployment

The application is configured for deployment on AWS Amplify:

- **Main App**: Deployed at the root path (`/`)
- **Admin Dashboard**: Deployed as a subdirectory (`/admin`)
- **Authentication**: Shared authentication state between both applications
- **Navigation**: Direct links between applications maintain authentication context

## PostgreSQL Integration

The application is optimized for PostgreSQL with:

- Connection pooling with configurable parameters
- Connection verification and testing
- Proper error handling for database constraints
- Sequence management utilities
- Type-safe database operations

## Troubleshooting Database Connectivity

If you encounter database connectivity issues, especially in the deployed environment, check the following:

1. **Environment Variables**: Ensure all PostgreSQL connection parameters are correctly set in `.ebextensions/04_environment.config`:
   - Verify the `POSTGRES_PASSWORD` is correctly set for your Neon database
   - Check that `POSTGRES_SSL_MODE` is set to `require` for Neon PostgreSQL

2. **CORS Configuration**: Make sure your CORS settings include all necessary domains:
   - Include both HTTP and HTTPS versions of your domains
   - Include both www and non-www versions if applicable
   - Include your Elastic Beanstalk domain
   - The application has two CORS configurations that must be synchronized:
     1. Hardcoded `all_origins` list in `app/main.py`
     2. Environment variable `BACKEND_CORS_ORIGINS` in `.ebextensions/04_environment.config`
   - The custom CORS middleware in `app/main.py` merges origins from both sources
   - Check application logs for messages about CORS origins to troubleshoot issues

3. **SSL Configuration**: Ensure HTTPS is properly configured:
   - Add an HTTPS listener (port 443) to your Elastic Beanstalk load balancer
   - Configure HTTP to HTTPS redirection for security
   - Verify your SSL certificate covers both your main domain and api subdomain

4. **Connection Pooling**: Adjust pool settings if you encounter connection issues:
   - Increase `POOL_SIZE` and `MAX_OVERFLOW` for higher traffic
   - Decrease `POOL_RECYCLE` if you encounter stale connections

5. **Logs**: Check the application logs for specific error messages:
   - Database connection errors
   - SSL/TLS handshake failures
   - Authentication failures

## Testing Capabilities

The application includes a comprehensive test suite:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test interactions between components
- **API Tests**: Test API endpoints and error handling
- **Load Tests**: Evaluate performance under load
- **Demo Mode Tests**: Test without backend connection
- **Proxy/CORS Tests**: Ensure frontend-backend connectivity via Vercel proxy (see troubleshooting section)

Run the test suite with:

```bash
python run_comprehensive_tests.py
```

Or run specific test categories:

```bash
python run_tests.py       # Run all tests
python run_demo_tests.py  # Run tests in demo mode
```

---

## Troubleshooting Frontend-Backend Connectivity

### CORS Configuration Issues

- If your backend fails to start with `NameError: name 'all_origins' is not defined`, check the variable declaration order in `app/main.py`:
  - The `all_origins` list must be defined **before** any code that references it
  - The environment variable parsing should occur after the `all_origins` list is defined
  - The CORS middleware should be added last

- If you encounter CORS errors in the browser console:
  - Verify that your domain is included in both the `all_origins` list in `app/main.py` and the `BACKEND_CORS_ORIGINS` environment variable
  - Check the application logs for CORS-related messages
  - Ensure your API requests include the correct credentials and headers

### Proxy Configuration

- If your frontend cannot reach the backend or authentication fails, check your `pine-time-proxy/vercel.json`:
  - The `destination` must match your backend route structure (add or remove `/api` as needed).
  - CORS headers must allow credentials and the Authorization header.
- For authentication issues, ensure your axios client uses the correct token key (`access_token`) and always uses the shared API instance.
- If you deploy to a new domain, add it to your backend's CORS origins (see `BACKEND_CORS_ORIGINS` in your environment variables).
- For more advanced proxy needs, see the sample `api/[...path].js` handler in the documentation or ask for help.

## API Configuration and Path Handling

The Pine Time application uses a specific API configuration pattern to prevent duplicate API prefixes:

- **Backend Configuration**: The FastAPI backend already includes the `/api/v1` prefix in its routes
- **Frontend Configuration**: The frontend configuration in `src/config.ts` sets `API_PREFIX = ''` (empty string)
- **API Path Handling**: The `getApiPath` function in `src/utils/api.ts` handles path normalization
- **Common Issues to Avoid**:
  - Never set `API_PREFIX = '/api/v1'` in the frontend config
  - Don't include `/api/v1` in API request paths in components
  - When adding new API endpoints, follow the existing pattern

## Points Management Utilities

The application includes several command-line utilities for managing the points system:

```bash
# Display current points data
python app/utils/manage_points.py --display

# Reset points data with sample data
python app/utils/manage_points.py --reset

# Clean all points transactions
python app/utils/manage_points.py --clean

# Show points summary by user
python app/utils/manage_points.py --summary
```

These utilities are essential for production maintenance and troubleshooting.

## Contributing

1. Fork the repository

2. Create a feature branch: `git checkout -b feature-name`

3. Commit your changes: `git commit -am 'Add feature'`

4. Push to the branch: `git push origin feature-name`

5. Submit a pull request

## License

MIT
