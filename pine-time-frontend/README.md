# Pine Time App Frontend

## Modern React frontend for Pine Time Experience Baguio

This React-based frontend application powers the Pine Time Experience Baguio platform, connecting locals with local businesses and artisans in Baguio City. The app allows users to discover and register for events, track points and badges, and engage with the Pine Time community.

## Key Features

- **Event Discovery**: Browse and register for upcoming events
- **User Profiles**: View and manage user profiles
- **Gamification**: Track badges, points, and achievements
- **Image Handling**: Robust image loading with fallbacks and proxying
- **API Integration**: Resilient API client with error handling
- **Authentication**: JWT-based auth with token management
- **Theme Support**: Custom theme with light/dark mode

## Environment Setup

The application uses environment variables for development and a configuration file for production:

### Development Environment

Create a `.env` file based on `.env.example`:

```
# API Configuration - for development only
# Production uses the config.ts file with hardcoded values
VITE_API_BASE_URL=http://localhost:8000
```

### Production Configuration

Production settings are managed in `src/config.ts`:

```typescript
// Base URL for API requests
export const API_BASE_URL = 'https://api.pinetimeapp.com';

// API version prefix
export const API_PREFIX = '/api/v1';

// Default request timeout in milliseconds
export const DEFAULT_TIMEOUT = 10000;

// Extended timeout for paginated endpoints
export const EXTENDED_TIMEOUT = 30000;
```

## Development Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:5173](http://localhost:5173) in your browser.

## Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Image Handling System

The application includes a robust image handling system with:

- Automatic fallbacks for missing images
- Event type-specific image placeholders
- CORS-aware image proxying
- Lazy loading and graceful error recovery
- Image caching prevention

Key components:

- `EventImage.tsx`: Specialized component for displaying event images
- `utils/image.ts`: Utilities for image URL handling and proxying

## API Integration

The application uses a centralized API client with:

- Consistent error handling
- Loading state management
- JWT authentication
- Support for both standard and long-timeout endpoints
- Configuration based on environment or production settings

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Components**: Material UI v7
- **API Client**: Axios
- **Routing**: React Router v6
- **State Management**: React Context
- **Authentication**: JWT
- **Styling**: Emotion/styled-components
