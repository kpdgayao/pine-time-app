# Pine Time Experience Baguio

> **Migration Note (April 2025):**
>
> The Pine Time application now features a modern React frontend (Vite + TypeScript) for end users, in addition to the legacy Streamlit admin dashboard. All new user-facing features are being developed in React. See below for updated setup instructions and project structure.

A web application for Pine Time Experience Baguio, a community that hosts trivia nights, murder mysteries, and game nights in Baguio City. The app connects locals with local businesses and artisans.

## Features

- **User Authentication**: Registration, login/logout with JWT token management
- **Event Management**: Create, discover, and register for events
- **Multi-level Badge System**: Bronze, silver, and gold badges across different categories
- **Points & Rewards**: Track points, view leaderboards, and earn rewards
- **Streak Tracking**: Rewards for consistent weekly attendance
- **Admin Dashboard**: Comprehensive tools for managing users, events, and analytics
- **User Interface**: Mobile-friendly design with intuitive navigation
- **Demo Mode**: Test the application without backend connection
- **Enhanced Error Handling**: Robust error handling with graceful degradation
- **API Integration**: Resilient API client with response format handling
- **PostgreSQL Support**: Optimized for PostgreSQL with connection pooling

## Project Structure

```
pine-time-app/
├── admin_dashboard/       # Streamlit admin dashboard (legacy/admin)
│   ├── pages/             # Dashboard page components
│   ├── utils/             # Utility modules (auth, API, DB, connection)
│   ├── app.py             # Admin dashboard entry point
│   └── user_app_postgres.py # User interface entry point with PostgreSQL support
├── app/                   # FastAPI backend
│   ├── api/               # API endpoints
│   ├── core/              # Core functionality
│   ├── db/                # Database setup
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── main.py            # Backend entry point
├── pine-time-frontend/    # React frontend (Vite + TypeScript)
│   ├── src/               # React source code (components, pages, hooks, types, utils)
│   ├── public/            # Static assets
│   ├── package.json       # React frontend dependencies
│   └── ...
├── tests/                 # Comprehensive test suite
│   ├── api/               # API tests
│   ├── frontend/          # Frontend tests
│   ├── integration/       # Integration tests
│   └── load/              # Load testing tools
├── .env.example           # Example environment variables
└── requirements.txt       # Backend dependencies
```

**Note:** The project now supports both a modern React frontend (for users) and a Streamlit-based admin dashboard. The React frontend is located in `pine-time-frontend/` and is the recommended UI for end users.

## Tech Stack

- **Backend**: FastAPI with SQLAlchemy ORM
- **Database**: PostgreSQL 17.4 (primary), SQLite (development)
- **Frontend**: React (Vite + TypeScript) and Streamlit (legacy/admin)
- **React Frontend**: Modern UI, uses axios, react-router-dom, jwt-decode, and custom hooks
- **Admin Dashboard**: Streamlit-based admin tools
- **Authentication**: JWT-based auth system with token refresh
- **Styling**: Custom CSS with Pine Time green theme (#2E7D32)
- **Testing**: Pytest with demo mode support

## Setup Instructions

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/kpdgayao/pine-time-app.git
   cd pine-time-app
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

6. Run the FastAPI backend:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

#### React Frontend (Recommended)

1. Navigate to the React frontend directory:
   ```bash
   cd pine-time-frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:5173](http://localhost:5173) in your browser.

#### Streamlit Admin Dashboard (Legacy/Admin)

1. Navigate to the admin_dashboard directory:
   ```bash
   cd ../admin_dashboard
   ```
2. Run the admin dashboard:
   ```bash
   streamlit run app.py
   ```
3. Run the user interface with PostgreSQL support:
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
API_BASE_URL=http://localhost:8000

# Demo Mode (set to "true" to enable)
DEMO_MODE=false
```

## Demo Mode

The application includes an enhanced demo mode for testing without backend connection:

1. Set `DEMO_MODE=true` in your `.env` file or run:
   ```bash
   python run_admin_dashboard_demo.py
   ```

2. Use the demo credentials:
   - Username: demo@pinetimeexperience.com
   - Password: demo

## Error Handling and Resilience

The application implements a robust error handling system with multiple layers:

- **API Client Layer**: Enhanced error handling with specific error messages for different status codes
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

Run the test suite with:
```bash
python run_comprehensive_tests.py
```

Or run specific test categories:
```bash
python run_demo_tests.py  # Run tests in demo mode
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

MIT