# Pine Time Admin Dashboard

The Pine Time Admin Dashboard is a React-based admin interface for the Pine Time Event Management System. It allows administrators to manage users, events, badges, points, and access analytics data.

> **Migration Notice:** This React-based admin dashboard replaces the previous Streamlit implementation for improved performance, better user experience, and enhanced maintainability. The old Streamlit files have been archived in the `archive_old_dashboard` directory.

## Features

- **Dashboard Overview**: Key metrics and activity summaries
- **User Management**: View and manage user accounts
- **Event Management**: Create, edit, and monitor events
- **Analytics**: Visualize data with charts and reports
- **Badge & Points Management**: Administer the gamification system

## Tech Stack

- **Frontend**: React 19 with TypeScript
- **UI Library**: Material UI 7
- **State Management**: React Context API
- **Routing**: React Router
- **HTTP Client**: Axios
- **Authentication**: JWT-based authentication
- **Charts**: Recharts for data visualization

## Development Setup

### Prerequisites

- Node.js 18.18.0 or compatible version (an `.nvmrc` file is provided)
- PostgreSQL 17.4
- Pine Time backend API running (default: `http://localhost:8000`)

### Installation

1. Clone the repository (if not already done):

   ```bash
   git clone https://github.com/yourusername/pine-time-app.git
   cd pine-time-app/pine-time-admin
   ```

2. Install dependencies:

   ```bash
   npm install --legacy-peer-deps
   ```

   Note: The `--legacy-peer-deps` flag helps resolve dependency conflicts with newer React versions.

3. Create a `.env` file based on `.env.example`:

   ```bash
   cp .env.example .env
   ```

   Then edit the `.env` file to set your local API URL.

4. Start the development server:

   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:5174`

## API Integration

### API Configuration

The admin dashboard uses a proxy configuration for local development to avoid CORS issues:

- In development mode, API requests are proxied through the Vite development server
- The API base URL is configured in `src/config.ts`
- Authentication tokens are automatically attached to requests via an Axios interceptor

### API Path Structure

The Pine Time backend uses a specific path structure that the admin dashboard respects:

- The backend already includes `/api/v1` in its routes
- Frontend requests should not duplicate this prefix
- Example: `/login/access-token` will be proxied to `/api/v1/login/access-token`

### Authentication

The dashboard uses JWT-based authentication with automatic token refresh:

- JWT tokens are stored securely in localStorage
- Tokens are automatically attached to API requests
- Token expiration is handled with automatic refresh
- Admin-specific role checks are enforced

## Recent Improvements

### Component Structure Fixes

- Fixed component hierarchy in App.tsx to ensure proper context nesting
- Corrected AuthProvider placement to ensure it has access to the router context
- Added missing component imports across various pages

### TypeScript Enhancements

- Added comprehensive interfaces for API responses
- Fixed type errors in utility functions
- Implemented proper typing for Material UI v7 components
- Updated Grid component syntax to match Material UI v7 requirements

### Error Handling

Following Pine Time's error handling guidelines:

- Implemented comprehensive error handling for API requests
- Added fallback mechanisms for unavailable services
- Included user-friendly error messages
- Improved logging for debugging purposes

## Folder Structure

```txt
src/
├── api/          # API clients and services
├── components/   # Reusable UI components
├── contexts/     # React context providers
├── pages/        # Page components organized by feature
├── types/        # TypeScript interfaces and type definitions
├── utils/        # Utility functions and helpers
├── App.tsx       # Main application component
└── main.tsx      # Application entry point
```
- Database operations are wrapped in try/catch blocks
- User-friendly error messages are displayed
- Comprehensive logging is implemented
- Graceful degradation is provided when services are unavailable

## Building for Production

```bash
npm run build
```

This generates optimized production files in the `dist/` directory, ready for deployment to a static hosting service.

## Deployment

The production build is configured to connect to `https://api.pinetimeapp.com` automatically. Deployment can be done to any static hosting service that supports single-page applications (like AWS Amplify, Netlify, or Vercel).

For more information on the Pine Time project architecture, refer to the main project documentation.
