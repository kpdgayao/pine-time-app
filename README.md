# Pine Time Experience Baguio

> **Migration Note (April 2025):**
>
> The Pine Time application now features a modern React frontend (Vite + TypeScript) for end users, in addition to the legacy Streamlit admin dashboard. All new user-facing features are being developed in React. See below for updated setup instructions and project structure.

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
- **Admin Dashboard**: Comprehensive tools for managing users, events, and analytics
- **User Interface**: Mobile-friendly design with intuitive navigation
- **Demo Mode**: Test the application without backend connection
- **Enhanced Error Handling**: Robust error handling with graceful degradation
- **API Integration**: Resilient API client with response format handling
- **PostgreSQL Support**: Optimized for PostgreSQL with connection pooling

## Project Structure

```text
pine-time-app/
├── admin_dashboard/       # Streamlit admin dashboard (legacy/admin)
│   ├── pages/             # Dashboard page components
│   ├── utils/             # Utility modules (auth, API, DB, connection)
│   ├── app.py             # Admin dashboard entry point
│   └── user_app_postgres.py # User interface entry point with PostgreSQL support
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
├── pine-time-frontend/    # React frontend (Vite + TypeScript)
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

## Tech Stack

- **Backend**: FastAPI (with all routes under `/api`) and SQLAlchemy ORM
- **Database**: PostgreSQL 17.4 (production), SQLite (development/testing)
- **Frontend**: React (Vite + TypeScript) for users, Streamlit (legacy/admin)
- **Proxy**: Vercel proxy for frontend-backend integration and CORS handling
- **React Frontend**: Uses axios (with JWT auth), react-router-dom, jwt-decode, custom hooks, robust error handling
- **Admin Dashboard**: Streamlit-based admin tools
- **Authentication**: JWT-based auth system with refresh token logic (frontend and backend)
- **Payment System**: Context-based payment management with database integration and step-based payment flow
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

1. Start the development server:

```bash
npm run dev
```

1. Open [http://localhost:5173](http://localhost:5173) in your browser.

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
DATABASE_TYPE=postgresql
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=pine_time
POSTGRES_PORT=5432
POSTGRES_SSL_MODE=prefer

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

## PostgreSQL Integration

The application is optimized for PostgreSQL with:

- Connection pooling with configurable parameters
- Connection verification and testing
- Proper error handling for database constraints
- Sequence management utilities
- Type-safe database operations

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

- If your frontend cannot reach the backend or authentication fails, check your `pine-time-proxy/vercel.json`:
  - The `destination` must match your backend route structure (add or remove `/api` as needed).
  - CORS headers must allow credentials and the Authorization header.
- For authentication issues, ensure your axios client uses the correct token key (`access_token`) and always uses the shared API instance.
- If you deploy to a new domain, add it to your backend's CORS origins (see `BACKEND_CORS_ORIGINS` in your environment variables).
- For more advanced proxy needs, see the sample `api/[...path].js` handler in the documentation or ask for help.

## Contributing

1. Fork the repository

2. Create a feature branch: `git checkout -b feature-name`

3. Commit your changes: `git commit -am 'Add feature'`

4. Push to the branch: `git push origin feature-name`

5. Submit a pull request

## License

MIT
